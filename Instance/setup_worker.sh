#!/bin/bash
# CLOUD-INIT para las instancias Worker de EC2
# Reemplazar <LB_PRIVATE_IP> con la IP privada del LoadBalancer

LB_IP="<LB_PRIVATE_IP>"

# 1. Actualizar e instalar dependencias
dnf update -y
dnf install -y docker git
systemctl start docker
systemctl enable docker

# 2. Descargar código y preparar entorno
cd /home/ec2-user
# Suponiendo que el código se descarga de un S3 o se clona de un repo
# git clone ... o aws s3 cp ...
# mkdir -p Instance

# 3. Configurar .env dinámicamente
cat <<EOF > /home/ec2-user/Instance/MonitorC/.env
MONITOR_SERVER_HOST=$LB_IP
MONITOR_SERVER_PORT=50051
REPORT_INTERVAL=5
LOG_LEVEL=INFO
EOF

# 4. Iniciar contenedores
cd /home/ec2-user/Instance
docker compose up -d --build
