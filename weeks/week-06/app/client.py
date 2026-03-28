import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

PROJECT_CODE = "shipments-s22"
GRAPHQL_ENDPOINT = "http://localhost:8080/graphql" 

def build_payload(query: str, variables: dict) -> dict:
    return {
        "query": query,
        "variables": variables
    }

def execute_graphql(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if variables is None:
        variables = {}
    
    payload = build_payload(query, variables)
    
    print(f"Отправка запроса на {GRAPHQL_ENDPOINT}")
    print(f"Полезная нагрузка: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"Статус ответа: {response.status_code}")

        result = response.json()

        if "errors" in result:
            print("\nОшибки GraphQL:")
            for error in result["errors"]:
                print(f"{error.get('message', 'Неизвестная ошибка')}")
                if "locations" in error:
                    print(f"    на строке {error['locations'][0].get('line', '?')}")
        
        if "data" in result:
            print("\nДанные GraphQL:")
            print(json.dumps(result["data"], indent=2, ensure_ascii=False))
        
        return result
        
    except requests.exceptions.ConnectionError:
        print(f"Ошибка: Не удается подключиться к {GRAPHQL_ENDPOINT}")
        print("   Убедитесь, что сервер запущен (python app/server.py)")
        return {"errors": [{"message": "Ошибка подключения"}]}
    except Exception as e:
        print(f"Ошибка: {e}")
        return {"errors": [{"message": str(e)}]}

def query_shipments(limit: int = 10):
    query = """
    query GetShipments($limit: Int) {
        shipments(limit: $limit) {
            id
            tracking
            status
            createdAt
        }
    }
    """
    
    variables = {
        "limit": limit
    }
    print("ЗАПРОС: Получить посылки")
    return execute_graphql(query, variables)

def create_shipment(tracking: Optional[str] = None, status: str = "CREATED"):
    query = """
    mutation CreateShipment($input: CreateShipmentInput!) {
        createShipment(input: $input) {
            id
            tracking
            status
            createdAt
        }
    }
    """
    
    if tracking is None:
        tracking = f"TRK{datetime.now().strftime('%H%M%S')}"
    
    variables = {
        "input": {
            "tracking": tracking,
            "status": status
        }
    }
    
    print("МУТАЦИЯ: Создать посылку")
    return execute_graphql(query, variables)

def query_shipments_custom_fields(fields: list):
    fields_str = "\n            ".join(fields)
    query = f"""
    query GetShipments {{
        shipments {{
            {fields_str}
        }}
    }}
    """
    
    print(f"ЗАПРОС: Получить посылки (поля: {', '.join(fields)})")
    return execute_graphql(query)

def test_error_handling():    
    query = """
    query GetShipments {
        nonExistentField {
            id
        }
    }
    """
    print("ТЕСТ: Обработка ошибок")
    return execute_graphql(query)

def main():
    print(f"\nGraphQL Клиент для {PROJECT_CODE}")
    print(f"Сервер: {GRAPHQL_ENDPOINT}")
    
    try:
        requests.get("http://localhost:8080/health", timeout=2)
        print("Сервер доступен")
    except:
        print("Запустите: python app/server.py")
    
    query_shipments(limit=2)
    create_shipment()
    query_shipments_custom_fields(["id", "tracking"]) 
    query_shipments(limit=100)

if __name__ == "__main__":
    main()