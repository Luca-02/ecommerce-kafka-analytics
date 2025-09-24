# Start minikube
minikube start --driver=docker

# Switch to minikube context
kubectl config use-context minikube

# Apply namespace
kubectl apply -f k8s/namespace.yml

# Install Strimzi
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
# Wait for Strimzi to be ready
#kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Apply Kafka cluster
kubectl apply -f k8s/kafka-cluster.yml -n kafka
# Wait for Kafka cluster to be ready
#kubectl wait kafka/my-cluster --for=condition=Ready -n kafka --timeout=300s

# Apply Kafka users
kubectl apply -f k8s/kafka-users.yml -n kafka
# Wait for Kafka users to be ready
#kubectl wait --for=condition=Ready kafkauser/admin -n kafka --timeout=300s
#kubectl wait --for=condition=Ready kafkauser/producer-user -n kafka --timeout=300s
#kubectl wait --for=condition=Ready kafkauser/consumer-user -n kafka --timeout=300s

# Apply Kafka topics
kubectl apply -f k8s/kafka-topics.yml -n kafka
# Wait for Kafka topics to be ready
#kubectl wait --for=condition=Ready kafkatopic/e-commerce-events -n kafka --timeout=300s

# Create firebase secret
kubectl create secret generic firebase-credentials --from-file=serviceAccountKey.json=secret/serviceAccountKey.json -n kafka

#minikube docker-env | Invoke-Expression

# Build and load image
docker build -t ecommerce-kafka-analytics/event-simulator-service:latest -f event-simulator-service/Dockerfile .
docker build -t ecommerce-kafka-analytics/analytics-service:latest -f analytics-service/Dockerfile .
minikube image load ecommerce-kafka-analytics/event-simulator-service:latest
minikube image load ecommerce-kafka-analytics/analytics-service:latest
# List images
minikube image ls

kubectl apply -f k8s/producer-deployment.yml -n kafka
kubectl apply -f k8s/consumer-deployment.yml -n kafka
kubectl apply -f k8s/bad-consumer-deployment.yml -n kafka
kubectl apply -f k8s/bad-producer-deployment.yml -n kafka

#kubectl -n kafka get secret producer-user -o jsonpath='{.data.password}'
#kubectl -n kafka get secret consumer-user -o jsonpath='{.data.password}'
#kubectl get secret my-cluster-cluster-ca-cert -n kafka -o jsonpath='{.data.ca\.crt}'

# Useful commands
#kubectl get pods -n kafka
#kubectl get kafka -n kafka
#kubectl get kafkauser -n kafka
#kubectl get kafkatopic -n kafka


# Test Kafka fault tolerance
# Delete pod
#kubectl delete pod <pod-name> -n kafka
#kubectl get pods -n kafka