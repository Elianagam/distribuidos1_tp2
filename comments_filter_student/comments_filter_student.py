import signal
import logging

import json
from common.connection import Connection


class CommentsFilterStudent:
    def __init__(self, queue_recv, queue_send, recv_workers):
        self.conn_recv = Connection(queue_name=queue_recv, durable=True)
        self.conn_send = Connection(queue_name=queue_send, durable=True)
        self.end_recv = 0
        self.recv_workers = recv_workers
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.conn_recv.close()
        self.conn_send.close()

    def start(self):
        self.conn_recv.recv(self.__callback)
        self.exit_gracefully()

    def __callback(self, ch, method, properties, body):
        comments = json.loads(body)

        if "end" in comments:
            self.end_recv += 1
            #if self.end_recv == self.recv_workers:
            self.conn_send.send(json.dumps(comments))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        else:
            result = self.__parser(comments)
            self.conn_send.send(json.dumps(result))
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def __parser(self, comments):
        student_comments = []
        for comment in comments:
            if self.__filter_student(comment):
                comment_new = {
                    "url": c["url"],
                    "score": c["score"]
                }
                student_comments.append(comment_new)

        return student_comments

    def __filter_student(self, comment):
        student_words = ["university", "college", "student", "teacher", "professor"]
        body =  " ".join(comment["body"])
        return any(word.lower() in body for word in student_words)
