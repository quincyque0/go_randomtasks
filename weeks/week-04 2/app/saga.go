package main

import (
	"fmt"
	"log"
	"time"
)

type OrderStatus string

const (
	OrderStatusNew       OrderStatus = "NEW"
	OrderStatusPaid      OrderStatus = "PAID"
	OrderStatusDone      OrderStatus = "DONE"
	OrderStatusCancelled OrderStatus = "CANCELLED"
)

type SagaStep string

const (
	SagaStepCreateOrder    SagaStep = "create_order"
	SagaStepReserveProduct SagaStep = "reserve_product"
	SagaStepProcessPayment SagaStep = "process_payment"
)

type Logger interface {
	Info(format string, v ...interface{})
	Error(format string, v ...interface{})
	Warn(format string, v ...interface{})
}

type DefaultLogger struct{}

func (l DefaultLogger) Info(format string, v ...interface{}) {
	log.Printf("[INFO] "+format, v...)
}

func (l DefaultLogger) Error(format string, v ...interface{}) {
	log.Printf("[ERROR] "+format, v...)
}

func (l DefaultLogger) Warn(format string, v ...interface{}) {
	log.Printf("[WARN] "+format, v...)
}

type OrderSaga struct {
	orderID             string
	productID           string
	quantity            int
	amount              float64
	status              OrderStatus
	currentStep         SagaStep
	compensationActions []func() error
	retryCount          int
	retryDelay          time.Duration
	logger              Logger
}

func NewOrderSaga(orderID, productID string, quantity int, amount float64) *OrderSaga {
	return &OrderSaga{
		orderID:             orderID,
		productID:           productID,
		quantity:            quantity,
		amount:              amount,
		status:              OrderStatusNew,
		currentStep:         SagaStepCreateOrder,
		compensationActions: make([]func() error, 0),
		retryCount:          3,
		retryDelay:          time.Second,
		logger:              DefaultLogger{},
	}
}

func next_state(state string, event string) string {
	cur_state := map[string]map[string]string{
		"NEW": {
			"PAY_OK":   "PAID",
			"PAY_FAIL": "CANCELLED",
			"CANCEL":   "CANCELLED",
		},
		"PAID": {
			"COMPLETE": "DONE",
			"CANCEL":   "CANCELLED",
		},
		"DONE":      {},
		"CANCELLED": {},
	}

	if stateEvents, ok := cur_state[state]; ok {
		if nextState, ok := stateEvents[event]; ok {
			return nextState
		}
	}
	return state
}

func execute(s *OrderSaga) bool {
	log.Println("Начало выполнения саги для заказа")
	if err := s.create_order(); err != nil {
		s.logger.Error("Не удалось зарезервировать товар: %v", err)
		s.compensate()
		return false
	}
	s.compensationActions = append(s.compensationActions, s.cancelOrder)

	if err := s.reserveProduct(); err != nil {
		s.logger.Error("Ну удалось зарезервировать товар: %v", err)
		s.compensate()
		return false
	}
	s.compensationActions = append(s.compensationActions, s.releaseProduct)

	if err := s.processPayment(); err != nil {
		s.logger.Error("Не удалось списать деньги: %v", err)
		s.compensate()
		return false
	}
	s.compensationActions = append(s.compensationActions, s.refundPayment)

	s.status = OrderStatusPaid
	s.logger.Info("Заказ %s успешно оплачен", s.orderID)
	return true
}

func (s *OrderSaga) executeWithRetry(action func() error) {
	for attempt := 0; attempt < s.retryCount; attempt++ {
		err := action()
		if err == nil {
			s.logger.Info("Компенсационное действие выполнено успешно")
			return
		}

		s.logger.Warn("Попытка %d не удалась: %v", attempt+1, err)
		if attempt < s.retryCount-1 {
			time.Sleep(s.retryDelay)
		} else {
			s.logger.Error("Все попытки исчерпаны для компенсационного действия")
			s.logger.Info("Обратитесь в паддержку!")
		}
	}
}
func (s *OrderSaga) cancelOrder() error {
	s.logger.Info("Отмена заказа %s", s.orderID)
	return nil
}
func (s *OrderSaga) reserveProduct() error {
	s.logger.Info("Резервирование товара %s в количестве %d", s.productID, s.quantity)
	s.currentStep = SagaStepReserveProduct
	return nil
}
func (s *OrderSaga) processPayment() error {
	s.logger.Info("Списание суммы %.2f для заказа %s", s.amount, s.orderID)
	s.currentStep = SagaStepProcessPayment
	if s.amount > 10000 {
		return fmt.Errorf("сумма слишком большая (%.2f), платеж отклонен", s.amount)
	}
	return nil
}
func (s *OrderSaga) SetRetryConfig(count int, delay time.Duration) {
	s.retryCount = count
	s.retryDelay = delay
}
func (s *OrderSaga) create_order() error {
	s.logger.Info("Создание заказа: %s", s.orderID)
	s.currentStep = SagaStepCreateOrder
	return nil
}
func (s *OrderSaga) compensate() {
	s.logger.Info("Возврат средств: %s", s.amount)
	s.currentStep = SagaStep(OrderStatusCancelled)
	for i := len(s.compensationActions) - 1; i >= 0; i-- {
		s.executeWithRetry(s.compensationActions[i])
	}
}
func (s *OrderSaga) releaseProduct() error {
	s.logger.Info("Возврат товара %s на склад (количество: %d)", s.productID, s.quantity)
	return nil
}
func (s *OrderSaga) refundPayment() error {
	s.logger.Info("Возврат средств %.2f для заказа %s", s.amount, s.orderID)
	return nil
}
func (s *OrderSaga) GetStatus() OrderStatus {
	return s.status
}

func (s OrderStatus) String() string {
	return string(s)
}

func (s SagaStep) String() string {
	return string(s)
}
func main() {

	log.SetFlags(log.Ldate | log.Ltime | log.Lmicroseconds)

	saga1 := NewOrderSaga("order-001", "product-123", 2, 5000)
	result1 := execute(saga1)
	fmt.Printf("Результат: %v, Статус: %s\n\n", result1, saga1.GetStatus())

	saga2 := NewOrderSaga("order-002", "product-456", 1, 15000)
	result2 := execute(saga2)
	fmt.Printf("Результат: %v, Статус: %s\n", result2, saga2.GetStatus())
}
