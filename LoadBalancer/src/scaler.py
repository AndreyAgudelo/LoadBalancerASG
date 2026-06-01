import os
import time
import logging
import boto3
from botocore.exceptions import ClientError

class AutoScaler:
    def __init__(self, shared_clients):
        self.clients = shared_clients
        self.ec2 = boto3.client('ec2', region_name=os.getenv("AWS_REGION", "us-east-1"))
        self.launch_template_id = os.getenv("LAUNCH_TEMPLATE_ID")
        self.upper_threshold = float(os.getenv("UPPER_THRESHOLD", "0.8"))
        self.lower_threshold = float(os.getenv("LOWER_THRESHOLD", "0.2"))
        self.min_instances = int(os.getenv("MIN_INSTANCES", "1"))
        self.max_instances = int(os.getenv("MAX_INSTANCES", "10"))
        self.check_interval = int(os.getenv("CHECK_INTERVAL", "30"))

    def get_average_load(self):
        now = time.time()
        timeout = 25 # Segundos antes de considerar al cliente como muerto
        
        # Limpieza de zombies y filtrado de reportes frescos
        active_loads = []
        dead_clients = []
        
        for cid, data in self.clients.items():
            if now - data.get("last_seen", 0) > timeout:
                dead_clients.append(cid)
            else:
                active_loads.append(data["last_load"])
        
        # Eliminar de la memoria compartida
        for cid in dead_clients:
            logging.info(f"Removing dead client: {cid}")
            del self.clients[cid]
            
        if not active_loads:
            return 0.0
        return sum(active_loads) / len(active_loads)

    def scale_up(self):
        logging.info("Average load > 80%. Scaling up...")
        try:
            self.ec2.run_instances(
                LaunchTemplate={'LaunchTemplateId': self.launch_template_id},
                MinCount=1,
                MaxCount=1
            )
            logging.info("New instance launched successfully.")
        except ClientError as e:
            logging.error(f"Failed to scale up: {e}")

    def scale_down(self):
        logging.info("Average load < 20%. Scaling down...")
        # Lógica para terminar la instancia más joven o una específica
        # Por simplicidad, buscamos instancias con el tag de nuestro sistema
        try:
            response = self.ec2.describe_instances(
                Filters=[
                    {'Name': 'instance-state-name', 'Values': ['running']},
                    {'Name': 'tag:Role', 'Values': ['Worker']}
                ]
            )
            instances = [i for r in response['Reservations'] for i in r['Instances']]
            if len(instances) > self.min_instances:
                target_id = instances[0]['InstanceId']
                self.ec2.terminate_instances(InstanceIds=[target_id])
                logging.info(f"Instance {target_id} terminated.")
        except ClientError as e:
            logging.error(f"Failed to scale down: {e}")

    def run(self):
        logging.info("ControllerASG started.")
        while True:
            avg_load = self.get_average_load()
            num_instances = len(self.clients)
            logging.info(f"Status: Avg Load: {avg_load:.2f}, Instances: {num_instances}")

            if avg_load > self.upper_threshold and num_instances < self.max_instances:
                self.scale_up()
            elif avg_load < self.lower_threshold and num_instances > self.min_instances:
                self.scale_down()

            time.sleep(30) # Intervalo de chequeo
