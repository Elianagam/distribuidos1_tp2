import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class PostsAvgSentiment:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = RabbitMQConnection(queue_name=queue_recv)
        self.conn_send = RabbitMQConnection(queue_name=queue_send)

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)

        if "end" in posts:
            self.conn_send.send(json.dumps(posts))
            return
        result = self.__parser(posts)
        self.conn_send.send(json.dumps(result))

    def start(self):
        self.conn_recv.recv(self.__callback)
        
        self.conn_recv.close()
        self.conn_send.close()

    def __parser(self, posts):
        list_posts = []
        for p in posts:
            post_stm_avg = sum(p["sentiments"]) / len(p["sentiments"]) 
            p_stm = {
                "post_id": p["post_id"],
                "avg_sentiment": post_stm_avg
            }
            logging.info(f"[SENTIMENT_AVG] {p_stm}")
            list_posts.append(p_stm)

        return list_posts
