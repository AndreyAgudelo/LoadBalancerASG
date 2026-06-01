import multiprocessing
import os
import sys
import logging

# Add paths for discovery
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import server
from scaler import AutoScaler

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Shared memory dictionary
    manager = multiprocessing.Manager()
    shared_clients = manager.dict()

    # Create processes
    # 1. MonitorS Server
    p_server = multiprocessing.Process(target=server.serve, args=(shared_clients,))
    
    # 2. ControllerASG Scaler
    scaler = AutoScaler(shared_clients)
    p_scaler = multiprocessing.Process(target=scaler.run)

    # Start both
    p_server.start()
    p_scaler.start()

    try:
        p_server.join()
        p_scaler.join()
    except KeyboardInterrupt:
        p_server.terminate()
        p_scaler.terminate()
