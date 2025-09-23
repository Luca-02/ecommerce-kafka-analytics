#!/bin/bash

# Script completo per il deploy del cluster Kafka su Minikube
# Autore: Assistant
# Data: $(date)

set -e

NAMESPACE="kafka"
CLUSTER_NAME="kafka-cluster"

echo "🚀 Avvio deploy cluster Kafka su Minikube..."

# Funzione per controllare se un comando esiste
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verifica prerequisiti
echo "🔍 Verifica prerequisiti..."
if ! command_exists kubectl; then
    echo "❌ kubectl non trovato. Installare kubectl prima di continuare."
    exit 1
fi

if ! command_exists minikube; then
    echo "❌ minikube non trovato. Installare minikube prima di continuare."
    exit 1
fi

# Verifica che Minikube sia in esecuzione
if ! minikube status >/dev/null 2>&1; then
    echo "❌ Minikube non è in esecuzione. Avviare Minikube prima di continuare."
    echo "   Comando: minikube start --memory=8192 --cpus=4 --disk-size=20g --driver=docker"
    exit 1
fi

echo "✅ Prerequisiti verificati"

# Passo 1: Installazione Strimzi Operator
echo "📦 Installazione Strimzi Operator..."
./01-install-strimzi.sh

# Passo 2: Creazione namespace
echo "📁 Creazione namespace kafka..."
kubectl apply -f 02-namespace.yaml

# Passo 3: Deploy cluster Kafka
echo "⚙️  Deploy cluster Kafka..."
kubectl apply -f 03-kafka-cluster.yaml

# Attendi che il cluster sia pronto
echo "⏳ Attendo che il cluster Kafka sia pronto..."
echo "   Questo può richiedere alcuni minuti..."

# Attendi Zookeeper
kubectl wait --for=condition=Ready pod -l strimzi.io/name=${CLUSTER_NAME}-zookeeper -n ${NAMESPACE} --timeout=300s

# Attendi Kafka
kubectl wait --for=condition=Ready pod -l strimzi.io/name=${CLUSTER_NAME}-kafka -n ${NAMESPACE} --timeout=300s

echo "✅ Cluster Kafka pronto!"

# Passo 4: Creazione utenti
echo "👥 Creazione utenti SCRAM..."
kubectl apply -f 04-kafka-users.yaml

# Attendi che gli utenti siano creati
echo "⏳ Attendo creazione utenti..."
kubectl wait --for=condition=Ready kafkauser -l strimzi.io/cluster=${CLUSTER_NAME} -n ${NAMESPACE} --timeout=120s

echo "✅ Utenti creati!"

# Passo 5: Creazione topic
echo "📋 Creazione topic..."
kubectl apply -f 05-kafka-topics.yaml

# Attendi che i topic siano creati
echo "⏳ Attendo creazione topic..."
kubectl wait --for=condition=Ready kafkatopic -l strimzi.io/cluster=${CLUSTER_NAME} -n ${NAMESPACE} --timeout=120s

echo "✅ Topic creati!"

# Mostra informazioni del cluster
echo ""
echo "🎉 Deploy completato con successo!"
echo ""
echo "📊 Informazioni cluster:"
kubectl get kafka ${CLUSTER_NAME} -n ${NAMESPACE}
echo ""
echo "👥 Utenti creati:"
kubectl get kafkauser -n ${NAMESPACE}
echo ""
echo "📋 Topic creati:"
kubectl get kafkatopic -n ${NAMESPACE}
echo ""
echo "🔐 Per ottenere le credenziali degli utenti:"
echo "   Producer: kubectl get secret producer-user -n ${NAMESPACE} -o jsonpath='{.data.password}' | base64 -d"
echo "   Consumer: kubectl get secret consumer-user -n ${NAMESPACE} -o jsonpath='{.data.password}' | base64 -d"
echo "   Admin:    kubectl get secret admin-user -n ${NAMESPACE} -o jsonpath='{.data.password}' | base64 -d"
echo ""
echo "🌐 Per accedere al cluster dall'esterno:"
echo "   minikube service kafka-cluster-kafka-external-bootstrap -n ${NAMESPACE} --url"
echo ""
echo "✨ Il tuo cluster Kafka è pronto per l'uso!"