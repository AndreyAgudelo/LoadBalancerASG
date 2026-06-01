FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/ ./proto/
COPY src/ ./src/

# Generate gRPC code
RUN python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/monitor.proto

ENV PYTHONPATH=/app/src
ENV MONITOR_SERVER_HOST=monitor-server
ENV MONITOR_SERVER_PORT=50051
ENV REPORT_INTERVAL=10

CMD ["python", "src/client.py"]
