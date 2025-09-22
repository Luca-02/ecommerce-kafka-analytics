#!/bin/bash
cd /opt/bitnami/kafka/bin/ || exit

echo "Creating event topic..."
./kafka-topics.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --create --topic e-commerce-events --if-not-exists --command-config "$COMMAND_PROPERTIES"

echo "Creating SCRAM users..."
./kafka-configs.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --alter --add-config 'SCRAM-SHA-256=[iterations=8192,password=admin-secret]' --entity-type users --entity-name admin --command-config "$COMMAND_PROPERTIES"
./kafka-configs.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --alter --add-config 'SCRAM-SHA-256=[iterations=8192,password=producer-secret]' --entity-type users --entity-name producer-user --command-config "$COMMAND_PROPERTIES"
./kafka-configs.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --alter --add-config 'SCRAM-SHA-256=[iterations=8192,password=consumer-secret]' --entity-type users --entity-name consumer-user --command-config "$COMMAND_PROPERTIES"

echo 'Setting up producer ACLs...'
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --add --allow-principal User:producer-user --operation Write --topic e-commerce-events --command-config "$COMMAND_PROPERTIES"
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --add --allow-principal User:producer-user --operation Describe --topic e-commerce-events --command-config "$COMMAND_PROPERTIES"
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --add --allow-principal User:producer-user --operation Create --topic e-commerce-events --command-config "$COMMAND_PROPERTIES"

echo 'Setting up consumer ACLs...'
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --add --allow-principal User:consumer-user --operation Read --topic e-commerce-events --command-config "$COMMAND_PROPERTIES"
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --add --allow-principal User:consumer-user --operation Describe --topic e-commerce-events --command-config "$COMMAND_PROPERTIES"
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --add --allow-principal User:consumer-user --operation Read --group analytics-service --command-config "$COMMAND_PROPERTIES"
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --add --allow-principal User:consumer-user --operation Describe --group analytics-service --command-config "$COMMAND_PROPERTIES"

echo 'Setup completed!'

echo 'SCRAM users:'
./kafka-configs.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --describe --entity-type users --command-config "$COMMAND_PROPERTIES"

echo "Current ACLs:"
./kafka-acls.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --list --command-config "$COMMAND_PROPERTIES"
