FROM openjdk:8-jdk-slim

RUN apt-get update && apt-get install -y libpcap0.8 wget unzip curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app/CICFlowMeter

# Copy the unpacked CICFlowMeter directory
COPY CICFlowMeter-4.0 /app/CICFlowMeter/CICFlowMeter-4.0

# Ensure permissions and library paths
RUN chmod +x /app/CICFlowMeter/CICFlowMeter-4.0/bin/cfm \
    && mkdir -p /data /out

ENV LD_LIBRARY_PATH=/app/CICFlowMeter/CICFlowMeter-4.0/lib/native:$LD_LIBRARY_PATH
WORKDIR /app/CICFlowMeter/CICFlowMeter-4.0

ENTRYPOINT ["./bin/cfm"]
