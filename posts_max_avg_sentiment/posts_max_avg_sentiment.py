import signal
import logging

import json
from common.connection import Connection


class PostsMaxAvgSentiment:
    def __init__(self, queue_recv, queue_send, recv_workers):
        self.conn_recv = Connection(queue_name=queue_recv)
        self.conn_send = Connection(queue_name=queue_send)
        self.max_avg = {"url": None, "avg_sentiment": 0}
        self.recv_workers = recv_workers
        self.end_recv = 0
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.conn_recv.close()
        self.conn_send.close()

    def start(self):
        self.conn_recv.recv(self.__callback)
        self.exit_gracefully()

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)

        if "end" in posts:
            self.end_recv += 1
            if self.end_recv == self.recv_workers:
                self.__end_recv(posts)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        else:
            self.__get_max_avg_sentiment(posts)
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def __end_recv(self, end_msg):
        # Send only post with max avg sentiment
        logging.info(f" --- [POST MAX AVG SENTIMENT] {self.max_avg}")
        self.conn_send.send(json.dumps(self.max_avg))

        if self.max_avg["url"] != None:
            download = self.__download_image()
            self.conn_send.send(json.dumps(download))

        self.conn_send.send(json.dumps(end_msg))

    def __get_max_avg_sentiment(self, posts):
        for p in posts:
            if p["avg_sentiment"] > self.max_avg["avg_sentiment"] \
                and p["url"][-3:] in ["png", "jpg"]:
                self.max_avg = p

    def __download_image(self):
        import requests 
        import shutil
        import base64

        image_url = self.max_avg["url"]
        filename = "data/max_avg_sentiment.jpg"

        r = requests.get(image_url, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)
            
            with open(filename, "rb") as image:
                b = bytearray(image.read())
                encoded = base64.b64encode(b)
                data = encoded.decode('ascii')  
                logging.info(f"[DOWNLOAD_IMAGE] Success {filename}")
                return {"image_bytes": data}
        else:
            logging.error(f"[DOWNLOAD_IMAGE] Fail")