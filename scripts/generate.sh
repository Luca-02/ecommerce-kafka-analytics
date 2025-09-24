#!/usr/bin/env bash

set -eu

set -a
source .env
set +a

CN="kafka-admin"
PASSWORD=$(echo "$KAFKA_SSL_PASSWORD" | tr -d '\r')
ADMIN_USER=$(echo "$ADMIN_USER" | tr -d '\r')
ADMIN_PASSWORD=$(echo "$ADMIN_PASSWORD" | tr -d '\r')
KAFKA_HOSTS=$(echo "$KAFKA_HOSTS" | tr -d '\r')

TO_GENERATE_PEM="yes"
TO_GENERATE_CONFIG="yes"

VALIDITY_IN_DAYS=3650
GENERATED_ROOT_DIRECTORY="generated"
CA_WORKING_DIRECTORY="$GENERATED_ROOT_DIRECTORY/certificate-authority"
TRUSTSTORE_WORKING_DIRECTORY="$GENERATED_ROOT_DIRECTORY/truststore"
KEYSTORE_WORKING_DIRECTORY="$GENERATED_ROOT_DIRECTORY/keystore"
PEM_WORKING_DIRECTORY="$GENERATED_ROOT_DIRECTORY/pem"
CONFIG_WORKING_DIRECTORY="$GENERATED_ROOT_DIRECTORY/config"

CA_KEY_FILE="ca-key"
CA_CERT_FILE="ca-cert"
DEFAULT_TRUSTSTORE_FILE="kafka.truststore.jks"
KEYSTORE_SIGN_REQUEST="cert-file"
KEYSTORE_SIGN_REQUEST_SRL="ca-cert.srl"
KEYSTORE_SIGNED_CERT="cert-signed"

echo "Welcome to the Kafka SSL certificate authority, key store and trust store generator script."

echo "Creating generated directory structure..."
mkdir -p $GENERATED_ROOT_DIRECTORY

echo
echo "First we will create our own certificate authority"
echo "  Two files will be created if not existing:"
echo "    - $CA_WORKING_DIRECTORY/$CA_KEY_FILE -- the private key used later to sign certificates"
echo "    - $CA_WORKING_DIRECTORY/$CA_CERT_FILE -- the certificate that will be stored in the trust store"
echo "                                                        and serve as the certificate authority (CA)."
if [ -f "$CA_WORKING_DIRECTORY/$CA_KEY_FILE" ] && [ -f "$CA_WORKING_DIRECTORY/$CA_CERT_FILE" ]; then
  echo "Use existing $CA_WORKING_DIRECTORY/$CA_KEY_FILE and $CA_WORKING_DIRECTORY/$CA_CERT_FILE ..."
else
  rm -rf $CA_WORKING_DIRECTORY && mkdir $CA_WORKING_DIRECTORY
  echo
  echo "Generate $CA_WORKING_DIRECTORY/$CA_KEY_FILE and $CA_WORKING_DIRECTORY/$CA_CERT_FILE ..."
  echo
  openssl req -new -newkey rsa:4096 -days $VALIDITY_IN_DAYS -x509 -subj "/CN=$CN" \
    -keyout $CA_WORKING_DIRECTORY/$CA_KEY_FILE -out $CA_WORKING_DIRECTORY/$CA_CERT_FILE -nodes
fi

echo
echo "A keystore will be generated for each host in $KAFKA_HOSTS as each broker and logical client needs its own keystore"
echo
echo " NOTE: currently in Kafka, the Common Name (CN) does not need to be the FQDN of"
echo " this host. However, at some point, this may change. As such, make the CN"
echo " the FQDN. Some operating systems call the CN prompt 'first / last name'"
echo " To learn more about CNs and FQDNs, read:"
echo " https://docs.oracle.com/javase/7/docs/api/javax/net/ssl/X509ExtendedTrustManager.html"
rm -rf $KEYSTORE_WORKING_DIRECTORY && mkdir $KEYSTORE_WORKING_DIRECTORY

IFS=',' read -ra KAFKA_HOSTS <<< "$KAFKA_HOSTS"
for KAFKA_HOST in "${KAFKA_HOSTS[@]}"; do
  KAFKA_HOST=$(echo "$KAFKA_HOST" | xargs)
  KEY_STORE_FILE_NAME="$KAFKA_HOST.server.keystore.jks"
  echo
  echo "'$KEYSTORE_WORKING_DIRECTORY/$KEY_STORE_FILE_NAME' will contain a key pair and a self-signed certificate."
  keytool -genkey -keystore $KEYSTORE_WORKING_DIRECTORY/"$KEY_STORE_FILE_NAME" \
    -alias localhost -validity $VALIDITY_IN_DAYS -keyalg RSA \
    -noprompt -dname "CN=$KAFKA_HOST" -keypass $PASSWORD -storepass $PASSWORD

  echo
  echo "Now a certificate signing request will be made to the keystore."
  keytool -certreq -keystore $KEYSTORE_WORKING_DIRECTORY/"$KEY_STORE_FILE_NAME" \
    -alias localhost -file $KEYSTORE_SIGN_REQUEST -keypass $PASSWORD -storepass $PASSWORD

  echo
  echo "Now the private key of the certificate authority (CA) will sign the keystore's certificate."
  openssl x509 -req -CA $CA_WORKING_DIRECTORY/$CA_CERT_FILE \
    -CAkey $CA_WORKING_DIRECTORY/$CA_KEY_FILE \
    -in $KEYSTORE_SIGN_REQUEST -out $KEYSTORE_SIGNED_CERT \
    -days $VALIDITY_IN_DAYS -CAcreateserial
  # creates $CA_WORKING_DIRECTORY/$KEYSTORE_SIGN_REQUEST_SRL which is never used or needed.

  echo
  echo "Now the CA will be imported into the keystore."
  keytool -keystore $KEYSTORE_WORKING_DIRECTORY/"$KEY_STORE_FILE_NAME" -alias CARoot \
    -import -file $CA_WORKING_DIRECTORY/$CA_CERT_FILE -keypass $PASSWORD -storepass $PASSWORD -noprompt

  echo
  echo "Now the keystore's signed certificate will be imported back into the keystore."
  keytool -keystore $KEYSTORE_WORKING_DIRECTORY/"$KEY_STORE_FILE_NAME" -alias localhost \
    -import -file $KEYSTORE_SIGNED_CERT -keypass $PASSWORD -storepass $PASSWORD

  echo
  echo "Complete keystore generation!"
  echo
  echo "Deleting intermediate files. They are:"
  echo " - '$CA_WORKING_DIRECTORY/$KEYSTORE_SIGN_REQUEST_SRL': CA serial number"
  echo " - '$KEYSTORE_SIGN_REQUEST': the keystore's certificate signing request"
  echo " - '$KEYSTORE_SIGNED_CERT': the keystore's certificate, signed by the CA, and stored back"
  echo " into the keystore"
  rm -f $CA_WORKING_DIRECTORY/$KEYSTORE_SIGN_REQUEST_SRL $KEYSTORE_SIGN_REQUEST $KEYSTORE_SIGNED_CERT
