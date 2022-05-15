import pika
import time
import logging
import json


class RabbitMQConnection:
    def __init__(self, queue_name='', exchange_name='', bind=False):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('rabbitmq')
        ) #rabbitmq/localhost
        self.channel = self.connection.channel()
        
        self.queue_name = queue_name
        self.exchange_name = exchange_name # durable=True
        self.__declare(bind)

    def __declare(self, bind):
        if self.queue_name != '':
            self.channel.queue_declare(queue=self.queue_name)

        if self.exchange_name != '':
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='fanout'
        )
        if bind:
            anon_queue = channel.queue_declare(queue='', exclusive=True)
            self.queue_name = anon_queue.method.queue

            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name
        )

    def send(self, body):
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.queue_name,
            body=body,
            #properties=pika.BasicProperties(delivery_mode=2)  #  message persistent
        )

    def recv(self, callback):
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        self.channel.start_consuming()

    def close(self):
        self.connection.close()


