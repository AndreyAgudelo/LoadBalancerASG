#!/bin/bash
# Script de despliegue rápido para el Worker

echo "Actualizando código..."
git pull origin main

echo "Construyendo imágenes manualmente para evitar errores de buildx..."
docker build -t instance-app ./App
docker build -t instance-monitor ./MonitorC

echo "Iniciando contenedores..."
docker-compose up -d --no-build

echo "Verificando estado..."
docker ps
