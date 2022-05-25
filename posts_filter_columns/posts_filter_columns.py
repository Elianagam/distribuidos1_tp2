import logging

import json
from common.connection import Connection


class PostsFilterColumns:
    def __init__(self, queue_recv, queue_send_to_join, queue_send_to_avg):
        self.conn_recv = Connection(queue_name=queue_recv, durable=True)
        self.conn_send_join = Connection(queue_name=queue_send_to_join)
        self.conn_send_avg = Connection(queue_name=queue_send_to_avg)
        signal.signal(signal.SIGINT, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.conn_recv.close()
        self.conn_send_join.close()
        self.conn_send_avg.close()

    def start(self):
        self.conn_recv.recv(self.__callback)
        self.exit_gracefully()

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)

        if "end" in posts:
            logging.info(f"[POSTS_RECV] END")
            self.conn_send_join.send(end)
            self.conn_send_avg.send(end)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        self.__parser(posts)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def __parser(self, posts):
        posts_to_join = []
        posts_for_avg = []
        for p in posts:
            if self.__invalid_post(p):
                continue
            else:
                post = {"score": float(p["score"])}
                posts_for_avg.append(post)
                
                post["post_id"] = p["id"]
                post["url"] = p["url"]
                posts_to_join.append(post)

        self.conn_send_join.send(json.dumps(posts_to_join))
        self.conn_send_avg.send(json.dumps(posts_for_avg))
        

    def __invalid_post(self, post):
        # Dont send post without url or deleted
        meirls = ["meirl", "me irl", "me_irl"]

        return len(post["url"]) == '' or \
            post["selftext"] == "[deleted]" or \
            not post["title"].lower() in meirls
