import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class CommentsFilterStudent:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = RabbitMQConnection(exchange_name=queue_recv, bind=True)
        self.conn_send = RabbitMQConnection(queue_send)


    def __callback(self, ch, method, properties, body):
        comments = json.loads(body)
        
        if len(comments) == 0: pass
            # TODO SOMETHING??

        result = self.__parser(comments)
        for r in result:
            logging.info(f"[FILTER_STD] {r['post_id']}")
        #self.conn_send.send(json.dumps(result))

    def start(self):
        self.conn_recv.recv(self.__callback)
        self.conn_recv.close()
        self.conn_send.close()

    def __parser(self, comments):
        st = ["university", "college", "student", "teacher", "professor"]
        student_comments = []
        for c in comments:
            if any(word.lower() in c["body"] for word in st):
                cmt = {"post_id": c["post_id"]}
                student_comments.append(cmt)

        return student_comments