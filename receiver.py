import logging

import csv
import json
from multiprocessing import Process, Queue
from rabbitmq_connection import RabbitMQConnection


class Receiver:
    def __init__(self, queue_name):
        self.queue_name = queue_name

    def callback(self, ch, method, properties, body):
        lines = json.loads(body)

        print(f"[LEN] {len(lines)}")
        #for line in lines[]:
        if lines:
            print(f"[x] Received {lines[0]['id']}")
            print(f"[x] Received {lines[-1]['id']}")
        else:
            return

    def recv(self):
        conn = RabbitMQConnection(self.queue_name)
        conn.recv(self.callback)
        conn.close()
