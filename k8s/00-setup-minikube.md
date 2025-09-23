# Setup Minikube per Kafka

## Prerequisiti
- Docker installato
- Minikube installato
- kubectl installato

## Passo 1: Avvio Minikube

```bash
# Avvia Minikube con configurazione ottimizzata per Kafka
minikube start --memory=8192 --cpus=4 --disk-size=20g --driver=docker

# Verifica che Minikube sia in esecuzione
minikube status

# Configura kubectl per usare il contesto di Minikube
kubectl config use-context minikube
```

## Passo 2: Verifica cluster
```bash
# Verifica che i nodi siano pronti
kubectl get nodes

# Verifica che i pod di sistema siano in esecuzione
kubectl get pods -n kube-system
```

## Note
- Memoria: 8GB necessari per Kafka cluster con 3 repliche
- CPU: 4 core per performance adeguate
- Disk: 20GB per storage persistente