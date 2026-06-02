import os
import sys
import grpc
import time
import logging
import socket
import psutil

import monitor_pb2
import monitor_pb2_grpc

class MonitorClient:
    def __init__(self, server_addr, client_id=None):
        self.server_addr = server_addr
        self.client_id = client_id or socket.gethostname()
        self.channel = grpc.insecure_channel(server_addr)
        self.stub = monitor_pb2_grpc.LoadMonitorStub(self.channel)

    def register(self):
        try:
            response = self.stub.RegisterClient(monitor_pb2.RegisterRequest(
                client_id=self.client_id,
                ip_address=socket.gethostbyname(socket.gethostname())
            ))
            return response.success
        except Exception as e:
            logging.error(f"Registration failed: {e}")
            return False

    def send_load(self, load_value):
        try:
            response = self.stub.ReportLoad(monitor_pb2.LoadReport(
                client_id=self.client_id,
                load_value=load_value
            ))
            return response.acknowledged
        except Exception as e:
            logging.error(f"Load report failed: {e}")
            return False

def get_actual_cpu_load():
    return psutil.cpu_percent(interval=1.0) / 100.0

def main():
    server_host = os.getenv("MONITOR_SERVER_HOST", "localhost")
    server_port = os.getenv("MONITOR_SERVER_PORT", "50051")
    client_id = os.getenv("CLIENT_ID") 
    server_addr = f"{server_host}:{server_port}"
    
    logging.basicConfig(level=logging.INFO)
    client = MonitorClient(server_addr, client_id=client_id)

    registered = False
    while not registered:
        logging.info("Attempting to register...")
        registered = client.register()
        if not registered:
            time.sleep(5)

    logging.info("Starting load reporting loop...")
    while True:
        current_load = get_actual_cpu_load()
        success = client.send_load(current_load)
        if success:
            logging.info(f"Sent actual CPU load: {current_load:.2f}")
        
        time.sleep(int(os.getenv("REPORT_INTERVAL", "5")))

if __name__ == "__main__":
    main()
