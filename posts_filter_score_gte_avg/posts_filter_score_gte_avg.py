import logging

import json
from common.connection import Connection


class PostsFilterScoreGteAvg:
    def __init__(self, queue_recv_avg, queue_recv_students, queue_send, chunksize=10):
        self.conn_recv_students = Connection(queue_name=queue_recv_students)
        self.conn_recv_avg = Connection(exchange_name=queue_recv_avg, bind=True, conn=self.conn_recv_students)
        self.conn_send = Connection(queue_name=queue_send)
        self.avg_score = None
        self.arrived_early = []
        self.chunksize = chunksize

    def __callback_students(self, ch, method, properties, body):
        posts = json.loads(body)

        if "end" in posts:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        if self.avg_score != None:
            # TODO NOTHING UNTIL AVG != None
            self.__parser(posts)
        else:
            logging.info(f"[EARLY ARRIVE] {len(posts)}")
            self.arrived_early.append([p for p in posts])
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def __callback_avg(self, ch, method, properties, body):
        avg = json.loads(body)

        if "end" in avg:
            logging.info(f"[AVG END] {self.avg_score}")
            self.__send_arrive_early()
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        self.avg_score = float(avg["posts_score_avg"])
        ch.basic_ack(delivery_tag=method.delivery_tag)


    def start(self):
        self.conn_recv_avg.recv(self.__callback_avg, start_consuming=False)
        self.conn_recv_students.recv(self.__callback_students)
        
        self.conn_recv_avg.close()
        self.conn_recv_students.close()
        self.conn_send.close()

    def __parser(self, posts):
        list_posts = []
        for p in posts:
            logging.info(f"[STUDENT INFO] {p}")
            if float(p["score"]) >= self.avg_score:
                list_posts.append({"url": p["url"]}
                )
        if len(list_posts) != 0:
            logging.info(f" --- [STUDENTS MAX SCORE] {list_posts}")
            self.conn_send.send(json.dumps(list_posts))

    def __send_arrive_early(self):
        n = self.chunksize
        lst = self.arrived_early
        chunks = [lst[i:i + n] for i in range(0, len(lst), n)]
        for chunk in chunks:
            self.__parser(chunk)
