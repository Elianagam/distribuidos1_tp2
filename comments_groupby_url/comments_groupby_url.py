import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class CommentsGroupbyUrl:
    def __init__(self, queue_recv, queue_send, chunksize=10):
        self.conn_recv = RabbitMQConnection(exchange_name=queue_recv, bind=True)
        self.conn_send = RabbitMQConnection(queue_name=queue_send)
        self.chunksize = chunksize
        self.cmts_group_pid = {}

    def __callback(self, ch, method, properties, body):
        comments = json.loads(body)

        if "end" in comments:
            logging.info(f"[COMMENTS_GROUPBY_URL] END: {len(self.cmts_group_pid.items())}")

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
            if c["sentiment"] != '':
                # Filter comments with sentiment null
                key = c["url"]
                self.cmts_group_pid[key] = self.cmts_group_pid.get(key, [])
                stm = float(c["sentiment"])
                self.cmts_group_pid[key].append(stm)

    def __send_grouped(self):
        # when client finish, have send all
        # send comments_grouped by chunks
        chunk = []
        for url, sentiments in self.cmts_group_pid.items():
            if len(chunk) == self.chunksize:
                self.conn_send.send(json.dumps(chunk))
                chunk = []
            group = {
                "url": url,
                "sentiments": sentiments
            }
            chunk.append(group)

        if len(chunk) != 0:
            self.conn_send.send(json.dumps(chunk))
