#!/bin/bash
# Script de despliegue rápido para el Worker

echo "Corrigiendo propiedad del repositorio..."
sudo chown -R ec2-user:ec2-user /home/ec2-user/LoadBalancerASG
git config --global --add safe.directory /home/ec2-user/LoadBalancerASG

echo "Actualizando código..."
git pull origin main

echo "Verificando instalación de Docker y permisos..."
# Asegurar que docker esté iniciado
sudo systemctl start docker
sudo systemctl enable docker
# Asegurar permisos del socket
sudo chmod 666 /var/run/docker.sock

echo "Verificando instalación de Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "Instalando Docker Compose manualmente..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

echo "Preparando directorios y archivos de volumen..."
sudo mkdir -p /tmp/throttler
# Si existe como directorio por error, lo borramos
if [ -d "/tmp/throttler/global_throttle" ]; then
    sudo rm -rf /tmp/throttler/global_throttle
fi
# Crear el archivo si no existe
if [ ! -f "/tmp/throttler/global_throttle" ]; then
    echo "0" | sudo tee /tmp/throttler/global_throttle > /dev/null
fi
sudo chmod -R 777 /tmp/throttler

echo "Construyendo imágenes manualmente para evitar errores de buildx..."
docker build -t instance-app ./App
docker build -t instance-monitor ./MonitorC

echo "Iniciando contenedores..."
docker-compose up -d --no-build

echo "Verificando estado..."
docker ps
