# Kafka Log Consumption Experiment

This repository contains code and configurations for an experiment that demonstrates consuming server logs from a Virtual Machine (VM) using Kafka. The logs are collected by Filebeat running on the VM and published to a Kafka topic, which is then consumed by a Python script running on a local computer.

## Purpose of the Experiment

The purpose of this experiment is to:
1. Test the setup and configuration for reading logs from a VM using Filebeat and sending them to a Kafka broker.
2. Verify that a Python-based Kafka consumer can successfully read and process these logs.
3. Provide a working example of log aggregation using Filebeat and Kafka for monitoring, troubleshooting, or log analysis.

## Architecture Overview

1. **Virtual Machine (VM)**:
   - **Filebeat** is configured to monitor specific log files and publish them to a Kafka topic.
   - A sample API (or application) generates logs, which are monitored by Filebeat.

2. **Local Machine**:
   - **Kafka Consumer**: A Python script that connects to the Kafka topic and reads the logs.

The architecture diagram looks as follows:

```
[ VM: API & Filebeat ] --> [ Kafka Broker ] --> [ Local Machine: Kafka Consumer Script ]
```

## Repository Contents

- `consumer.py`: Python script that consumes logs from the Kafka topic.
- `filebeat.yml`: Reference Filebeat configuration file for publishing logs to Kafka.
- `api_sample/`: Directory containing a sample API that generates logs for testing purposes.
- `README.md`: This readme file.

## Prerequisites

- Kafka and Zookeeper installed and running (can be set up locally or on a server).
- Python 3.x installed.
- `kafka-python` library for consuming messages.
- Filebeat installed on the VM.

## Setup Instructions

### Step 1: Configure Filebeat on the VM

1. **Install Filebeat** on the VM if not already installed:
   ```bash
   # On Debian/Ubuntu
   sudo apt-get install filebeat
   ```
   
2. **Configure `filebeat.yml`**:
   Update the Filebeat configuration to monitor log files and send them to Kafka. Below is a reference configuration (`filebeat.yml`):

   ```yaml
   filebeat.inputs:
     - type: log
       enabled: true
       paths:
         - /var/log/myapp/*.log  # Update to your log file path

   output.kafka:
     hosts: ["<KAFKA_BROKER_IP>:9092"]  # Replace <KAFKA_BROKER_IP> with your Kafka broker's IP address
     topic: "server_logs"
     partition.round_robin:
       reachable_only: false
     required_acks: 1
     compression: gzip
     max_message_bytes: 1000000
   ```

3. **Start Filebeat**:
   ```bash
   sudo filebeat -e -c /path/to/filebeat.yml
   ```

### Step 2: Setup Kafka on Your Local Machine

1. **Download and Install Kafka**:
   Follow the [Apache Kafka Quickstart](https://kafka.apache.org/quickstart) guide to install and start Kafka.

2. **Create the Kafka Topic**:
   ```bash
   bin/kafka-topics.sh --create --topic server_logs --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   ```

### Step 3: Run the Sample API (Optional)

1. **Run the API**:
   If you want to generate logs using a sample API, you can use the provided API in the `api_sample/` directory. This API will generate logs at `/var/log/myapp/server.log` (or any path you configure).

2. **Log File Setup**:
   Ensure that the log file directory `/var/log/myapp/` exists and is writable by the API.

### Step 4: Run the Kafka Consumer Script

1. **Install the `kafka-python` Library**:
   ```bash
   pip install kafka-python
   ```

2. **Run the Consumer Script**:
   Use the provided `consumer.py` script to start consuming logs from the Kafka topic:
   ```bash
   python consumer.py
   ```

   The `consumer.py` script should look like this:

   ```python
   from kafka import KafkaConsumer
   import json
   import logging

   # Enable logging at the DEBUG level
   logging.basicConfig(level=logging.DEBUG)

   # Kafka configuration
   bootstrap_servers = 'localhost:9092'
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
       print("Timestamp:", log_data.get('@timestamp'))
       print("Host:", log_data.get('host', {}).get('name'))
       print("Log message:", log_data.get('message'))
       print("File path:", log_data.get('log', {}).get('file', {}).get('path'))
       print("-" * 50)
   ```

## Testing the Setup

1. **Verify Kafka Topic Data**:
   Check if the logs are being published to the Kafka topic using the Kafka console consumer:
   ```bash
   bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic server_logs --from-beginning
   ```

2. **Run the Python Consumer Script**:
   If the Python script is running correctly, it should display the log messages published by Filebeat.

## Troubleshooting

- If the consumer script cannot connect to Kafka, check the Kafka broker configuration, particularly the `advertised.listeners` setting.
- Ensure that Filebeat is running without errors. Check the Filebeat logs for any issues.

## Next Steps

The following steps outline the future enhancements for this project to expand its capabilities and make it suitable for log analysis and threat detection using AI:

1. **Make Filebeat Send Logs by Batches**  
   - Modify the Filebeat configuration to send logs to Kafka in batches, rather than log-by-log. This can help improve performance and reduce the number of requests made to Kafka.
   - Use the `bulk_max_size` parameter in the Filebeat configuration to control the batch size:
     ```yaml
     output.kafka:
       hosts: ["<KAFKA_BROKER_IP>:9092"]
       topic: "server_logs"
       bulk_max_size: 1024  # Adjust the batch size according to your requirements
     ```
   - Test the batch sending configuration to ensure logs are still transmitted correctly and verify that Kafka is able to handle the incoming batches.

2. **Create an Extractor Algorithm to Maintain the Logs and Format Them as Model Input**  
   - Develop an algorithm to preprocess the logs, cleaning and structuring them to make them suitable for analysis.
   - The algorithm should:
     - Parse relevant fields from each log entry (e.g., timestamp, log level, message content).
     - Remove or anonymize sensitive information, if necessary.
     - Format the logs in a structured format (e.g., JSON or CSV) that can be directly fed to a machine learning model.
   - Implement logic to handle batch processing of logs, ensuring that each batch is consistent in format and structure.

3. **Integrate an AI Model to Detect Threats in the Logs**  
   - Train or integrate an existing machine learning model capable of detecting threats or anomalies in log data.
   - The model should:
     - Analyze each log entry within the batch to determine if it exhibits characteristics of a potential threat.
     - Provide a confidence score or classification (e.g., "benign" or "threat") for each log.
   - Add post-processing steps to log the results or trigger alerts based on the model's predictions.
   - Consider using existing models or frameworks such as scikit-learn, TensorFlow, or PyTorch, or explore pre-trained models for anomaly detection in log data.
   - Continuously improve the model by updating the training dataset with new threats and refining the algorithm based on feedback.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [Apache Kafka](https://kafka.apache.org/)
- [Filebeat](https://www.elastic.co/beats/filebeat)
- [kafka-python](https://github.com/dpkp/kafka-python)
