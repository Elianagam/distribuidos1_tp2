import logging
import signal

import json
from common.connection import Connection

class PostsAvgSentiment:
    def __init__(self, queue_recv, queue_send):
        #self.conn_recv = Connection(exchange_name=queue_recv, bind=True)
        self.conn_recv = Connection(queue_name=queue_recv, durable=True)
        self.conn_send = Connection(queue_name=queue_send)
        signal.signal(signal.SIGINT, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.conn_recv.close()
        self.conn_send.close()

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)

        if "end" in posts:
            self.conn_send.send(json.dumps(posts))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        result = self.__parser(posts)
        self.conn_send.send(json.dumps(result))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self.conn_recv.recv(self.__callback)
        self.exit_gracefully()

    def __parser(self, posts):
        list_posts = []
        for p in posts:
            sentiments = [float(v) for v in p["sentiments"] if (v != '' and v != None)]
            if len(sentiments) == 0: continue
            post_stm_avg = sum(sentiments) / len(sentiments)
            p_stm = {
                "url": p["url"],
                "avg_sentiment": post_stm_avg
            }
            list_posts.append(p_stm)
        return list_posts

