#!/bin/bash
# EC2 User Data or Setup script

# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io

# Build and Run the Throttler
cd /app
sudo docker build -t cpu-throttler .
sudo docker run -d --name throttler --privileged cpu-throttler

echo "Throttler started. Use 'docker exec throttler sh -c \"echo 20 > /tmp/global_throttle\"' to add 20% load globally."
