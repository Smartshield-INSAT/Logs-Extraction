import logging
from kafka import KafkaConsumer
import json

# logging.basicConfig(level=logging.DEBUG)

# Kafka configuration
bootstrap_servers = '192.168.100.88:9092'
topic = 'server_logs'

# Create a Kafka consumer
consumer = KafkaConsumer(
    topic,
    bootstrap_servers=[bootstrap_servers],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='log-consumers',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Process the consumed messages
print("Consuming messages from Kafka topic:", topic)
for message in consumer:
    log_data = message.value
    print(log_data)
    print("Timestamp:", log_data.get('@timestamp'))
    print("Host:", log_data.get('host', {}).get('name'))
    print("Log message:", log_data.get('message'))
    print("File path:", log_data.get('log', {}).get('file', {}).get('path'))
    print("-" * 50)
