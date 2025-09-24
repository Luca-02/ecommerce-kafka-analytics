#!/bin/bash
cd /opt/bitnami/kafka/bin/ || exit

function broker_ready() {
  ./kafka-topics.sh --bootstrap-server "$1" --list --command-config "$COMMAND_PROPERTIES" > /dev/null 2>&1
}

echo "🔄 Waiting for Kafka brokers to be ready..."

IFS=',' read -ra BROKERS <<< "$KAFKA_BOOTSTRAP_SERVERS"
for broker in "${BROKERS[@]}"; do
  echo "⏳ Waiting for broker $broker to be ready..."
  until broker_ready "$broker"; do
    echo "🔁 $broker not ready yet, retrying in $WAIT_TIME sec..."
    sleep 5
  done
  echo "✅ $broker is ready"
done

echo "🚀 All brokers are up. Proceeding to create topics..."

echo "Creating event topic..."
./kafka-topics.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --create --topic "$KAFKA_EVENT_TOPIC" --if-not-exists \
    --partitions "$KAFKA_EVENT_TOPIC_PARTITIONS" --replication-factor "$KAFKA_EVENT_TOPIC_REPLICATION_FACTOR" \
    --command-config "$COMMAND_PROPERTIES"

echo "Creating SCRAM users..."
./kafka-configs.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --alter --add-config "SCRAM-SHA-256=[iterations=8192,password=$ADMIN_PASSWORD]" \
    --entity-type users --entity-name "$ADMIN_USER" \
    --command-config "$COMMAND_PROPERTIES"
./kafka-configs.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --alter --add-config "SCRAM-SHA-256=[iterations=8192,password=$PRODUCER_PASSWORD]" \
    --entity-type users --entity-name "$PRODUCER_USER" \
    --command-config "$COMMAND_PROPERTIES"
./kafka-configs.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --alter --add-config "SCRAM-SHA-256=[iterations=8192,password=$CONSUMER_PASSWORD]" \
    --entity-type users --entity-name "$CONSUMER_USER" \
    --command-config "$COMMAND_PROPERTIES"

echo 'Setting up producer ACLs...'
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --add --allow-principal User:"$PRODUCER_USER" \
    --operation Write --topic "$KAFKA_EVENT_TOPIC" \
    --command-config "$COMMAND_PROPERTIES"
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --add --allow-principal User:"$PRODUCER_USER" \
    --operation Describe --topic "$KAFKA_EVENT_TOPIC" \
    --command-config "$COMMAND_PROPERTIES"
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --add --allow-principal User:"$PRODUCER_USER" \
    --operation Create --topic "$KAFKA_EVENT_TOPIC" \
    --command-config "$COMMAND_PROPERTIES"

echo 'Setting up consumer ACLs...'
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --add --allow-principal User:"$CONSUMER_USER" \
    --operation Read --topic "$KAFKA_EVENT_TOPIC" \
    --command-config "$COMMAND_PROPERTIES"
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --add --allow-principal User:"$CONSUMER_USER" \
    --operation Describe --topic "$KAFKA_EVENT_TOPIC" \
    --command-config "$COMMAND_PROPERTIES"
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --add --allow-principal User:"$CONSUMER_USER" \
    --operation Read --group "$KAFKA_CONSUMER_GROUP_ID" \
    --command-config "$COMMAND_PROPERTIES"
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --add --allow-principal User:"$CONSUMER_USER" \
    --operation Describe --group "$KAFKA_CONSUMER_GROUP_ID" \
    --command-config "$COMMAND_PROPERTIES"

echo 'Setup completed!'

echo 'SCRAM users:'
./kafka-configs.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --describe --entity-type users \
    --command-config "$COMMAND_PROPERTIES"

echo "Current ACLs:"
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
    --list --command-config "$COMMAND_PROPERTIES"
