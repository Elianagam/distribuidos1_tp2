import logging

import json
import re 
from common.connection import Connection


class CommentsFilterColumns:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = Connection(queue_name=queue_recv, durable=True)
        self.conn_send = Connection(queue_name=queue_send)


    def __callback(self, ch, method, properties, body):
        comments = json.loads(body)

        if len(comments) == 0:
            logging.info(f"[COMMENTS_RECV] END")
            self.conn_send.send(json.dumps({"end": True}))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        result = self.__parser(comments)
        self.conn_send.send(json.dumps(result))
        ch.basic_ack(delivery_tag=method.delivery_tag)

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

        logging.info(f"[COMMENTS FILTER] {len(filter_comments)}")
        return filter_comments

    def __invalid_body(self, comment):
        # Dont send comment without body or deleted
        return len(comment["body"]) == 0 or comment["body"] == "[removed]"

    def __get_post_id(self, comment):
        try:
            rgx = r'https://old.reddit.com/r/meirl/comments/([^/]+)/me.*'
            return re.findall(rgx, comment["permalink"])[0]
        except Exception as e:
            #logging.error(f"[FILTER_POST_ID] ERROR {e} ")
            return ''
