import logging

import json
import re 
from common.rabbitmq_connection import RabbitMQConnection

class CommentsFilterWithSentiment:
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
        filter_comments = []
        for c in comments:
            if c["sentiment"] != '':
                cmt = {
                    "post_id": c["post_id"],
                    "sentiment": float(c["sentiment"])
                }
                filter_comments.append(cmt)

        logging.info(f"[FILTER_SENTIMENT] {len(filter_comments)}")
        return filter_comments