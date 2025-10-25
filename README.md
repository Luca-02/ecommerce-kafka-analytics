# E-commerce Kafka Analytics System

A distributed system for real-time e-commerce event analysis using Apache Kafka, developed for the Cloud Computing Technologies course (A.Y 2024/25).

## 📋 Project Overview

This project implements an event-driven architecture for real-time e-commerce data analysis. The system simulates user behavior on an e-commerce platform, captures events through Apache Kafka, and processes them to generate analytics stored in Firebase Firestore.

### System Architecture

The system is composed of three main components:

1. **Event Simulator Service** - Simulates user behavior and generates events  
2. **Apache Kafka Cluster** - Message broker for event management  
3. **Analytics Service** - Processes events and generates statistics  

## 🏗️ System Components

### Event Simulator Service

The simulation service generates realistic e-commerce events:

- **Supported Event Types**:
  - `session_started` - User session start  
  - `category_viewed` - Category viewed  
  - `product_viewed` - Product viewed  
  - `product_added_to_cart` - Product added to cart  
  - `product_removed_from_cart` - Product removed from cart  
  - `purchase` - Purchase completed  
  - `session_ended` - User session end  

- **Features**:
  - Multi-process simulation for high concurrency  
  - Synthetic data generation (users, products, categories)  
  - Configurable probabilistic behaviors  
  - Realistic user geolocation  

### Apache Kafka Cluster

Secure Kafka cluster with:

- **Configuration**:
  - 3 Kafka brokers for high availability  
  - Topic partition replication  
  - Replication factor: 3  
  - Min ISR: 2  

- **Security**:
  - Encryption in Transit: SSL/TLS  
  - Authentication: SASL/SCRAM-SHA-256  
  - Authorization: Kafka ACLs for access control  
  - Custom SSL certificates  

### Analytics Service

Event processing service with:

- **Processing**:
  - Multi-threaded Kafka consumer  
  - Event-type specific processing patterns  
  - Real-time statistical aggregations  
  - Concurrency management with worker pool  

- **Storage**:
  - Firebase Firestore for persistence  
  - Collections organized by data type  
  - Aggregations by country, date, product  
  - Lifetime and temporal statistics  

## 🚀 Deployment and Configuration

### Prerequisites

- Docker & Docker Compose  
- Python 3.11+  
- Firebase Project  
- Make  

### Initial Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Luca-02/ecommerce-kafka-analytics.git
    cd ecommerce-kafka-analytics
    ```

2. **Initialization**:
    ```bash
    make init
    ```
    This command:
    - Creates Python virtual environments  
    - Installs dependencies  
    - Generates SSL certificates and Kafka configurations  

3. **Firebase Configuration**:
   - Place the `serviceAccountKey.json` file in `secret/`  
   - Configure environment variables in the `.env` file  

### Deployment Modes

1. **Development (with Firebase Emulator)**
    ```bash
    # Start Firebase Emulator
    make firebase-start
    
    # In another terminal
    make compose-dev-up
    ```

2. **Full Production**
    ```bash
    make compose-up
    ```

3. **Kafka Cluster Only**
    ```bash
    make kafka-up
    ```

4. **Services Only (Producer/Consumer)**
    ```bash
    make services-up
    ```

### Kubernetes Deployment

For deployment in Kubernetes run:
```bash
bash ./scripts/k8s-start.sh
```

## 🧪 Testing and Security

### Security Tests

The project includes "attacker" services to test security:
```bash
make attacker-up
```

This starts:
- Producer with invalid certificates
- Producer with incorrect credentials
- Consumer with invalid certificates
- Consumer with incorrect credentials

### Monitoring

- **Kafka UI**: Available at `http://localhost:8888`
- **Firebase Emulator UI**: Available at `http://localhost:4000`
- **Logs**: Available through `docker-compose logs`

## 🔧 Technologies Used

- **Python**: Main programming language
- **Apache Kafka**: Message streaming platform
- **Firebase Firestore**: NoSQL database for analytics
- **Docker**: Containerization
- **Kubernetes**: Orchestration
- **Strimzi**: Kafka operator for Kubernetes