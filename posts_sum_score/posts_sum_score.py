import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class PostsSumScore:
    def __init__(self, queue_recv, queue_send):
        self.queue_recv = queue_recv
        self.queue_send = queue_send
        self.conn_recv = RabbitMQConnection(self.queue_recv)
        self.conn_send = RabbitMQConnection(self.queue_send)

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)

        if len(posts) == 0:
            pass

        post_score = self.__parser(posts)
        self.conn_send.send(json.dumps(post_score))

    def start(self):
        self.conn_recv.recv(self.__callback)
        
        self.conn_recv.close()
        self.conn_send.close()

    def __parser(self, posts):
        score_sum = 0
        total = 0
        for p in posts:
            score_sum += p["score"]
            total += 1

        p_score = {"score_sum": score_sum, "n_post": total}
        return p_score
