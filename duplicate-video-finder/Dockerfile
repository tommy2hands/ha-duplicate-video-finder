ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.16
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install requirements for add-on
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-pillow \
    py3-requests \
    nginx

WORKDIR /app

# Copy root filesystem
COPY rootfs /

# Copy Python app
COPY app /app

# Install Python requirements
RUN pip3 install -r /app/requirements.txt

# Make scripts executable
RUN chmod a+x /etc/services.d/*/run
RUN chmod a+x /app/run.py

CMD ["/init"]
