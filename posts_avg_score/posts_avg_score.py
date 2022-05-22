import logging

import json
from common.connection import Connection


class PostsAvgScore:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = Connection(queue_name=queue_recv)
        self.conn_send = Connection(exchange_name=queue_send)
        self.count_posts = 0 
        self.sum_score = 0 

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)

        if "end" in posts:
            avg = self.__calculate_avg()
            self.conn_send.send(json.dumps({"posts_score_avg": avg}))
            self.conn_send.send(json.dumps(posts))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        self.__sum_score(posts)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self.conn_recv.recv(self.__callback)
        
        self.conn_recv.close()
        self.conn_send.close()

    def __sum_score(self, posts):
        for p in posts:
            self.sum_score += p["score"]
            self.count_posts += 1

    def __calculate_avg(self):
        # when client finish, have send all
        # publish avg
        avg = self.sum_score / self.count_posts
        
        logging.info(f" --- [POST_SCORE_AVG] {avg}")
        return avg
