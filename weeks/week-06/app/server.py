from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
import uvicorn
from datetime import datetime
import json

app = FastAPI(title="GraphQL Test Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GraphQLRequest(BaseModel):
    query: str
    variables: Optional[Dict[str, Any]] = None

class Shipment(BaseModel):
    id: int
    tracking: str
    status: str
    created_at: datetime

shipments_db = [
    Shipment(
        id=1, 
        tracking="TRK123456", 
        status="CREATED", 
        created_at=datetime.now()
    ),
    Shipment(
        id=2, 
        tracking="TRK789012", 
        status="IN_TRANSIT", 
        created_at=datetime.now()
    ),
    Shipment(
        id=3, 
        tracking="TRK345678", 
        status="DELIVERED", 
        created_at=datetime.now()
    ),
]

def parse_graphql_query(query: str) -> dict:
    result = {
        "operation": "query",
        "fields": []
    }
    
    if "mutation" in query.lower():
        result["operation"] = "mutation"
    
    if "{" in query and "}" in query:
        fields_part = query.split("{", 1)[1].rsplit("}", 1)[0]
        if "(" in fields_part:
            fields_part = fields_part.split(")", 1)[1] if ")" in fields_part else fields_part

        for field in fields_part.split():
            field = field.strip()
            if field and field not in ["{", "}", "shipments", "createShipment"]:
                result["fields"].append(field)
    
    return result

@app.post("/graphql")
async def graphql_endpoint(request: GraphQLRequest):
    """GraphQL endpoint"""
    print(f"Received GraphQL request: {request.query}")
    print(f"Variables: {request.variables}")
    
    parsed = parse_graphql_query(request.query)

    if "shipments" in request.query.lower() and parsed["operation"] == "query":

        limit = 10
        if request.variables and "limit" in request.variables:
            limit = request.variables["limit"]
        
        shipments_data = []
        for shipment in shipments_db[:limit]:
            shipment_dict = {
                "id": shipment.id,
                "tracking": shipment.tracking,
                "status": shipment.status,
                "createdAt": shipment.created_at.isoformat()
            }
            if parsed["fields"]:
                shipment_dict = {k: v for k, v in shipment_dict.items() 
                               if k in parsed["fields"]}
            shipments_data.append(shipment_dict)
        
        return {"data": {"shipments": shipments_data}}
    
    elif "createShipment" in request.query.lower() and parsed["operation"] == "mutation":
        input_data = {}
        if request.variables and "input" in request.variables:
            input_data = request.variables["input"]

        new_id = len(shipments_db) + 1
        new_shipment = Shipment(
            id=new_id,
            tracking=input_data.get("tracking", f"TRK{new_id:06d}"),
            status=input_data.get("status", "CREATED"),
            created_at=datetime.now()
        )
        shipments_db.append(new_shipment)
        
        shipment_dict = {
            "id": new_shipment.id,
            "tracking": new_shipment.tracking,
            "status": new_shipment.status,
            "createdAt": new_shipment.created_at.isoformat()
        }
        
        if parsed["fields"]:
            shipment_dict = {k: v for k, v in shipment_dict.items() 
                           if k in parsed["fields"]}
        
        return {"data": {"createShipment": shipment_dict}}
    
    else:
        return {
            "errors": [{
                "message": f"Unsupported operation or query",
                "locations": [{"line": 1, "column": 1}]
            }]
        }

@app.get("/")
async def root():
    return {
        "message": "GraphQL Test Server",
        "endpoints": {
            "graphql": "/graphql (POST)",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)