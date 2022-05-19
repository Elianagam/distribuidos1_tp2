import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class PostsAvgScore:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = RabbitMQConnection(queue_name=queue_recv)
        self.conn_send = RabbitMQConnection(queue_name=queue_send)
        self.count_posts = 0 
        self.sum_score = 0 

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)

        if "end" in posts:
            avg = self.__calculate_avg()
            self.conn_send.send(json.dumps({"posts_score_avg": avg}))
            return

        self.__sum_score(posts)

    def start(self):
        self.conn_recv.recv(self.__callback)
        
        self.conn_recv.close()
        self.conn_send.close()

    def __sum_score(self, posts):
        for p in posts:
            self.sum_score += p["score"]
            self.count_posts += 1
        logging.info(f"[SCORE SUM] score: {self.sum_score}, post:{self.count_posts}")

    def __calculate_avg(self):
        # when client finish, have send all
        # publish avg
        avg = self.sum_score / self.count_posts
        
        logging.info(f"--- [POST_SCORE_AVG] {avg}")
        return avg
