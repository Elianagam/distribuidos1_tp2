import logging
import signal
import csv
import json
from multiprocessing import Process
from common.connection import Connection

class Client:
    def __init__(self, comments_queue, posts_queue, 
        file_comments, file_posts, chunksize, send_workers,
        students_queue, avg_queue, image_queue):
        self.file_comments = file_comments
        self.file_posts = file_posts
        self.chunksize = chunksize
        self.send_workers = send_workers

        self.conn_posts = Connection(queue_name=posts_queue)
        self.conn_comments = Connection(queue_name=comments_queue, conn=self.conn_posts)

        self.comments_sender = Process(target=self.__send_comments())
        self.posts_sender = Process(target=self.__send_posts())
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.conn_posts.close()

    def start(self):
        logging.info(f"[CLIENT] started...")

        self.comments_sender.start()
        self.posts_sender.start()

        self.comments_sender.join()
        self.posts_sender.join()
        self.exit_gracefully()


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
        