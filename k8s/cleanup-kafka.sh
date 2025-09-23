#!/bin/bash

echo "🧹 Cleanup Kafka Cluster"
echo "========================"

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

echo "🗑️  Rimozione risorse Kafka..."

# Rimuovi topic
if kubectl get kafkatopic events -n kafka &> /dev/null; then
    kubectl delete kafkatopic events -n kafka
    print_status "Topic events rimosso"
fi

# Rimuovi utenti
for user in admin producer consumer; do
    if kubectl get kafkauser $user -n kafka &> /dev/null; then
        kubectl delete kafkauser $user -n kafka
        print_status "Utente $user rimosso"
    fi
done

# Rimuovi secret utenti
for secret in admin-credentials producer-credentials consumer-credentials; do
    if kubectl get secret $secret -n kafka &> /dev/null; then
        kubectl delete secret $secret -n kafka
        print_status "Secret $secret rimosso"
    fi
done

# Rimuovi cluster Kafka
if kubectl get kafka demo-cluster -n kafka &> /dev/null; then
    kubectl delete kafka demo-cluster -n kafka
    print_status "Cluster Kafka rimosso"
    
    echo "⏳ Attendo rimozione completa del cluster..."
    kubectl wait --for=delete kafka/demo-cluster -n kafka --timeout=300s
fi

# Rimuovi PVC (opzionale - commentato per preservare i dati)
# echo "🗄️  Rimozione Persistent Volume Claims..."
# kubectl delete pvc -l strimzi.io/cluster=demo-cluster -n kafka
# print_warning "PVC rimossi - i dati sono stati eliminati permanentemente"

echo ""
echo "🔍 Stato finale namespace kafka:"
kubectl get all -n kafka

echo ""
print_status "Cleanup completato!"
echo ""
print_warning "Note:"
echo "   - I PVC non sono stati rimossi per preservare i dati"
echo "   - Per rimuovere anche i PVC: kubectl delete pvc -l strimzi.io/cluster=demo-cluster -n kafka"
echo "   - Per rimuovere Strimzi: kubectl delete -f https://strimzi.io/install/latest?namespace=kafka -n kafka"
echo "   - Per rimuovere namespace: kubectl delete namespace kafka"