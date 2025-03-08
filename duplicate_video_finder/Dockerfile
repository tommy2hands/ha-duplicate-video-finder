ARG BUILD_FROM
FROM $BUILD_FROM

# Install required packages
RUN apk add --no-cache \
    python3 \
    py3-pip

# Copy root filesystem
COPY rootfs /

# Copy app files
WORKDIR /opt/duplicate_video_finder
COPY app/ /opt/duplicate_video_finder/

# Make scripts executable
RUN chmod a+x /etc/services.d/duplicate-video-finder/run \
    && chmod a+x /opt/duplicate_video_finder/run.py

# Install Python requirements
RUN pip3 install --no-cache-dir -r /opt/duplicate_video_finder/requirements.txt

# Set entrypoint
CMD ["/init"]
