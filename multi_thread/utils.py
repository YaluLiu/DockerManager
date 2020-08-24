import json
import copy
import requests
import time

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
