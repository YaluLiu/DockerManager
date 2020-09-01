import json
import copy
import requests
import time
import os 

def speed_test(sec):
    if not hasattr(speed_test, 'start_time'):
        speed_test.start_time = time.time()
        cost_time = 0
    else:
        cost_time = time.time() - speed_test.start_time
    print("{} sec cost:{}".format(sec,cost_time))
    speed_test.start_time = time.time()

def check_threat_level(act_json):
    str_level = None
    if act_json["fire"]["status"]:
        str_level  = "high"
    elif act_json["guns"]["status"]:
        str_level = "high"
    elif act_json["fighting"]:
        str_level = "high"
    elif act_json["destroy_camera"]:
        str_level = "mid"
    elif act_json["intrusion"]["status"]:
        str_level = "mid"
    elif act_json["crowd_abnormal"]:
        str_level = "low"
    else:
        str_level = "no"
    
    act_json["threat_level"] = str_level

def merge_json(workers,act_json):
    for idx,worker in enumerate(workers):
        worker.merge_json(act_json)
    check_threat_level(act_json)

def get_default_json():
    if not hasattr(get_default_json, 'json_default'):
        with open("../config/format.json","r") as f:
            get_default_json.json_default = json.load(f)
    return copy.deepcopy(get_default_json.json_default)

def print_json(frame_idx,data):
    sec =  int(frame_idx / 24) - 2
    print("-"*8,sec," sec","-"*8)
    speed_test(sec)
    print(json.dumps(data, indent=4, sort_keys=True))
    

def push_json(data,url):
    try:
        r = requests.post(url, json=data)
        if r.status_code == 200:
            print(r.json())
        else:
            print(r.status_code)
    except Exception as e:
        pass

def find_videos_by_label(root_dir):
    labels = os.listdir(root_dir)
    ret_json = {}
    for label in labels:
        ret_json[label] = []
        label_video_dir = os.path.join(root_dir,label)
        for video in os.listdir(label_video_dir):
            video_path = os.path.join(label_video_dir,video)
            if os.path.isfile(video_path):
                ret_json[label].append(video_path)
            elif os.path.isdir(video_path):
                ret_json[label] = ""
    return ret_json


def find_all_videos(root_dir):
    g = os.walk(root_dir)  
    ret_list = []
    for path,dir_list,file_list in g: 
        for file_name in file_list:
            part = {}
            part["name"] = file_name
            part["path"] = os.path.join(path, file_name)
            ret_list.append(part)
    ret_json = {"videos":ret_list}
    return ret_json

# ===============TEST=====================================================

def test_find_videos_by_label():
    root_dir = "/home/fudan/lyl/test_video/"
    ret_json["crowd_action"] = find_videos_by_label(root_dir)
    print(json.dumps(ret_json, indent=4, sort_keys=True))


if __name__ == "__main__":
    video_list = find_all_videos("/home/fudan/lyl/test_video")
    print(len(video_list["videos"]))
    # print(video_list)
