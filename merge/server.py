import sys,os
sys.path.append(os.getcwd())

import cv2
import numpy as np
import json
import requests

#flask lib
import flask
from flask import Flask,url_for,render_template,request,redirect,send_file,jsonify

# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

TJU_data = [[]] * 100


def print_json(data):
    if len(data) == 0:
        return 
    print(json.dumps(data, indent=4, sort_keys=True))

def push_json(data):
    url = "http://192.168.50.100:8092/pushAnalysisInfo"
    try:
        r = requests.post(url, json=data)
        if r.status_code == 200:
            print(r.json())
        else:
            print(r.status_code)
    except Exception as e:
        print(e)

def init_threat_cfg(threat_cfg):
    for cam_id in range(100):
        threat_cfg[cam_id] = {
            "find_person":1,
            "find_car":1,
            "gun":3,
            "fire":3,
            "fighting":2,
            "crowd_behavior":1,
            "sleep":1,
            "intrusion":1,
            "destroy_camera": 1,
            "crowd_abnormal": 1,
        }

def check_FU_threat(data):
    global threat_cfg

    cam_id = data["camera_id"]
    cam_cfg = threat_cfg[cam_id]
    data = data["action_analysis_result"]

    # High
    if data["guns"]["status"]:
        return cam_cfg["gun"]
    if data["fire"]["status"]:
        return cam_cfg["fire"]
    
    # Mid
    if data["fighting"]:
        return cam_cfg["fighting"]

    # Low
    if data["intrusion"]["status"]:
        return cam_cfg["intrusion"]
    if data["sleep"]:
        return  cam_cfg["sleep"]
    if data["destroy_camera"]:
        return  cam_cfg["destroy_camera"]
    if data["crowd_abnormal"]:
        return  cam_cfg["crowd_abnormal"]
    if len(data["crowd_behavior"]) != 0:
        return  cam_cfg["crowd_behavior"]

    return 0

def check_TJU_threat(TJU_datas):
    if len(TJU_datas) == 0:
        return 0,False
    
    global threat_cfg
    ret = {"person":False,"car":False}
    for data in TJU_datas:
        ret[data["name"]] = True
        cam_id = data["equipment_id"]
    
    threat_level = 0
    find_nothing = False
    if ret["person"] == False and ret["car"] == False:
        threat_level = 0
        find_nothing = True
    elif ret["person"] == True and ret["car"] == False:
        threat_level = threat_cfg[cam_id]["person"]
    elif ret["person"] == True and ret["car"] == False:
        threat_level = threat_cfg[cam_id]["car"]
    else:
        threat_level = max(threat_cfg["person"], threat_cfg["person"])

    return threat_level,find_nothing
    
def check_all_threat(data):
    TJU_level,find_nothing = check_TJU_threat(data["TJU"])
    if len(data["TJU"]) != 0 and find_nothing:
        max_level = 0
    else:
        FU_level = check_FU_threat(data)
        max_level = max(TJU_level,FU_level)
    
    threat_str = ["no","low","mid","high"]
    data["action_analysis_result"]["threat_level"] = threat_str[max_level]
    return max_level

@app.route('/api_get_TJUdata/<id>', methods=['POST'])
def api_get_TJUdata(id):
    global TJU_data
    cam_id = int(id)
    get_data = request.json
    TJU_data[cam_id] = get_data
    return jsonify("ok")

@app.route('/api_get_FUdata/<id>', methods=['POST'])
def api_get_FUdata(id):
    global TJU_data
    merge_data = request.json
    cam_id = int(merge_data["camera_id"])
    
    if len(TJU_data[cam_id]) == 0:
        merge_data["TJU"] = []
    else:
        merge_data["TJU"] = TJU_data[cam_id]

    threat_level = check_all_threat(merge_data)
    if threat_level > 0:
        print_json(merge_data)
        # push_json(merge_data)

    # reset it to empty after use it
    TJU_data[cam_id] = []
    return jsonify("ok")

@app.route('/api_update_cfg' , methods=['POST'])
def api_update_cfg():
    global threat_cfg
    cfg_data = request.json
    cam_id = int(cfg_data["cam_id"])
    threat_cfg[cam_id]["find_person"] = cfg_data["find_person"]
    threat_cfg[cam_id]["find_car"] = cfg_data["find_car"]
    return jsonify("ok")


if __name__ == '__main__':
    threat_cfg = [None] * 100
    init_threat_cfg(threat_cfg)
    app.run(debug=False, host='0.0.0.0', port=6666,threaded=False)
