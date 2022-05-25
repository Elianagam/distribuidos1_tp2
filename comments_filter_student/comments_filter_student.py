import signal
import logging

import json
from common.connection import Connection


class CommentsFilterStudent:
    def __init__(self, queue_recv, queue_send, recv_workers):
        self.conn_recv = Connection(queue_name=queue_recv, durable=True)
        self.conn_send = Connection(queue_name=queue_send)
        self.end_recv = 0
        self.recv_workers = recv_workers
        signal.signal(signal.SIGINT, self.exit_gracefully)

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
            if self.end_recv == self.recv_workers:
                self.conn_send.send(json.dumps(comments))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        result = self.__parser(comments)
        self.conn_send.send(json.dumps(result))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def __parser(self, comments):
        student_comments = []
        for c in comments:
            if self.__filter_student(c):
                cmt = {
                    "url": c["url"],
                    "score": c["score"]
                }
                student_comments.append(cmt)
        #logging.info(f"[STUDENTS FILTER] size={len(student_comments)}")

        return student_comments

    def __filter_student(self, comment):
        st = ["university", "college", "student", "teacher", "professor"]
        body =  " ".join(comment["body"])
        return any(word.lower() in body for word in st)
