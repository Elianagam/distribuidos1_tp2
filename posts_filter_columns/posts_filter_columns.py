import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class PostsFilterColumns:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = RabbitMQConnection(queue_name=queue_recv)
        self.conn_send = RabbitMQConnection(exchange_name=queue_send)

    def start(self):
        self.conn_recv.recv(self.__callback)
        
        self.conn_recv.close()
        self.conn_send.close()

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)
        result = self.__parser(posts)
        self.conn_send.send(json.dumps(result))

    def __parser(self, posts):
        list_posts = []
        for p in posts:
            if self.__invalid_post(p): continue
            
            post = {
                "id": p["id"],
                "url": p["url"],
                "score": p["score"]
            }
            list_posts.append(post)

        logging.info(f"[POST FILTER] {len(list_posts)}")
        return list_posts

    def __invalid_post(self, post):
        # Dont send post without url or deleted
        meirls = ["meirl", "me irl", "me_irl"]

        return len(post["url"]) == 0 or \
            post["selftext"] == "[deleted]" or \
            not post["title"].lower() in meirls
