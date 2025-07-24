#!/bin/bash

# Wait until a broker is up
echo "Waiting for Kafka to be ready..."
until kafka-topics --bootstrap-server "${KAFKA_BOOTSTRAP_SERVERS}" --list >/dev/null 2>&1; do
  sleep 3
done

IFS=',' read -ra TOPIC_LIST <<< "$KAFKA_INIT_TOPICS"
for topic in "${TOPIC_LIST[@]}"; do
  echo "Creating topic: $topic"
  kafka-topics --create --if-not-exists \
    --bootstrap-server "${KAFKA_BOOTSTRAP_SERVERS}" \
    --replication-factor 3 \
    --partitions 3 \
    --topic "$topic"
done

echo "Topics created"