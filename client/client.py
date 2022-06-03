import logging
import signal
import csv
import json
from multiprocessing import Process
from common.connection import Connection

SINK_TO_RECV = 3

class Client:
    def __init__(self, comments_queue, posts_queue, file_comments, 
        file_posts, chunksize, send_workers_comments, send_workers_posts,
        students_queue, avg_queue, image_queue):
        self.file_comments = file_comments
        self.file_posts = file_posts
        self.chunksize = chunksize
        self.send_workers_comments = send_workers_comments
        self.send_workers_posts = send_workers_posts

        self.students_recved = []
        self.count_end = 0
        self.conn_posts = Connection(queue_name=posts_queue)
        self.conn_comments = Connection(queue_name=comments_queue, conn=self.conn_posts)

        self.conn_recv_students = Connection(queue_name=students_queue, conn=self.conn_posts)
        self.conn_recv_avg = Connection(exchange_name=avg_queue, bind=True, conn=self.conn_posts)
        self.conn_recv_image = Connection(queue_name=image_queue, conn=self.conn_posts)
        
        self.comments_sender = Process(target=self.__send_comments())
        self.posts_sender = Process(target=self.__send_posts())
        self.sink_recver = Process(target=self.__recv_sinks())
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        logging.info(f"CLOSE RECV CLIENT")
        self.conn_posts.close()

    def start(self):
        logging.info(f"[CLIENT] started...")

        self.comments_sender.start()
        self.posts_sender.start()
        self.sink_recver.start()

        self.comments_sender.join()
        self.posts_sender.join()
        self.sink_recver.join()
        
    def __recv_sinks(self):
        self.conn_recv_students.recv(self.__callback_students, start_consuming=False)
        self.conn_recv_avg.recv(self.__callback, start_consuming=False)
        self.conn_recv_image.recv(self.__callback)
        

    def __callback_students(self, ch, method, properties, body):
        sink_recv = json.loads(body)
        
        if "end" in sink_recv:
            self.count_end += 1
            return
        for student in sink_recv:
            logging.info(f"* * * [CLIENT RECV END STUDENT] {sink_recv}")
            self.students_recved.append(student)
        

    def __callback(self, ch, method, properties, body):
        sink_recv = json.loads(body)
        if "end" in sink_recv:
            self.count_end += 1
            return
        else:
            logging.info(f"* * * [CLIENT RECV] {sink_recv.keys()}")

    def __send_comments(self):
        fields = ["type","id", "subreddit.id", "subreddit.name",
                  "subreddit.nsfw", "created_utc", "permalink", 
                  "body", "sentiment", "score"]

        self.__read(self.file_comments, self.conn_comments, fields)
        self.__send_end(self.conn_comments, self.send_workers_comments)

    def __send_posts(self):
        fields = ["type", "id", "subreddit.id", "subreddit.name", 
                  "subreddit.nsfw", "created_utc", "permalink", 
                  "domain", "url", "selftext", "title", "score"]
        self.__read(self.file_posts, self.conn_posts, fields)
        self.__send_end(self.conn_posts, self.send_workers_posts)

    def __send_end(self, conn, send_workers):
        for i in range(send_workers):
            conn.send(json.dumps({"end": True}))

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
        