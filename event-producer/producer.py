import json
import logging
import os

from kafka import KafkaProducer

from models import Event

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9093')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'pollution-data')
# USERNAME = os.getenv('KAFKA_USERNAME', 'producerUser')
# PASSWORD = os.getenv('KAFKA_PASSWORD', 'producerPass')
#
# SSL_CAFILE = '/certs/ca-cert.pem'
# SSL_CERTFILE = '/certs/kafka-cert.pem'
# SSL_KEYFILE = '/certs/kafka-key.pem'

class Producer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            acks='all',
            retries=5,
            # security_protocol="SASL_SSL",
            # ssl_cafile=SSL_CAFILE,
            # ssl_certfile=SSL_CERTFILE,
            # ssl_keyfile=SSL_KEYFILE,
            # sasl_mechanism="PLAIN",
            # sasl_plain_username=USERNAME,
            # sasl_plain_password=PASSWORD,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def produce(self, event: Event):
        try:
            # self.producer.send(KAFKA_TOPIC, key=event.user_id, value=event)
            logging.info(f"[Kafka] Event sent: {event}")
        except Exception as e:
            logging.error(f"[Kafka] Error: {e}")

    def close(self):
        self.producer.flush()
        self.producer.close()
        logging.info("[Kafka] Producer closed cleanly!")
