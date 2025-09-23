#!/bin/bash

echo "🧪 Test Kafka Cluster"
echo "===================="

# Colori per output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verifica che il cluster sia attivo
echo "🔍 Verifica stato cluster..."
if ! kubectl get kafka demo-cluster -n kafka &> /dev/null; then
    print_error "Cluster Kafka non trovato"
    exit 1
fi

# Ottieni stato del cluster
CLUSTER_STATUS=$(kubectl get kafka demo-cluster -n kafka -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
if [ "$CLUSTER_STATUS" != "True" ]; then
    print_warning "Cluster non ancora completamente pronto"
    echo "   Stato: $CLUSTER_STATUS"
else
    print_status "Cluster Kafka pronto"
fi

# Verifica pod
echo ""
echo "📊 Stato pod:"
kubectl get pods -n kafka -l strimzi.io/cluster=demo-cluster

# Verifica servizi
echo ""
echo "🌐 Servizi esposti:"
kubectl get svc -n kafka -l strimzi.io/cluster=demo-cluster

# Test connettività con un pod temporaneo
echo ""
echo "🔗 Test connettività..."

# Crea un pod temporaneo per i test
kubectl run kafka-test-client --image=quay.io/strimzi/kafka:0.38.0-kafka-3.6.0 --rm -i --restart=Never -n kafka -- sleep 3600 &
TEST_POD_PID=$!

# Attendi che il pod sia pronto
echo "⏳ Attendo pod di test..."
sleep 10

# Verifica che il pod sia in esecuzione
if kubectl get pod kafka-test-client -n kafka &> /dev/null; then
    print_status "Pod di test creato"
    
    # Test lista topic
    echo ""
    echo "📝 Lista topic disponibili:"
    kubectl exec -n kafka kafka-test-client -- /opt/kafka/bin/kafka-topics.sh \
        --bootstrap-server demo-cluster-kafka-bootstrap:9092 \
        --list || print_warning "Impossibile listare i topic"
    
    # Test produzione messaggio (se hai configurato un utente)
    echo ""
    echo "📤 Test invio messaggio..."
    echo "test-message-$(date +%s)" | kubectl exec -i -n kafka kafka-test-client -- \
        /opt/kafka/bin/kafka-console-producer.sh \
        --bootstrap-server demo-cluster-kafka-bootstrap:9092 \
        --topic events || print_warning "Test produzione fallito - potrebbe essere necessaria autenticazione"
    
    # Cleanup pod di test
    kubectl delete pod kafka-test-client -n kafka &> /dev/null
else
    print_warning "Impossibile creare pod di test"
fi

# Informazioni di connessione
echo ""
echo "🔗 Informazioni di connessione:"
echo "   Bootstrap interno: demo-cluster-kafka-bootstrap.kafka.svc.cluster.local:9094"
echo "   Bootstrap esterno: $(minikube ip):32100"
echo ""
echo "🔐 Per connettersi con SASL SCRAM:"
echo "   security.protocol=SASL_SSL"
echo "   sasl.mechanism=SCRAM-SHA-512"
echo "   sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username=\"producer\" password=\"producer123\";"
echo ""
echo "📋 Secret disponibili:"
kubectl get secrets -n kafka | grep -E "(admin|producer|consumer)"

# Mostra come ottenere i certificati
echo ""
echo "🔒 Per ottenere il certificato CA:"
echo "   kubectl get secret demo-cluster-cluster-ca-cert -n kafka -o jsonpath='{.data.ca\.crt}' | base64 -d > ca.crt"

echo ""
print_status "Test completato!"