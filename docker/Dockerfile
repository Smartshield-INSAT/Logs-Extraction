# Base image
FROM ubuntu:20.04

# Install tcpdump and kafkacat
RUN apt-get update && \
    apt-get install -y tcpdump kafkacat iproute2 iputils-ping && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Script to capture traffic and send to Kafka
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
