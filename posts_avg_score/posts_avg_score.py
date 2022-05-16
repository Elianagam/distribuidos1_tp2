import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class PostsAvgScore:
    def __init__(self, queue_recv, queue_send):
        self.count_posts = 0 
        self.sum_score = 0 
        self.conn_recv = RabbitMQConnection(queue_name=queue_recv)
        self.conn_send = RabbitMQConnection(exchange_name=queue_send)

    def __callback(self, ch, method, properties, body):
        post_score = json.loads(body)

        if "end" in post_score:
            avg = self.__calculate_avg()
            self.conn_send.send(json.dumps({"posts_score_avg": avg}))
            return

        self.__sum_score(post_score)

    def start(self):
        self.conn_recv.recv(self.__callback)
        
        self.conn_recv.close()
        self.conn_send.close()

    def __sum_score(self, post_score):
        self.count_posts += post_score["n_post"]
        self.sum_score += post_score["sum_score"]

    def __calculate_avg(self):
        # when client finish, have send all
        # publish avg
        avg = self.sum_score / self.count_posts
        
        logging.info(f"--- [POST_SCORE_AVG] {avg}")
