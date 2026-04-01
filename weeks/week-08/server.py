import asyncio
import time
from concurrent import futures
import grpc

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protos import items_pb2, items_pb2_grpc

class ItemsService(items_pb2_grpc.ItemsServiceServicer):
    
    def GetItem(self, request, context):
        return items_pb2.Item(
            id=request.id,
            name="Test Item",
            sku="TEST-123",
            created_at=int(time.time())
        )
    
    def CreateItem(self, request, context):
        return items_pb2.Item(
            id="new-123",
            name=request.name,
            sku=request.sku,
            created_at=int(time.time())
        )
    
    def ListItems(self, request, context):
        items = []
        for i in range(10):
            items.append(items_pb2.Item(
                id=f"item-{i}",
                name=f"Item {i}",
                sku=f"SKU-{i}",
                created_at=int(time.time())
            ))
        return items_pb2.ListItemsResponse(items=items)
    
    def SubscribeItems(self, request, context):
        for i in range(5):
            yield items_pb2.ItemUpdate(
                item_id=request.item_ids[0] if request.item_ids else "all",
                field="name",
                old_value=f"old-{i}",
                new_value=f"new-{i}",
                timestamp=int(time.time())
            )
            time.sleep(0.5)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    items_pb2_grpc.add_ItemsServiceServicer_to_server(ItemsService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()