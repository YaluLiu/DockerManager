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
    if check_all(data) == 0:
        return 
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
            "fighting":2
        }

def check_FU_threat(data):
    global threat_cfg

    if data["guns"]["status"]:
        return threat_cfg[cam_id]["gun"]
    if data["fire"]["status"]:
        return threat_cfg[cam_id]["fire"]
    if data["fighting"]:
        return threat_cfg[cam_id]["fighting"]
    return 0

def check_TJU_threat(TJU_datas):
    global threat_cfg
    ret = {"person":False,"car":False}
    for data in TJU_datas:
        ret[data["name"]] = True
        cam_id = data["equipment_id"]
    
    threat_level = 0
    if ret["person"] == False and ret["car"] == False:
        threat_level = 0
    elif ret["person"] == True and ret["car"] == False:
        threat_level = threat_cfg[cam_id]["person"]
    elif ret["person"] == True and ret["car"] == False:
        threat_level = threat_cfg[cam_id]["car"]
    else:
        threat_level = max(threat_cfg["person"], threat_cfg["person"])

    return threat_level
    
def check_all(data):
    TJU_level = check_TJU_threat(data["TJU"])
    FU_level = check_FU_threat(data["action_analysis_result"])
    max_level = max(TJU_level,FU_level)
    if TJU_level == 0:
        max_level = 0
    threat_str = ["no","low","mid","high"]
    data["action_analysis_result"]["threat_level"] = threat_str[max_level]
    return max_level

@app.route('/api_get_TJUdata/<id>' , methods=['POST'])
def api_get_TJUdata(id):
    global TJU_data
    cam_id = int(id)
    get_data = request.json
    TJU_data[cam_id] = get_data
    return jsonify("ok")

@app.route('/api_get_violence/<id>' , methods=['POST'])
def api_get_violence(id):
    global TJU_data
    cam_id = int(id)
    violence_data = request.json
    if len(TJU_data[cam_id]) == 0:
        violence_data["TJU"] = []
    else:
        violence_data["TJU"] = TJU_data[cam_id]
        assert(TJU_data[cam_id][0]["equipment_id"] == cam_id)
    # reset it to empty after use it
    TJU_data[cam_id] = []
    return jsonify("ok")

@app.route('/api_update_cfg/<id>' , methods=['POST'])
def api_update_cfg(id):
    global threat_cfg
    cam_id = int(id)
    cfg_data = request.json
    threat_cfg[cam_id] = cfg_data
    return jsonify("ok")


if __name__ == '__main__':
    threat_cfg = [None] * 100
    init_threat_cfg(threat_cfg)
    app.run(debug=False, host='0.0.0.0', port=6666,threaded=False)
