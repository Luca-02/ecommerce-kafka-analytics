#!/bin/bash

echo "🚀 Setup Minikube per Kafka con Strimzi"
echo "======================================"

# Controlla se minikube è installato
if ! command -v minikube &> /dev/null; then
    echo "❌ Minikube non è installato. Installalo prima di continuare."
    echo "   Visita: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Controlla se kubectl è installato
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl non è installato. Installalo prima di continuare."
    exit 1
fi

echo "✅ Minikube e kubectl sono installati"

# Avvia Minikube con configurazione ottimizzata per Kafka
echo "🔧 Avvio Minikube con configurazione per Kafka..."
minikube start \
    --driver=docker \
    --cpus=4 \
    --memory=8192 \
    --disk-size=20g \
    --kubernetes-version=v1.28.3

# Verifica che Minikube sia in esecuzione
if ! minikube status | grep -q "Running"; then
    echo "❌ Errore nell'avvio di Minikube"
    exit 1
fi

echo "✅ Minikube è in esecuzione"

# Abilita addon necessari
echo "🔧 Abilitazione addon Minikube..."
minikube addons enable ingress
minikube addons enable dashboard

# Configura il contesto kubectl
kubectl config use-context minikube

# Verifica la connessione al cluster
echo "🔍 Verifica connessione al cluster..."
kubectl cluster-info

echo ""
echo "🎉 Setup Minikube completato!"
echo "📝 Informazioni cluster:"
echo "   - Driver: docker"
echo "   - CPU: 4"
echo "   - Memory: 8GB"
echo "   - Disk: 20GB"
echo "   - Kubernetes: v1.28.3"
echo ""
echo "🔗 Per accedere al dashboard: minikube dashboard"
echo "🔗 Per ottenere l'IP: minikube ip"