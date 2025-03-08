ARG BUILD_FROM
FROM $BUILD_FROM

# Install required packages
RUN apk add --no-cache \
    python3 \
    py3-pip

# Copy root filesystem
COPY rootfs /

# Setup app directory
WORKDIR /usr/src/app

# Copy app files
COPY app /usr/src/app/

# Install Python requirements
RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt

# Set executable
RUN chmod a+x /etc/services.d/duplicate-video-finder/run

CMD ["/init"]
