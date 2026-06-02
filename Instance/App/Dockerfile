FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    stress-ng \
    bc \
    procps \
    coreutils \
    sed \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY throttle.sh .
RUN chmod +x throttle.sh

# Asegurar que el archivo de throttle global exista con permisos de escritura
RUN touch /tmp/global_throttle && chmod 666 /tmp/global_throttle

ENTRYPOINT ["/bin/bash", "./throttle.sh"]
