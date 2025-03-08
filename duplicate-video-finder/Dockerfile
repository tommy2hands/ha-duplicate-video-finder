ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.16
FROM ${BUILD_FROM}

# Install required packages
RUN apk add --no-cache \
    python3 \
    py3-pip

# Copy root filesystem
COPY rootfs /

# Setup application
WORKDIR /usr/src/app

# Copy app files
COPY app /usr/src/app/

# Make scripts executable
RUN chmod a+x /etc/services.d/duplicate-video-finder/run \
    && chmod a+x /usr/src/app/run.py

# Install Python requirements
RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt
