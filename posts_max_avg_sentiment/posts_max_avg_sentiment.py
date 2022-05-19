import logging

import json
from common.rabbitmq_connection import RabbitMQConnection

class PostsMaxAvgSentiment:
    def __init__(self, queue_recv, queue_send):
        self.conn_recv = RabbitMQConnection(queue_name=queue_recv)
        self.conn_send = RabbitMQConnection(queue_name=queue_send)
        self.max_avg = {"url": None, "avg_sentiment": 0}

    def __callback(self, ch, method, properties, body):
        posts = json.loads(body)

        if "end" in posts:
            # Send only post with max avg sentiment
            logging.info(f"[POST MAX AVG SENTIMENT] {self.max_avg}")
            self.conn_send.send(json.dumps(self.max_avg["url"]))
            # send "end" msg
            # self.conn_send.send(json.dumps(posts))
            return

        self.__parser(posts)

    def start(self):
        self.conn_recv.recv(self.__callback)
        
        self.conn_recv.close()
        self.conn_send.close()

    def __parser(self, posts):
        for p in posts:
            if p["avg_sentiment"] > self.max_avg["avg_sentiment"]:
                self.max_avg = p


    def __download_image(self):
        import requests 
        import shutil

        image_url = self.max_avg["url"]
        filename = image_url.split("/")[-1]

        r = requests.get(image_url, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)
                
            print(f"[DOWNLOAD_IMAGE] Success {filename}")
        else:
            logging.error(f"[DOWNLOAD_IMAGE] Fail")