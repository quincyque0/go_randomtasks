import grpc
from concurrent import futures
import time
import uuid
from datetime import datetime
from typing import Dict, List

import service_pb2
import service_pb2_grpc

class TicketsService(service_pb2_grpc.TicketsServiceServicer):
    
    def __init__(self):
        self.tickets: Dict[str, service_pb2.Ticket] = {}
        self.counter = 1
    
    def GetTicket(self, request, context):
        ticket_id = request.id
        
        if ticket_id not in self.tickets:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Ticket with id {ticket_id} not found")
            return service_pb2.Ticket()
        
        return self.tickets[ticket_id]
    
    def CreateTicket(self, request, context):
        ticket_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        ticket = service_pb2.Ticket(
            id=ticket_id,
            title=request.title,
            description=request.description,
            status=request.status if request.status else "new",
            created_at=current_time,
            updated_at=current_time
        )
        
        self.tickets[ticket_id] = ticket
        return ticket
    
    def UpdateTicketStatus(self, request, context):
        ticket_id = request.id
        
        if ticket_id not in self.tickets:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Ticket with id {ticket_id} not found")
            return service_pb2.Ticket()
        
        ticket = self.tickets[ticket_id]
        ticket.status = request.status
        ticket.updated_at = datetime.now().isoformat()
        
        self.tickets[ticket_id] = ticket
        return ticket
    
    def ListTickets(self, request, context):
        all_tickets = list(self.tickets.values())
        total_count = len(all_tickets)
        
        page_size = request.page_size if request.page_size > 0 else 10
        page_number = request.page_number if request.page_number > 0 else 1
        
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        
        if start_index >= total_count:
            paginated_tickets = []
        else:
            paginated_tickets = all_tickets[start_index:end_index]
        
        return service_pb2.ListTicketsResponse(
            tickets=paginated_tickets,
            total_count=total_count
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    service_pb2_grpc.add_TicketsServiceServicer_to_server(
        TicketsService(), 
        server
    )
    
    port = 8224
    server.add_insecure_port(f'[::]:{port}')
    
    server.start()
    print(f"gRPC сервер запущен на порту {port}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
        server.stop(0)

if __name__ == '__main__':
    serve()