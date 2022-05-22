import pika
import time
import logging
import json


class Connection:
    def __init__(self, queue_name='', exchange_name='', bind=False, conn=None, durable=False):
        time.sleep(20)
        if not conn:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            self.channel = self.connection.channel()
        else:
            logging.info(f"[CONECTION] {conn.connection}, {conn.channel}")
            self.connection = conn.connection
            self.channel = conn.channel

        self.queue_name = queue_name
        self.exchange_name = exchange_name # durable=True
        self.__declare(bind, durable)

    def __declare(self, bind, durable):
        if self.queue_name != '':
            self.channel.queue_declare(queue=self.queue_name, durable=durable)

        if self.exchange_name != '':
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='fanout'
        )
        if bind:
            # Si es exgange que recibe tiene que crear una anon queue 
            anon_queue = self.channel.queue_declare(queue='', exclusive=True)
            self.queue_name = anon_queue.method.queue

            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name
        )

    def send(self, body):
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self.queue_name,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2)  #  message persistent
        )

    def recv(self, callback, start_consuming=True):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback,
            #auto_ack=True
        )
        if start_consuming:
            self.channel.start_consuming()

    def close(self):
        self.connection.close()

    def get_connection():
        return self.connection, self.channel

