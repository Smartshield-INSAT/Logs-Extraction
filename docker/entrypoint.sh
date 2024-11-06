#!/bin/bash

# Define variables
PCAP_FILE="capture_$(date +%Y%m%d_%H%M%S).pcap"
KAFKA_TOPIC="topic_server_1"
KAFKA_BROKER="kafka_broker:9092"

# Step 1: Capture network traffic and save it to a .pcap file
echo "Starting tcpdump capture..."
tcpdump -i any -w "$PCAP_FILE"

# # Step 2: Send the .pcap file content to Kafka
# echo "Sending $PCAP_FILE to Kafka topic $KAFKA_TOPIC..."
# cat "$PCAP_FILE" | kafkacat -b "$KAFKA_BROKER" -t "$KAFKA_TOPIC"

# Optional: Remove the .pcap file after sending
# rm "$PCAP_FILE"

