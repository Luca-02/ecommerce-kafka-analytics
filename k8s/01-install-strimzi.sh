#!/bin/bash

# Script per installare Strimzi Operator su Minikube
# Versione Strimzi: 0.39.0 (versione stabile)

set -e

echo "🚀 Installazione Strimzi Operator..."

# Crea namespace per Strimzi
echo "📁 Creazione namespace strimzi-system..."
kubectl create namespace strimzi-system --dry-run=client -o yaml | kubectl apply -f -

# Installa Strimzi Operator
echo "⚙️  Installazione Strimzi Operator..."
kubectl create -f 'https://strimzi.io/install/latest?namespace=strimzi-system' -n strimzi-system

# Attendi che l'operator sia pronto
echo "⏳ Attendo che Strimzi Operator sia pronto..."
kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator -n strimzi-system --timeout=300s

echo "✅ Strimzi Operator installato con successo!"

# Verifica installazione
echo "🔍 Verifica installazione..."
kubectl get pods -n strimzi-system
kubectl get crd | grep strimzi

echo "🎉 Installazione completata!"