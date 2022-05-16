import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class PostsMaxAvgSentiment:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = RabbitMQConnection(queue_name=queue_recv)
        self.conn_send = RabbitMQConnection(queue_name=queue_send)
        self.max_avg = {"post_id": None, "avg_sentiment": 0}

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)

        if "end" in posts:
            # Send only post with max avg sentiment
            self.conn_send.send(json.dumps(self.max_avg))
            logging.info(f"[POST MAX AVG SENTIMENT] {self.max_avg}")
            
            self.conn_send.send(json.dumps(posts))
            return

        self.__parser(posts)

    def start(self):
        self.conn_recv.recv(self.__callback)
        
        self.conn_recv.close()
        self.conn_send.close()

    def __parser(self, posts):
        for p in posts:
            if p["avg_sentiment"] > self.max_avg["avg_sentiment"]:
                self.max_avg = p
