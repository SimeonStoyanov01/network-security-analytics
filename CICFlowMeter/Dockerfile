# Use Ubuntu as the base image
FROM ubuntu:22.04

# Non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Java 8, libpcap, and other dependencies
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk libpcap-dev bash curl unzip && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME for Java 8
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Copy CICFlowMeter from your repository into the container
COPY CICFlowMeter-4.0/CICFlowMeter-4.0 /opt/CICFlowMeter-4.0

# Make binaries executable
RUN chmod +x /opt/CICFlowMeter-4.0/bin/cfm && \
    chmod +x /opt/CICFlowMeter-4.0/bin/CICFlowMeter

# Set the Java library path to find libjnetpcap.so
ENV JAVA_OPTS="-Djava.library.path=/opt/CICFlowMeter-4.0/lib/native"
ENV PATH="$PATH:/opt/CICFlowMeter-4.0/bin"

# Set working directory (for mounting input/output directories)
WORKDIR /data

# Declare mount points for data and output
VOLUME ["/data", "/out"]

# Default entrypoint runs CICFlowMeter CLI
ENTRYPOINT ["cfm"]
