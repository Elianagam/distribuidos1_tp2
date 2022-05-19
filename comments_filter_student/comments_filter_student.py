import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class CommentsFilterStudent:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = RabbitMQConnection(exchange_name=queue_recv, bind=True)
        self.conn_send = RabbitMQConnection(queue_name=queue_send)

    def __callback(self, ch, method, properties, body):
        comments = json.loads(body)

        if "end" in comments:
            self.conn_send.send(json.dumps(comments))
            return
        
        result = self.__parser(comments)
        self.conn_send.send(json.dumps(result))

    def start(self):
        self.conn_recv.recv(self.__callback)
        self.conn_recv.close()
        self.conn_send.close()

    def __parser(self, comments):
        student_comments = []
        for c in comments:
            #logging.info(f" [FILTER STUDENT] {c}")

            if self.__filter_student(c):
                logging.info(f" --------- [FILTER STUDENT] {c} ----------")
                cmt = {
                    "url": c["url"],
                    "score": c["score"]
                }
                student_comments.append(cmt)

        logging.info(f"[FILTER_STUDENT] Size: {len(student_comments)}")
        return student_comments

    def __filter_student(self, comment):
        st = ["university", "college", "student", "teacher", "professor"]
        body =  " ".join(comment["body"])
        return any(word.lower() in body for word in st)
