#_*_coding:utf-8_*_
import pika
from threading import Thread
import time
from functools import partial
import json


def callback(idx, ch, method, properties, body):


class myThread(Thread):
    def __init__(self,idx):
        Thread.__init__(self)
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.conn.channel()
        self.channel.exchange_declare(exchange='logs', exchange_type='fanout')
        self.idx = idx
        self.get_queue()
    def get_queue(self):
        # exclusive=True 唯一的
        # 不指定queue名字,rabbit会随机分配一个名字,
        # exclusive=True会在使用此queue的消费者断开后,自动将queue删除
        result = self.channel.queue_declare(queue='',exclusive=True)

        # # 随机取queue名字。
        self.queue = result.method.queue
        # channel.queue_bind 绑定exchange转发器
        # exchange=logs 由于rabbitMQ下不知一个exchange需要绑定。
        # self.queue 对列名
        self.channel.queue_bind(exchange='logs',
                        queue=self.queue)
        print("random queuename",self.queue)
    def run(self):
        print(' [*] Waiting for logs. To exit press CTRL+C')
        self.channel.basic_consume(queue=self.queue,
                            on_message_callback=partial(callback,self.idx),
                            auto_ack=True)
        self.channel.start_consuming()


if __name__ == "__main__":

    json_cfg = {}
    with open("../docker-config.json","r") as f:
        json_cfg = json.load(f)

    #init the threads
    threads_num = len(json_cfg["docker_list"])
    threads = [None] * threads_num

    for idx in range(threads_num):
        cfg  = json_cfg["docker_list"][idx]
        port = cfg["port"]
        name = cfg["image_name"]
        threads[idx] = myThread(idx)
        threads[idx].start()
    threads[idx].join()


