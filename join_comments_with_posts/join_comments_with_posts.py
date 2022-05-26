import signal
import logging
import pika

import json
from common.connection import Connection


class JoinCommentsWithPosts:
    def __init__(self, queue_recv_comments, queue_recv_post, queue_send_students, 
            queue_send_sentiments, chunksize, recv_workers, send_workers):
        self.conn_recv_pst = Connection(queue_name=queue_recv_post)
        self.conn_recv_cmt = Connection(queue_name=queue_recv_comments, conn=self.conn_recv_pst)

        self.conn_send_st = Connection(queue_name=queue_send_students, durable=True)
        self.conn_send_se = Connection(queue_name=queue_send_sentiments, durable=True)
        self.join_dict = {}
        self.chunksize = chunksize
        self.finish = {"posts": 0, "comments": 0}
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.recv_workers = recv_workers
        self.send_workers = send_workers

    def exit_gracefully(self, *args):
        self.conn_recv_cmt.close()
        self.conn_send_st.close()
        self.conn_send_se.close()

    def start(self):
        self.conn_recv_pst.recv(self.__callback_recv_posts, start_consuming=False)
        self.conn_recv_cmt.recv(self.__callback_recv_comments)
        self.exit_gracefully()

    def __callback_recv_comments(self, ch, method, properties, body):
        comments = json.loads(body)

        if self.__finish(my_key="comments", other_key="posts", readed=comments):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        self.__add_comments(comments)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def __callback_recv_posts(self, ch, method, properties, body):
        posts = json.loads(body)

        if self.__finish(my_key="posts", other_key="comments", readed=posts):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        self.__add_post(posts)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def __finish(self, my_key, other_key, readed):
        if "end" in readed:
            self.finish[my_key] += 1
            logging.info(f"[FINISH JOIN ALL?] {self.finish} | Workers: {self.recv_workers}")
            if self.finish[other_key] == self.recv_workers \
                and self.finish[my_key] == self.recv_workers:
                self.__send_join_data()
                # Send end msg to n workers
                for i in range(self.send_workers):
                    self.__send_data(readed)
            return True
        return False

    def __send_data(self, data):
        self.conn_send_st.send(json.dumps(data))
        self.conn_send_se.send(json.dumps(data))

    def __add_comments(self, list_comments):
        for c in list_comments:
            key = c["post_id"]
            # get or create dict with key=post_id
            self.join_dict[key] = self.join_dict.get(key, {})

            self.join_dict[key]["body"] = self.join_dict[key].get("body", [])
            self.join_dict[key]["sentiments"] = self.join_dict[key].get("sentiments", [])

            self.join_dict[key]["body"].append(c["body"])
            self.join_dict[key]["sentiments"].append(c["sentiment"])
        
    def __add_post(self, list_posts):
        for p in list_posts:
            key = p["post_id"]
            if key in self.join_dict:
                self.join_dict[key].update(p)
            else:
                self.join_dict[key] = p
                self.join_dict[key]["body"] = []
                self.join_dict[key]["sentiments"] = []

    def __send_join_data(self):
        chunk = []
        for post_id, post in self.join_dict.items():
            if not "url" in self.join_dict[post_id]:
                continue
            if len(chunk) == self.chunksize:
                self.__send_data(chunk)
                chunk = []
            
            chunk.append(post)

        # send last data in chunk
        if len(chunk) > 0:
            self.__send_data(chunk)

