import signal
import logging

import json
from common.connection import Connection


class CommentsFilterStudent:
    def __init__(self, queue_recv, queue_send, recv_workers, worker_key):
        self.worker_key = f"worker.student.num{worker_key}"
        self.conn_recv = Connection(exchange_name=queue_recv, bind=True, 
            exchange_type='topic', routing_key=self.worker_key)
        self.conn_send = Connection(exchange_name=queue_send, exchange_type='topic')
        self.recv_workers = recv_workers
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.conn_recv.close()
        self.conn_send.close()

    def start(self):
        self.conn_recv.recv(self.__callback)

    def __callback(self, ch, method, properties, body):
        comments = json.loads(body)

        if "end" in comments:
            self.__send_data(comments)
            return
        else:
            result = self.__parser(comments)
            self.__send_data(result)

    def __send_data(self, data):
        self.conn_send.send(json.dumps(data), routing_key=self.worker_key)

    def __parser(self, comments):
        student_comments = []
        for comment in comments:
            if self.__filter_student(comment):
                comment_new = {
                    "url": comment["url"],
                    "score": comment["score"]
                }
                student_comments.append(comment_new)
        return student_comments

    def __filter_student(self, comment):
        student_words = ["university", "college", "student", "teacher", "professor"]
        body =  " ".join(comment["body"])
        return any(word.lower() in body for word in student_words)
