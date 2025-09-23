#!/bin/bash

echo "📦 Installazione Strimzi Operator"
echo "================================="

# Versione Strimzi
STRIMZI_VERSION="0.38.0"

# Crea namespace per Kafka
echo "🔧 Creazione namespace kafka..."
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

# Installa Strimzi Operator
echo "📥 Download e installazione Strimzi Operator v${STRIMZI_VERSION}..."
kubectl create -f https://strimzi.io/install/latest?namespace=kafka -n kafka

# Aspetta che l'operator sia pronto
echo "⏳ Attendo che Strimzi Operator sia pronto..."
kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

if [ $? -eq 0 ]; then
    echo "✅ Strimzi Operator installato e pronto!"
else
    echo "❌ Timeout nell'attesa di Strimzi Operator"
    exit 1
fi

# Verifica installazione
echo "🔍 Verifica installazione..."
kubectl get pods -n kafka
kubectl get crd | grep strimzi

echo ""
echo "🎉 Strimzi Operator installato con successo!"
echo "📝 Namespace: kafka"
echo "📝 Versione: ${STRIMZI_VERSION}"
echo ""
echo "🔧 Risorse Strimzi disponibili:"
kubectl api-resources --api-group=kafka.strimzi.io