import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class CommentsFilterStudent:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = RabbitMQConnection(exchange_name=queue_recv, bind=True)
        self.conn_send = RabbitMQConnection(queue_name=queue_send)

    def __callback(self, ch, method, properties, body):
        comments = json.loads(body)

        result = self.__parser(comments)
        for r in result:
            logging.info(f"[FILTER_STUDENT] {r['post_id']}")

        self.conn_send.send(json.dumps(result))

    def start(self):
        self.conn_recv.recv(self.__callback)
        self.conn_recv.close()
        self.conn_send.close()

    def __parser(self, comments):
        student_comments = []
        for c in comments:
            if self.__filter_student(c):
                cmt = {"post_id": c["post_id"]}
                student_comments.append(cmt)

        logging.info(f"[FILTER_STUDENT] {len(student_comments)}")
        return student_comments

    def __filter_student(self, comment):
        st = ["university", "college", "student", "teacher", "professor"]

        return any(word.lower() in comment["body"] for word in st)
