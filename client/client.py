import logging
import signal

import csv
import json
from multiprocessing import Process, Queue
from common.connection import Connection

class Client:
    def __init__(self, comments_queue, posts_queue, file_comments, file_posts, chunksize, send_workers):
        self.file_comments = file_comments
        self.file_posts = file_posts
        self.chunksize = chunksize
        self.send_workers = send_workers
        self.conn_posts = Connection(queue_name=posts_queue, durable=True)
        self.conn_comments = Connection(queue_name=comments_queue, durable=True)
        signal.signal(signal.SIGINT, self.exit_gracefully)

    def exit_gracefully(self, *args):
        # Send 
        for i in range(self.send_workers):
            self.conn_posts.close()
            self.conn_comments.close()

    def start(self):
        logging.info(f"[CLIENT] started...")
        comments_sender = Process(target=self.__send_comments())
        posts_sender = Process(target=self.__send_posts())

        comments_sender.start()
        comments_sender.join()

        posts_sender.start()
        posts_sender.join()

    def __send_comments(self):
        fields = ["type","id", "subreddit.id", "subreddit.name",
                  "subreddit.nsfw", "created_utc", "permalink", 
                  "body", "sentiment", "score"]

        self.__read(self.file_comments, self.conn_comments, fields)

    def __send_posts(self):
        fields = ["type", "id", "subreddit.id", "subreddit.name", 
                  "subreddit.nsfw", "created_utc", "permalink", 
                  "domain", "url", "selftext", "title", "score"]
        self.__read(self.file_posts, self.conn_posts, fields)

    def __read(self, file_name, conn, fields):
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
        for i in range(self.send_workers):
            conn.send(json.dumps({"end": True}))
        
        conn.close()
