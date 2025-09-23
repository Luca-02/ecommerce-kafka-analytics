#!/bin/bash

echo "🚀 Deploy Kafka su Minikube con Strimzi"
echo "======================================"

# Colori per output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funzione per stampa colorata
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verifica prerequisiti
echo "🔍 Verifica prerequisiti..."

if ! kubectl cluster-info &> /dev/null; then
    print_error "Cluster Kubernetes non raggiungibile"
    echo "   Esegui prima: ./setup-minikube.sh"
    exit 1
fi

if ! kubectl get namespace kafka &> /dev/null; then
    print_error "Namespace kafka non trovato"
    echo "   Esegui prima: ./install-strimzi.sh"
    exit 1
fi

if ! kubectl get crd kafkas.kafka.strimzi.io &> /dev/null; then
    print_error "Strimzi Operator non installato"
    echo "   Esegui prima: ./install-strimzi.sh"
    exit 1
fi

print_status "Prerequisiti verificati"

# Deploy dei secret per le password utenti
echo ""
echo "🔐 Deploy secret utenti..."
kubectl apply -f kafka/user-secrets.yaml
print_status "Secret utenti creati"

# Deploy del cluster Kafka
echo ""
echo "🔧 Deploy cluster Kafka..."
kubectl apply -f kafka/kafka-cluster.yaml

# Attendi che il cluster sia pronto
echo ""
echo "⏳ Attendo che il cluster Kafka sia pronto..."
echo "   Questo può richiedere alcuni minuti..."

# Attendi che tutti i pod di Kafka siano pronti
kubectl wait --for=condition=Ready pod -l strimzi.io/name=demo-cluster-kafka -n kafka --timeout=600s
if [ $? -ne 0 ]; then
    print_error "Timeout nell'attesa dei pod Kafka"
    echo "   Controlla lo stato con: kubectl get pods -n kafka"
    exit 1
fi

# Attendi che tutti i pod di Zookeeper siano pronti
kubectl wait --for=condition=Ready pod -l strimzi.io/name=demo-cluster-zookeeper -n kafka --timeout=300s
if [ $? -ne 0 ]; then
    print_error "Timeout nell'attesa dei pod Zookeeper"
    echo "   Controlla lo stato con: kubectl get pods -n kafka"
    exit 1
fi

print_status "Cluster Kafka pronto!"

# Deploy degli utenti
echo ""
echo "👥 Deploy utenti SCRAM..."
kubectl apply -f kafka/kafka-users.yaml

# Attendi che gli utenti siano creati
echo "⏳ Attendo creazione utenti..."
sleep 30

# Verifica che gli utenti siano stati creati
for user in admin producer consumer; do
    if kubectl get kafkauser $user -n kafka &> /dev/null; then
        print_status "Utente $user creato"
    else
        print_warning "Utente $user non ancora pronto"
    fi
done

# Deploy del topic
echo ""
echo "📝 Deploy topic events..."
kubectl apply -f kafka/kafka-topic.yaml

# Attendi che il topic sia creato
echo "⏳ Attendo creazione topic..."
sleep 15

if kubectl get kafkatopic events -n kafka &> /dev/null; then
    print_status "Topic events creato"
else
    print_warning "Topic events non ancora pronto"
fi

echo ""
echo "🎉 Deploy Kafka completato!"
echo ""
echo "📊 Stato del cluster:"
kubectl get pods -n kafka
echo ""
echo "👥 Utenti creati:"
kubectl get kafkauser -n kafka
echo ""
echo "📝 Topic creati:"
kubectl get kafkatopic -n kafka
echo ""
echo "🔗 Informazioni di connessione:"
echo "   Bootstrap servers (interno): demo-cluster-kafka-bootstrap.kafka.svc.cluster.local:9094"
echo "   Bootstrap servers (esterno): $(minikube ip):32100"
echo ""
echo "🔐 Credenziali utenti:"
echo "   Admin: admin / admin123"
echo "   Producer: producer / producer123"
echo "   Consumer: consumer / consumer123"
echo ""
echo "🛠️  Comandi utili:"
echo "   - Stato cluster: kubectl get kafka -n kafka"
echo "   - Log Kafka: kubectl logs -l strimzi.io/name=demo-cluster-kafka -n kafka"
echo "   - Port forward: kubectl port-forward svc/demo-cluster-kafka-bootstrap 9094:9094 -n kafka"