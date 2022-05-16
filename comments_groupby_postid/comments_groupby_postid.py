import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class CommentsGroupbyPostId:
    def __init__(self, queue_recv, queue_send, chunksize=10):
        self.conn_recv = RabbitMQConnection(queue_name=queue_recv)
        self.conn_send = RabbitMQConnection(queue_name=queue_send)
        self.chunksize = chunksize
        self.cmts_group_pid = {}

    def __callback(self, ch, method, properties, body):
        comments = json.loads(body)

        if "end" in comments:
            self.__send_grouped()
            # Send again end singnal
            self.conn_send.send(json.dumps(comments))
            return

        self.__parser(comments)

    def start(self):
        self.conn_recv.recv(self.__callback)
        
        self.conn_recv.close()
        self.conn_send.close()

    def __parser(self, comments):
        for c in comments:
            self.cmts_group_pid["post_id"] = self.cmts_group_pid.get(c["post_id"], [])
            self.cmts_group_pid["post_id"].append(c["sentiment"])

    def __send_grouped(self):
        # when client finish, have send all
        # send comments_grouped by chunks
        chunk = []
        for post_id, sentiments in self.cmts_group_pid.items():
            if len(chunk) == self.chunksize:
                self.conn_send.send(json.dump(chunk))
                chunk = []
            group = {
                "post_id": post_id,
                "sentiments": sentiments
            }
            chunk.append(group)