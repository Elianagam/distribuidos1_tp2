import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class PostsFilterScoreGteAvg:
    def __init__(self, queue_recv, queue_send):
        # Tiene que recibir from (posts_filter_columns + posts_avg_score)
        self.conn_recv = RabbitMQConnection(exchange_name=queue_recv, bind=True)
        self.conn_send = RabbitMQConnection(queue_name=queue_send)
        self.avg_socre = 0

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)

        # Consume avg: "posts_score_avg"
        if len(posts) == 0:
            # when client finish, have send all
            # send signal finish
            self.conn_send.send(json.dumps({"end": True}))

        else:
            post_score = self.__parser(posts)
            self.conn_send.send(json.dumps(post_score))

    def start(self):
        self.conn_recv.recv(self.__callback)
        
        self.conn_recv.close()
        self.conn_send.close()

    def __parser(self, posts):
        list_posts = []
        for p in posts:
            if p["score"] >= self.avg_score:
                list_posts.append(
                    {
                        "id": p["id"],
                        "url": p["url"]
                    }
                )
        return list_posts
