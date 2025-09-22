#!/bin/bash

set -e

echo "Generating SSL certificates for Kafka SASL_SSL setup..."

mkdir -p certs
cd certs

set -a
source ../.env
set +a

PASSWORD="$KAFKA_SSL_PASSWORD"

echo "Certificate passwords:"
echo "  - Keystore password: $PASSWORD"
echo "  - Truststore password: $PASSWORD"
echo "  - Key password: $PASSWORD"

echo "Cleaning up previous certificates..."
rm -f ca-key ca-cert ca-cert.pem ca-cert.srl keystore.jks truststore.jks cert-file cert-signed
rm -f keystore_creds key_creds truststore_creds

echo "Generating Certificate Authority (CA)..."
openssl req -new -x509 -keyout ca-key -out ca-cert -days 365 \
    -subj "/CN=kafka-ca/OU=Kafka/O=Local/L=Milan/ST=Lombardy/C=IT" \
    -nodes

echo "Generating Kafka keystore..."
keytool -keystore keystore.jks -alias kafka -validity 365 -genkey -keyalg RSA \
    -storepass "$PASSWORD" -keypass "$PASSWORD" \
    -dname "CN=kafka,OU=Kafka,O=Local,L=Milan,ST=Lombardy,C=IT" \
    -ext SAN=DNS:kafka,DNS:localhost,IP:127.0.0.1

echo "Generating certificate signing request..."
keytool -keystore keystore.jks -alias kafka -certreq -file cert-file \
    -storepass "$PASSWORD"

echo "Signing certificate with CA..."
openssl x509 -req -CA ca-cert -CAkey ca-key -in cert-file -out cert-signed \
    -days 365 -CAcreateserial \
    -extensions SAN -extfile <(echo "[SAN]"; echo "subjectAltName=DNS:kafka,DNS:localhost,IP:127.0.0.1")

echo "Importing CA into keystore..."
keytool -keystore keystore.jks -alias CARoot -import -file ca-cert \
    -storepass "$PASSWORD" -noprompt

echo "Importing signed certificate into keystore..."
keytool -keystore keystore.jks -alias kafka -import -file cert-signed \
    -storepass "$PASSWORD" -noprompt

echo "Creating truststore..."
keytool -keystore truststore.jks -alias CARoot -import -file ca-cert \
    -storepass "$PASSWORD" -noprompt

echo "Converting CA to PEM format for Python clients..."
cp ca-cert ca-cert.pem

echo "Certificates generated successfully!"
echo "Files created in ./certs/:"
ls -la

echo "Cleaning up temporary files..."
rm -f cert-file cert-signed ca-key

echo "Certificate generation completed!"
