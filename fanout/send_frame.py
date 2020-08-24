import pika
import json
import time
import os
import cv2

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# exchange=“自定义名字”
# type = 'fanout' 定义exchange发送类型，广播类型
# exchange_type type报错就使用这个
channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')


# for idx in range(100):
#     # 发送的内容
#     message = str(idx)

#     # routing_key 传入queue 由于是广播，不填
#     # 注:由于是广播类型所以不需要写queue。
#     channel.basic_publish(exchange='logs',
#                         routing_key='',
#                         body=message)
#     print(" [x] Sent %r" % message)

# connection.close()


if __name__ == "__main__":
    json_cfg = {}
    with open("../docker-config.json","r") as f:
        json_cfg = json.load(f)

    #init the threads
    # thread_num = len(json_cfg["docker_list"])
    # pool = ThreadPoolExecutor(thread_num * 3)

    # always use cam 6
    cam_id = 6

    url_1="rtsp://linye:linye123@192.168.200.253:554/Streaming/Channels/101"
    url_2="rtsp://linye:linye123@192.168.200.253:554/Streaming/Channels/301"
    # stream = cv2.VideoCapture(url_1)
    # ret, frame = stream.read()

    frame_idx = 0
    while True:
        frame_idx += 1
        img_path = "{}.jpg".format(frame_idx)
        # cv2.imwrite(img_path,frame)

        channel.basic_publish(exchange='logs',
                    routing_key='',
                    body=img_path)

        # ret, frame = stream.read()
        if frame_idx > 1000:
            break
    connection.close()




