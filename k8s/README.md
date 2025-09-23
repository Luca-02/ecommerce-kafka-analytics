# Deploy Kafka su Minikube con Strimzi

Questa guida ti aiuta a deployare un cluster Kafka sicuro su Minikube usando Strimzi Operator.

## 🎯 Caratteristiche del Cluster

- **3 broker Kafka** con replicazione
- **3 nodi Zookeeper** per alta disponibilità
- **Sicurezza TLS** per comunicazione interna
- **SASL/SCRAM-SHA-512** per autenticazione client
- **ACL** per autorizzazione granulare
- **Topic preconfigurati** per ecommerce analytics

## 📋 Prerequisiti

Assicurati di avere installato:
- Docker
- Minikube
- kubectl

## 🚀 Deploy Rapido

### 1. Avvia Minikube
```bash
minikube start --memory=8192 --cpus=4 --disk-size=20g --driver=docker
```

### 2. Deploy del cluster
```bash
cd k8s
./deploy-kafka.sh
```

Il processo richiederà circa 5-10 minuti e installerà automaticamente:
- Strimzi Operator
- Cluster Kafka con 3 repliche
- Utenti SCRAM (producer, consumer, admin)
- Topic predefiniti

## 🔧 Gestione del Cluster

Usa lo script di utilità per gestire il cluster:

```bash
# Mostra stato del cluster
./kafka-utils.sh status

# Lista pod
./kafka-utils.sh pods

# Mostra topic
./kafka-utils.sh topics

# Mostra utenti
./kafka-utils.sh users

# Ottieni password utenti
./kafka-utils.sh passwords

# Informazioni connessione
./kafka-utils.sh connect

# Aiuto
./kafka-utils.sh help
```

## 👥 Utenti Configurati

Il cluster include 3 utenti preconfigurati:

### Producer User
- **Username**: `producer-user`
- **Permessi**: Scrittura su tutti i topic
- **Uso**: Applicazioni che producono messaggi

### Consumer User
- **Username**: `consumer-user`
- **Permessi**: Lettura da tutti i topic
- **Uso**: Applicazioni che consumano messaggi

### Admin User
- **Username**: `admin-user`
- **Permessi**: Amministrazione completa
- **Uso**: Gestione cluster e topic

## 📋 Topic Preconfigurati

| Topic | Partizioni | Repliche | Retention |
|-------|-----------|----------|-----------|
| `ecommerce-events` | 6 | 3 | 7 giorni |
| `orders` | 3 | 3 | 30 giorni |
| `analytics-events` | 6 | 3 | 14 giorni |

## 🔐 Configurazione Client

Per connetterti al cluster dall'esterno:

### Ottenere certificati TLS
```bash
kubectl get secret kafka-cluster-cluster-ca-cert -n kafka -o jsonpath='{.data.ca\.crt}' | base64 -d > ca.crt
```

### Ottenere password utenti
```bash
# Producer
kubectl get secret producer-user -n kafka -o jsonpath='{.data.password}' | base64 -d

# Consumer  
kubectl get secret consumer-user -n kafka -o jsonpath='{.data.password}' | base64 -d

# Admin
kubectl get secret admin-user -n kafka -o jsonpath='{.data.password}' | base64 -d
```

### Configurazione Properties
```properties
# Bootstrap servers
bootstrap.servers=<MINIKUBE_IP>:<EXTERNAL_PORT>

# Sicurezza
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="producer-user" password="<PASSWORD>";

# TLS
ssl.truststore.location=/path/to/truststore.jks
ssl.truststore.password=changeit
```

## 🔍 Monitoraggio

### Verificare stato cluster
```bash
kubectl get kafka kafka-cluster -n kafka
```

### Vedere logs
```bash
kubectl logs -l strimzi.io/name=kafka-cluster-kafka -n kafka -f
```

### Monitorare pod
```bash
kubectl get pods -n kafka -w
```

## 🗑️ Pulizia

Per eliminare completamente il cluster:
```bash
./kafka-utils.sh delete
```

## 📚 File del Progetto

- `00-setup-minikube.md` - Guida setup Minikube
- `01-install-strimzi.sh` - Script installazione Strimzi
- `02-namespace.yaml` - Definizione namespace
- `03-kafka-cluster.yaml` - Configurazione cluster Kafka
- `04-kafka-users.yaml` - Definizione utenti SCRAM
- `05-kafka-topics.yaml` - Configurazione topic
- `deploy-kafka.sh` - Script deploy completo
- `kafka-utils.sh` - Utilità gestione cluster

## 🎯 Prossimi Passi

Una volta che il cluster è operativo, puoi:
1. Deployare le tue applicazioni nel namespace `kafka`
2. Configurare i client per usare SASL/SCRAM
3. Monitorare le metriche del cluster
4. Aggiungere nuovi topic secondo necessità

## 🆘 Troubleshooting

### Problema: Pod in CrashLoopBackOff
```bash
kubectl describe pod <pod-name> -n kafka
kubectl logs <pod-name> -n kafka
```

### Problema: Utenti non creati
```bash
kubectl get kafkauser -n kafka
kubectl describe kafkauser producer-user -n kafka
```

### Problema: Topic non accessibili
```bash
kubectl get kafkatopic -n kafka
kubectl describe kafkatopic ecommerce-events -n kafka
```

Per supporto aggiuntivo, controlla i logs di Strimzi:
```bash
kubectl logs -l name=strimzi-cluster-operator -n strimzi-system
```