import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class PostsSumScore:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = RabbitMQConnection(exchange_name=queue_recv, bind=True)
        self.conn_send = RabbitMQConnection(queue_name=queue_send)

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)

        if "end" in posts:
            # when client finish, have send all
            # send signal finish
            self.conn_send.send(json.dumps(posts))
            return

        post_score = self.__parser(posts)
        self.conn_send.send(json.dumps(post_score))

    def start(self):
        self.conn_recv.recv(self.__callback)
        
        self.conn_recv.close()
        self.conn_send.close()

    def __parser(self, posts):
        sum_score = 0
        count_posts = 0
        for p in posts:
            sum_score += p["score"]
            count_posts += 1

        p_score = {"sum_score": sum_score, "n_post": count_posts}
        return p_score
