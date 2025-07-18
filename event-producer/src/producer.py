from loguru import logger

from .models import Event


class Producer:
    # def __init__(self):
    #     self.producer = KafkaProducer(
    #         bootstrap_servers=KAFKA_BROKER,
    #         acks='all',
    #         retries=5,
    #         security_protocol="SASL_SSL",
    #         ssl_cafile=SSL_CAFILE,
    #         ssl_certfile=SSL_CERTFILE,
    #         ssl_keyfile=SSL_KEYFILE,
    #         sasl_mechanism="PLAIN",
    #         sasl_plain_username=USERNAME,
    #         sasl_plain_password=PASSWORD,
    #         value_serializer=lambda v: json.dumps(v).encode('utf-8')
    #     )

    def produce(self, event: Event):
        try:
            # self.producer.send(KAFKA_TOPIC, key=event.user_id, value=event)
            logger.info(f"[Kafka] Event sent: {event}")
        except Exception as e:
            logger.error(f"[Kafka] Error: {e}")

    def close(self):
        self.producer.flush()
        self.producer.close()
        logger.info("[Kafka] Producer closed cleanly!")
