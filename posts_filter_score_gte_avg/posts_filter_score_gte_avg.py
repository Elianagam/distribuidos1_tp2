import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class PostsFilterScoreGteAvg:
    def __init__(self, queue_recv_avg, queue_recv_students, queue_send):
        self.conn_recv_avg = RabbitMQConnection(exchange_name=queue_recv_avg, bind=True)
        self.conn_recv_students = RabbitMQConnection(queue_name=queue_recv_students, conn=self.conn_recv_avg)
        self.conn_send = RabbitMQConnection(queue_name=queue_send)
        self.avg_score = None

    def __callback_students(self, ch, method, properties, body):
        posts = json.loads(body)

        if "end" in posts:
            self.conn_send.send(json.dumps({"end": True}))

        else:
            # TODO NOTHING UNTIL AVG != None
            post_score = self.__parser(posts)
            self.conn_send.send(json.dumps(post_score))

    def __callback_avg(self, ch, method, properties, body):
        avg = json.loads(body)

        if "end" in posts:
            self.conn_send.send(json.dumps({"end": True}))

        self.avg_score = avg["posts_score_avg"]

    def start(self):
        self.conn_recv_avg.recv(self.__callback_avg, start_consuming=False)
        self.conn_recv_students.recv(self.__callback_students)
        
        self.conn_recv_avg.close()
        self.conn_recv_students.close()
        self.conn_send.close()

    def __parser(self, posts):
        list_posts = []
        for p in posts:
            if p["score"] >= self.avg_score:
                list_posts.append({"url": p["url"]}
                )
        return list_posts
