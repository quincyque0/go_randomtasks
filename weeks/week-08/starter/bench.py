import time
import requests
import grpc
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protos import items_pb2, items_pb2_grpc

def run_rest_bench():
    print("\n" + "="*50)
    print("REST Benchmark")
    print("="*50)
    
    start = time.time()
    for i in range(1000):
        try:
            response = requests.get("http://localhost:80/api/items", timeout=5)
            if response.status_code != 200:
                print(f"REST {i} failed: {response.status_code}")
        except Exception as e:
            print(f"REST {i} error: {e}")
    end = time.time()
    rest_time = end - start
    
    print(f"REST 1000 requests: {rest_time:.4f} sec")
    print(f"Avg: {(rest_time/1000)*1000:.4f} ms")
    return rest_time

def run_grpc_bench():
    print("\n" + "="*50)
    print("gRPC Benchmark")
    print("="*50)
    
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = items_pb2_grpc.ItemsServiceStub(channel)
        
        start = time.time()
        for i in range(1000):
            try:
                response = stub.ListItems(items_pb2.ListItemsRequest(page_size=10))
            except grpc.RpcError as e:
                print(f"gRPC {i} error: {e}")
        end = time.time()
        grpc_time = end - start
        
        print(f"gRPC 1000 requests: {grpc_time:.4f} sec")
        print(f"Avg: {(grpc_time/1000)*1000:.4f} ms")
        return grpc_time

def test_streaming():
    print("\n" + "="*50)
    print("Testing Streaming")
    print("="*50)
    
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = items_pb2_grpc.ItemsServiceStub(channel)
        request = items_pb2.SubscribeItemsRequest(item_ids=["1"])
        
        count = 0
        for update in stub.SubscribeItems(request):
            count += 1
            print(f"Update {count}: {update.item_id} - {update.field}")
            if count >= 5:
                break
        
        return count > 0

if __name__ == "__main__":
    print("gRPC vs REST Benchmark")
    try:
        requests.get("http://localhost:80/api/items", timeout=2)
        print("REST: OK")
    except Exception as e:
        print(f"REST not available: {e}")
        sys.exit(1)
    
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = items_pb2_grpc.ItemsServiceStub(channel)
            stub.ListItems(items_pb2.ListItemsRequest())
        print("gRPC: OK")
    except Exception as e:
        print(f"gRPC not available: {e}")
        sys.exit(1)
    
    rest_time = run_rest_bench()
    grpc_time = run_grpc_bench()
    
    print("\n" + "="*50)
    print("RESULTS")
    print("="*50)
    print(f"REST: {rest_time:.4f} sec")
    print(f"gRPC: {grpc_time:.4f} sec")
    
    if grpc_time < rest_time:
        print(f"gRPC faster by {((rest_time - grpc_time)/rest_time)*100:.1f}%")
    
    if test_streaming():
        print("\nStreaming: OK")