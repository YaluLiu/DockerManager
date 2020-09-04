# -*- coding: UTF-8 -*-
import json
import requests
import threading
import cv2
import os
from itertools import count
import argparse

parser = argparse.ArgumentParser(description='Detect Sleep')
# Datasets
parser.add_argument('-v', '--video', default='video/cjss1.mp4', type=str)
args = parser.parse_args()

#发送图片给检测服务器docker
def get_video_list():
    #init 
    #接口的名字
    port = 7009
    host  = "localhost"
    interface = "api_get_video_lst"
    url = "http://{}:{}/{}".format(host,port, interface)
    print(url)

    jsondata = requests.get(url)

    return jsondata.json()

def test_cam_list():
    #init 
    #接口的名字
    port = 7009
    host  = "localhost"
    interface = "api_get_cam_lst"
    url = "http://{}:{}/{}".format(host,port, interface)
    print(url)

    jsondata = requests.get(url)

    print(jsondata.json())

def get_cfg():
    port = 7009
    host  = "localhost"
    interface = "api_get_cfg"
    url = "http://{}:{}/{}".format(host,port, interface)
    print(url)

    jsondata = requests.get(url)

    return jsondata.json()

def get_running_state(start_cam_id):
    port = 7009
    host  = "localhost"
    interface = "api_get_state"
    url = "http://{}:{}/{}/{}".format(host,port, interface,start_cam_id)

    jsondata = requests.get(url)

    return jsondata.json()

def start_work(cfg_data):
    port = 7009
    host  = "localhost"
    interface = "api_start"
    url = "http://{}:{}/{}".format(host,port, interface)
    print(url)

    jsondata = requests.post(url,json=cfg_data)

    return jsondata.json()

def stop_work(cam_id):
    port = 7009
    host  = "localhost"
    interface = "api_stop"
    url = "http://{}:{}/{}/{}".format(host,port, interface,cam_id)

    jsondata = requests.post(url)

    return jsondata.json()

if __name__ == '__main__':
    start_cam_id = 0
    stop_work(start_cam_id)

    video_list = get_video_list()
    cfg = get_cfg()
    # print(cfg)
    # print(video_list)

    cfg["cam_id"] = start_cam_id
    cfg["docker_sleep"] = True
    cfg["video_path"] = "/home/fudan/lyl/test_video/crowd_action/zj/zj4.mp4"

    start_work(cfg)
    state = get_running_state(start_cam_id)
    print(state)


    

