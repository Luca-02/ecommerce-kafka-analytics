#!/bin/bash

# Script di utilità per gestire il cluster Kafka
# Fornisce comandi comuni per monitorare e gestire Kafka

NAMESPACE="kafka"
CLUSTER_NAME="kafka-cluster"

show_help() {
    echo "Utilità per gestire il cluster Kafka su Minikube"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandi disponibili:"
    echo "  status      - Mostra stato del cluster"
    echo "  pods        - Mostra pod Kafka e Zookeeper"
    echo "  topics      - Lista tutti i topic"
    echo "  users       - Lista tutti gli utenti"
    echo "  passwords   - Mostra le password degli utenti"
    echo "  logs        - Mostra logs dei broker Kafka"
    echo "  connect     - Mostra informazioni per connettersi"
    echo "  delete      - Elimina tutto il cluster (ATTENZIONE!)"
    echo "  help        - Mostra questo aiuto"
}

show_status() {
    echo "📊 Stato cluster Kafka:"
    kubectl get kafka ${CLUSTER_NAME} -n ${NAMESPACE}
    echo ""
    echo "📈 Stato operatori:"
    kubectl get pods -n strimzi-system
}

show_pods() {
    echo "🏃 Pod Kafka e Zookeeper:"
    kubectl get pods -n ${NAMESPACE} -l strimzi.io/cluster=${CLUSTER_NAME}
}

show_topics() {
    echo "📋 Topic disponibili:"
    kubectl get kafkatopic -n ${NAMESPACE}
}

show_users() {
    echo "👥 Utenti configurati:"
    kubectl get kafkauser -n ${NAMESPACE}
}

show_passwords() {
    echo "🔐 Password utenti:"
    echo "Producer: $(kubectl get secret producer-user -n ${NAMESPACE} -o jsonpath='{.data.password}' | base64 -d 2>/dev/null || echo 'Non disponibile')"
    echo "Consumer: $(kubectl get secret consumer-user -n ${NAMESPACE} -o jsonpath='{.data.password}' | base64 -d 2>/dev/null || echo 'Non disponibile')"
    echo "Admin:    $(kubectl get secret admin-user -n ${NAMESPACE} -o jsonpath='{.data.password}' | base64 -d 2>/dev/null || echo 'Non disponibile')"
}

show_logs() {
    echo "📝 Logs broker Kafka (ultimi 50 righe):"
    kubectl logs -l strimzi.io/name=${CLUSTER_NAME}-kafka -n ${NAMESPACE} --tail=50
}

show_connect_info() {
    echo "🌐 Informazioni connessione:"
    echo ""
    echo "Bootstrap servers (interno al cluster):"
    echo "  ${CLUSTER_NAME}-kafka-bootstrap.${NAMESPACE}.svc.cluster.local:9094"
    echo ""
    echo "Bootstrap servers (esterno - NodePort):"
    EXTERNAL_IP=$(minikube ip 2>/dev/null || echo "Minikube non disponibile")
    EXTERNAL_PORT=$(kubectl get service ${CLUSTER_NAME}-kafka-external-bootstrap -n ${NAMESPACE} -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "N/A")
    echo "  ${EXTERNAL_IP}:${EXTERNAL_PORT}"
    echo ""
    echo "Certificati TLS:"
    echo "  kubectl get secret ${CLUSTER_NAME}-cluster-ca-cert -n ${NAMESPACE} -o jsonpath='{.data.ca\.crt}' | base64 -d > ca.crt"
    echo ""
    echo "Configurazione client:"
    echo "  security.protocol=SASL_SSL"
    echo "  sasl.mechanism=SCRAM-SHA-512"
    echo "  sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username=\"[USER]\" password=\"[PASSWORD]\";"
    echo "  ssl.truststore.location=/path/to/truststore.jks"
}

delete_cluster() {
    echo "⚠️  ATTENZIONE: Questa operazione eliminerà TUTTO il cluster Kafka!"
    echo "   - Tutti i dati verranno persi"
    echo "   - I topic e gli utenti verranno eliminati"
    echo "   - L'operazione è irreversibile"
    echo ""
    read -p "Sei sicuro di voler continuare? (digita 'ELIMINA' per confermare): " confirm
    if [ "$confirm" = "ELIMINA" ]; then
        echo "🗑️  Eliminazione cluster in corso..."
        kubectl delete kafka ${CLUSTER_NAME} -n ${NAMESPACE} 2>/dev/null || true
        kubectl delete kafkauser --all -n ${NAMESPACE} 2>/dev/null || true
        kubectl delete kafkatopic --all -n ${NAMESPACE} 2>/dev/null || true
        kubectl delete namespace ${NAMESPACE} 2>/dev/null || true
        echo "✅ Cluster eliminato"
    else
        echo "❌ Operazione annullata"
    fi
}

case "$1" in
    status)
        show_status
        ;;
    pods)
        show_pods
        ;;
    topics)
        show_topics
        ;;
    users)
        show_users
        ;;
    passwords)
        show_passwords
        ;;
    logs)
        show_logs
        ;;
    connect)
        show_connect_info
        ;;
    delete)
        delete_cluster
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo "Comando non riconosciuto: $1"
        echo "Usa '$0 help' per vedere i comandi disponibili"
        exit 1
        ;;
esac