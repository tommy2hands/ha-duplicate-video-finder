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

# Create required directories
RUN mkdir -p /app /app/static /app/templates

# Install Python dependencies with specific versions
RUN pip3 install --no-cache-dir \
    fastapi==0.95.1 \
    uvicorn==0.22.0 \
    jinja2==3.1.2 \
    pydantic==1.10.7 \
    python-multipart==0.0.6

# Copy application files
COPY app/run.py /app/
COPY app/static /app/static/
COPY app/templates /app/templates/

# Copy root filesystem
COPY rootfs /

# Set working directory
WORKDIR /app

# Fix permissions
RUN chmod a+x /etc/services.d/*/run
RUN chmod a+x /app/run.py

CMD ["/init"]
