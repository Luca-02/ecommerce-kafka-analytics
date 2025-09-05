#!/bin/bash

WAIT_TIME=5

function broker_ready() {
  kafka-topics --bootstrap-server "$1" --list > /dev/null 2>&1
}

echo "🔄 Waiting for Kafka brokers to be ready..."

IFS=',' read -ra BROKERS <<< "$KAFKA_BOOTSTRAP_SERVERS"
for broker in "${BROKERS[@]}"; do
  echo "⏳ Waiting for broker $broker to be ready..."
  until broker_ready "$broker"; do
    echo "🔁 $broker not ready yet, retrying in $WAIT_TIME sec..."
    sleep $WAIT_TIME
  done
  echo "✅ $broker is ready"
done

echo "🚀 All brokers are up. Proceeding to create topics..."

IFS=',' read -ra TOPIC_LIST <<< "$KAFKA_INIT_TOPICS"
for topic in "${TOPIC_LIST[@]}"; do
  echo "📦 Creating topic $topic with $KAFKA_TOPIC_PARTITIONS partitions and $KAFKA_TOPIC_RF replicas"
  kafka-topics --create --if-not-exists \
    --bootstrap-server "${KAFKA_BOOTSTRAP_SERVERS}" \
    --topic "$topic" \
    --partitions $KAFKA_TOPIC_PARTITIONS \
    --replication-factor $KAFKA_TOPIC_RF
done

echo "Topics created"
