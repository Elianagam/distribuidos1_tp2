import signal
import logging

import json
import re 
from common.connection import Connection


class CommentsFilterColumns:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = Connection(queue_name=queue_recv, durable=True)
        self.conn_send = Connection(queue_name=queue_send, durable=True)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.conn_recv.close()
        self.conn_send.close()

    def start(self):
        self.conn_recv.recv(self.__callback)
        self.exit_gracefully()

    def __callback(self, ch, method, properties, body):
        comments = json.loads(body)

        if "end" in comments:
            logging.info(f"[COMMENTS_RECV] END")
            self.conn_send.send(json.dumps(comments))
            return

        logging.info(f"[COMMENT FILTER RECV] {len(comments)}")
        filter_comments = self.__parser(comments)
        self.conn_send.send(json.dumps(filter_comments))

    def __parser(self, comments):
        filter_comments = []
        for comment in comments:
            if self.__invalid_body(comment): continue
            comment_new = {
                "post_id": self.__get_post_id(comment),
                "body": comment["body"],
                "sentiment": comment["sentiment"],
            }
            filter_comments.append(comment_new)

        return filter_comments

    def __invalid_body(self, comment):
        return len(comment["body"]) == 0 or comment["body"] == "[removed]"

    def __get_post_id(self, comment):
        try:
            rgx = r'https://old.reddit.com/r/meirl/comments/([^/]+)/me.*'
            return re.findall(rgx, comment["permalink"])[0]
        except Exception as e:
            return ''
