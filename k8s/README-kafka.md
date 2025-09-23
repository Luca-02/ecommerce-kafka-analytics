# Deploy Kafka su Minikube con Strimzi

Questa guida descrive come deployare un cluster Kafka su Minikube usando Strimzi Operator per una demo locale.

## 📋 Prerequisiti

- **Docker** installato e in esecuzione
- **Minikube** installato ([guida installazione](https://minikube.sigs.k8s.io/docs/start/))
- **kubectl** installato ([guida installazione](https://kubernetes.io/docs/tasks/tools/))
- Almeno **8GB RAM** e **4 CPU cores** disponibili per Minikube

## 🚀 Installazione Passo Passo

### 1. Setup Minikube

```bash
./setup-minikube.sh
```

Questo script:
- Avvia Minikube con configurazione ottimizzata (4 CPU, 8GB RAM, 20GB disk)
- Abilita addon necessari (ingress, dashboard)
- Configura kubectl per usare il contesto Minikube

### 2. Installazione Strimzi Operator

```bash
./install-strimzi.sh
```

Questo script:
- Crea il namespace `kafka`
- Installa Strimzi Operator versione 0.38.0
- Attende che l'operator sia pronto

### 3. Deploy Cluster Kafka

```bash
./deploy-kafka.sh
```

Questo script deploya:
- **Cluster Kafka** con 3 broker
- **Zookeeper** con 3 nodi
- **Utenti SCRAM**: admin, producer, consumer
- **Topic**: events (3 partizioni, 3 repliche)
- **Configurazione sicurezza**: TLS + SASL SCRAM-SHA-512

## 🔧 Configurazione Cluster

### Kafka Cluster
- **3 broker Kafka** (versione 3.6.0)
- **3 nodi Zookeeper**
- **Storage persistente**: 10GB per Kafka, 5GB per Zookeeper
- **Risorse**: 1-2GB RAM, 0.5-1 CPU per broker

### Listeners
- **TLS (9093)**: Comunicazione inter-broker con autenticazione TLS
- **SASL (9094)**: Client interni con SASL SCRAM-SHA-512
- **External (9095)**: Accesso esterno via NodePort (32100-32103)

### Sicurezza
- **TLS** abilitato per tutte le comunicazioni
- **SASL SCRAM-SHA-512** per autenticazione client
- **ACL** configurate per producer e consumer
- **Super user**: admin

## 👥 Utenti Configurati

| Utente   | Password     | Permessi                    |
|----------|-------------|----------------------------|
| admin    | admin123    | Super user (tutti i permessi) |
| producer | producer123 | Write su topic `events`    |
| consumer | consumer123 | Read su topic `events`     |

## 📝 Topic Configurati

- **Nome**: events
- **Partizioni**: 3
- **Repliche**: 3
- **Retention**: 7 giorni
- **Compressione**: Snappy

## 🔗 Connessione al Cluster

### Da dentro il cluster Kubernetes
```
Bootstrap server: demo-cluster-kafka-bootstrap.kafka.svc.cluster.local:9094
```

### Da fuori il cluster (NodePort)
```bash
# Ottieni IP Minikube
minikube ip

# Bootstrap server esterno
<MINIKUBE_IP>:32100
```

### Configurazione Client SASL

```properties
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
    username="producer" \
    password="producer123";
ssl.truststore.location=/path/to/ca.crt
ssl.truststore.type=PEM
```

### Ottenere il Certificato CA

```bash
kubectl get secret demo-cluster-cluster-ca-cert -n kafka \
    -o jsonpath='{.data.ca\.crt}' | base64 -d > ca.crt
```

## 🧪 Test e Verifica

### Test Cluster
```bash
./test-kafka.sh
```

### Comandi Utili

```bash
# Stato del cluster
kubectl get kafka -n kafka

# Pod in esecuzione
kubectl get pods -n kafka

# Log dei broker
kubectl logs -l strimzi.io/name=demo-cluster-kafka -n kafka

# Port forward per accesso locale
kubectl port-forward svc/demo-cluster-kafka-bootstrap 9094:9094 -n kafka

# Dashboard Minikube
minikube dashboard
```

## 🗑️ Cleanup

### Rimuovi solo il cluster Kafka
```bash
./cleanup-kafka.sh
```

### Rimuovi tutto (incluso Minikube)
```bash
./cleanup-kafka.sh
kubectl delete namespace kafka
minikube stop
minikube delete
```

## 📊 Monitoraggio

Strimzi include automaticamente:
- **Cruise Control** per bilanciamento automatico
- **Entity Operator** per gestione topic e utenti
- **Metriche JMX** esposte per monitoring

## 🔧 Personalizzazioni

Per modificare la configurazione:

1. **Risorse**: Modifica `resources` in `kafka-cluster.yaml`
2. **Storage**: Modifica `storage.size` per aumentare lo spazio
3. **Utenti**: Aggiungi nuovi utenti in `kafka-users.yaml`
4. **Topic**: Crea nuovi topic copiando `kafka-topic.yaml`

## ⚠️ Note per Produzione

Questa configurazione è ottimizzata per **demo locale**. Per produzione considera:

- Aumentare le risorse (CPU/RAM)
- Configurare storage class appropriato
- Implementare backup automatici
- Configurare monitoring avanzato (Prometheus/Grafana)
- Hardening della sicurezza
- Network policies
- Resource quotas