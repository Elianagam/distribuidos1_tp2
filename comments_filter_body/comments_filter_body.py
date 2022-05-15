import logging

import json
import re 
from common.rabbitmq_connection import RabbitMQConnection

class CommentsFilterBody:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = RabbitMQConnection(queue_name=queue_recv)

        self.conn_send = RabbitMQConnection(exchange_name=queue_send)


    def __callback(self, ch, method, properties, body):
        comments = json.loads(body)
        
        if len(comments) == 0: pass
            # TODO SOMETHING??
        result = self.__parser(comments)
        self.conn_send.send(json.dumps(result))

    def start(self):
        self.conn_recv.recv(self.__callback)
        self.conn_recv.close()
        self.conn_send.close()

    def __parser(self, comments):
        filter_comments = []
        for c in comments:
            if self.__invalid_body(c): continue

            cmt = {
                "post_id": self.__get_post_id(c),
                "body": c["body"],
                "sentiment": c["sentiment"],
            }
            filter_comments.append(cmt)

        return filter_comments

    def __invalid_body(self, comment):
        # Dont send comment without body or deleted
        return len(comment["body"]) == 0 or comment["body"] == "[removed]"

    def __get_post_id(self, comment):
        rgx = r'https://old.reddit.com/r/meirl/comments/([^/]+)/meirl/.*'
        return re.findall(rgx, comment["permalink"])
