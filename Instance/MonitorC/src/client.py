import os
import sys
import grpc
import time
import logging
import socket
import psutil

# ... (imports and class remain same)

    def send_load(self, load_value):
        # ... (method remains same)

def get_actual_cpu_load():
    # Obtiene el uso real de CPU en el último segundo
    # Retorna valor entre 0.0 y 1.0
    return psutil.cpu_percent(interval=1.0) / 100.0

def main():
    server_host = os.getenv("MONITOR_SERVER_HOST", "localhost")
    server_port = os.getenv("MONITOR_SERVER_PORT", "50051")
    client_id = os.getenv("CLIENT_ID") 
    server_addr = f"{server_host}:{server_port}"
    
    logging.basicConfig(level=logging.INFO)
    client = MonitorClient(server_addr, client_id=client_id)

    # Auto-registration loop
    registered = False
    while not registered:
        logging.info("Attempting to register...")
        registered = client.register()
        if not registered:
            time.sleep(5)

    # Reporting loop
    logging.info("Starting load reporting loop...")
    while True:
        # LEER CARGA REAL DE CPU
        current_load = get_actual_cpu_load()
        
        success = client.send_load(current_load)
        if success:
            logging.info(f"Sent actual CPU load: {current_load:.2f}")
        
        time.sleep(int(os.getenv("REPORT_INTERVAL", "5")))

if __name__ == "__main__":
    main()
