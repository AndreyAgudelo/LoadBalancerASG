FROM amazonlinux:2023

RUN dnf update -y && dnf install -y \
    stress-ng \
    bc \
    procps-ng \
    coreutils \
    sed \
    && dnf clean all

WORKDIR /app
COPY throttle.sh .
RUN chmod +x throttle.sh

# Asegurar que el archivo de throttle global exista con permisos de escritura
RUN touch /tmp/global_throttle && chmod 666 /tmp/global_throttle

ENTRYPOINT ["/bin/bash", "./throttle.sh"]