done

echo
echo "Now the trust store will be generated from the certificate."
rm -rf $TRUSTSTORE_WORKING_DIRECTORY && mkdir $TRUSTSTORE_WORKING_DIRECTORY
keytool -keystore $TRUSTSTORE_WORKING_DIRECTORY/$DEFAULT_TRUSTSTORE_FILE \
  -alias CARoot -import -file $CA_WORKING_DIRECTORY/$CA_CERT_FILE \
  -noprompt -dname "CN=$CN" -keypass $PASSWORD -storepass $PASSWORD

if [ $TO_GENERATE_PEM == "yes" ]; then
  echo
  echo "The following files for SSL configuration will be created for a non-java client"
  echo "  $PEM_WORKING_DIRECTORY/ca-root.pem: CA file to use in certificate veriication"
  rm -rf $PEM_WORKING_DIRECTORY && mkdir $PEM_WORKING_DIRECTORY

  keytool -exportcert -alias CARoot -keystore $TRUSTSTORE_WORKING_DIRECTORY/$DEFAULT_TRUSTSTORE_FILE \
    -rfc -file $PEM_WORKING_DIRECTORY/ca-root.pem -storepass $PASSWORD
fi

if [ $TO_GENERATE_CONFIG == "yes" ]; then
  echo
  echo "Now generating configuration files for Kafka SSL and SASL setup"
  rm -rf $CONFIG_WORKING_DIRECTORY && mkdir $CONFIG_WORKING_DIRECTORY

  echo
  echo "Creating command.properties file..."
  cat > $CONFIG_WORKING_DIRECTORY/command.properties << EOF
security.protocol=SSL
ssl.truststore.location=/opt/bitnami/kafka/config/certs/kafka.truststore.jks
ssl.truststore.password=$PASSWORD
EOF

  echo
  echo "Creating kafka_jaas.conf file..."
  cat > $CONFIG_WORKING_DIRECTORY/kafka_jaas.conf << EOF
KafkaServer {
  org.apache.kafka.common.security.scram.ScramLoginModule required
  username="$ADMIN_USER"
  password="$ADMIN_PASSWORD";
};

Client {
  org.apache.zookeeper.server.auth.DigestLoginModule required
  username="$ADMIN_USER"
  password="$ADMIN_PASSWORD";
};

KafkaClient {
  org.apache.kafka.common.security.scram.ScramLoginModule required
  username="$ADMIN_USER"
  password="$ADMIN_PASSWORD";
};
EOF

  echo
  echo "Creating command.properties file..."
  cat > $CONFIG_WORKING_DIRECTORY/command.properties << EOF
security.protocol=SSL
ssl.key.password=$PASSWORD
ssl.truststore.location=/opt/bitnami/kafka/config/certs/kafka.truststore.jks
ssl.truststore.password=$PASSWORD
ssl.keystore.location=/opt/bitnami/kafka/config/certs/kafka.keystore.jks
ssl.keystore.password=$PASSWORD
EOF

  echo
  echo "Configuration files created successfully:"
  echo "  - $CONFIG_WORKING_DIRECTORY/command.properties"
  echo "  - $CONFIG_WORKING_DIRECTORY/kafka_jaas.conf"
  echo
  echo "These files can be used to configure your Kafka clients and brokers for SSL and SASL authentication."
fi

echo
echo "Script completed successfully!"
echo
echo "Generated directories and files:"
echo "  - $CA_WORKING_DIRECTORY/: Certificate Authority files"
echo "  - $KEYSTORE_WORKING_DIRECTORY/: Keystore files for each Kafka host"
echo "  - $TRUSTSTORE_WORKING_DIRECTORY/: Truststore file"
if [ $TO_GENERATE_PEM == "yes" ]; then
  echo "  - $PEM_WORKING_DIRECTORY/: PEM certificate files"
fi
if [ $TO_GENERATE_CONFIG == "yes" ]; then
  echo "  - $CONFIG_WORKING_DIRECTORY/: Configuration files for Kafka SSL/SASL setup"
fi
echo
echo "All files have been generated in the '$GENERATED_ROOT_DIRECTORY/' directory."