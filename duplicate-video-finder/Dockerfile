ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache \
    python3 \
    py3-pip \
    nginx

# Copy root filesystem
COPY rootfs /

# Setup app
COPY app /app

# Make scripts executable
RUN chmod a+x /etc/services.d/*/run \
    && chmod a+x /app/run.py

# Install Python requirements
WORKDIR /app
RUN pip3 install -r requirements.txt

CMD ["/init"]
