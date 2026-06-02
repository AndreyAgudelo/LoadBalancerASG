import os
import sys
import grpc
import time
from concurrent import futures
import logging
import multiprocessing

# Shared state using multiprocessing Manager
manager = multiprocessing.Manager()
shared_clients = manager.dict()

class LoadMonitorServicer(monitor_pb2_grpc.LoadMonitorServicer):
    def __init__(self, clients_dict):
        self.clients = clients_dict

    def RegisterClient(self, request, context):
        peer_addr = context.peer()
        client_ip = request.ip_address or peer_addr
        client_id = request.client_id or f"auto-{client_ip}"
        
        logging.info(f"Registering client: {client_id} (Source: {peer_addr})")
        self.clients[client_id] = {"ip": client_ip, "last_load": 0.0, "peer": peer_addr}
        return monitor_pb2.RegisterResponse(success=True, message=f"Registered as {client_id}")

    def ReportLoad(self, request, context):
        if request.client_id in self.clients:
            data = self.clients[request.client_id]
            data["last_load"] = request.load_value
            data["last_seen"] = time.time() # Timestamp para limpieza
            self.clients[request.client_id] = data
            return monitor_pb2.LoadResponse(acknowledged=True)
        return monitor_pb2.LoadResponse(acknowledged=False)

def serve(clients_dict):
    port = os.getenv("SERVER_PORT", "50051")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    monitor_pb2_grpc.add_LoadMonitorServicer_to_server(LoadMonitorServicer(clients_dict), server)
    server.add_insecure_port(f'[::]:{port}')
    logging.basicConfig(level=logging.INFO)
    logging.info(f"MonitorS starting on port {port}...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
