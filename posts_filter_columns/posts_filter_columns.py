import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class PostsFilterColumns:
    def __init__(self, queue_recv, queue_send_to_join, queue_send_to_avg):
        self.conn_recv = RabbitMQConnection(queue_name=queue_recv)
        self.conn_send_join = RabbitMQConnection(queue_name=queue_send_to_join)
        self.conn_send_avg = RabbitMQConnection(queue_name=queue_send_to_avg)

    def start(self):
        self.conn_recv.recv(self.__callback)
        
        self.conn_recv.close()
        self.conn_send_join.close()
        self.conn_send_avg.close()

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)

        if len(posts) == 0:
            end = json.dumps({"end": True})
            self.conn_send_join.send(end)
            self.conn_send_avg.send(end)
            return
        
        posts_to_join, posts_for_avg = self.__parser(posts)
        logging.info(f"[POST FILTER] {len(posts_to_join)}")
        
        self.conn_send_join.send(json.dumps(posts_to_join))
        self.conn_send_avg.send(json.dumps(posts_for_avg))

    def __parser(self, posts):
        posts_to_join = []
        posts_for_avg = []
        for p in posts:
            if self.__invalid_post(p):
                continue
            else:
                if p["id"] == "tt5aas":
                    logging.info(f"[SPECIAL KEY] {self.__invalid_post(p)} {p}")
                post = {"score": float(p["score"])}
                posts_for_avg.append(post)
                
                post["post_id"] = p["id"]
                post["url"] = p["url"]
                posts_to_join.append(post)

        return posts_to_join, posts_for_avg
        

    def __invalid_post(self, post):
        # Dont send post without url or deleted
        meirls = ["meirl", "me irl", "me_irl"]

        return len(post["url"]) == '' or \
            post["selftext"] == "[deleted]" or \
            not post["title"].lower() in meirls
