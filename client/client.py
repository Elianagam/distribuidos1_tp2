import logging

import csv
import json
from multiprocessing import Process, Queue
from common.rabbitmq_connection import RabbitMQConnection

class Client:
    def __init__(self, comments_queue, posts_queue, file_comments, file_posts, chunksize=10):
        self.comments_queue = comments_queue
        self.posts_queue = posts_queue
        self.file_comments = file_comments
        self.file_posts = file_posts
        self.chunksize = chunksize        

    def start(self):
        comments_sender = Process(target=self.__send_comments())
        #posts_sender = Process(target=self.__send_posts())

        comments_sender.start()
        comments_sender.join()

        #posts_sender.start()
        #posts_sender.join()
        logging.info(f"Client started...")

    def __send_comments(self):
        fields = ["type","id", "subreddit.id", "subreddit.name",
                  "subreddit.nsfw", "created_utc", "permalink", 
                  "body", "sentiment", "score"]
        self.__read(self.file_comments, self.comments_queue, fields)

    def __send_posts(self):
        fields = ["type", "id", "subreddit.id", "subreddit.name", 
                  "subreddit.nsfw", "created_utc", "permalink", 
                  "domain", "url", "selftext", "title", "score"]
        self.__read(self.file_posts, self.posts_queue, fields)

    def __read(self, file_name, queue_name, fields):
        conn = RabbitMQConnection(queue_name)

        with open(file_name, mode='r') as csv_file:
            reader = csv.DictReader(csv_file)
            chunk = []
            for i, line in enumerate(reader):
                if (i % self.chunksize == 0 and i > 0):
                    conn.send(json.dumps(chunk))
                    chunk = []
                chunk.append(line)
            
            if len(chunk) != 0:
                conn.send(json.dumps(chunk))

        # send empty when finish
        conn.send(json.dumps({}))
        
        conn.close()
