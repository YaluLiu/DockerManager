import requests
import json
import random
from worker_group import worker_group

import flask
from flask import Flask,url_for,render_template,request,redirect,send_file,jsonify
from flask_cors import *

from utils import find_all_videos

app = Flask(__name__)
CORS(app, supports_credentials=True)


def update_cfg(cfg_data,cam_id):
    host = "localhost"
    port = 6666
    api = "api_update_cfg"
    # print(cfg_data)
    url = "http://{}:{}/{}/{}".format(host,port,api,cam_id)
    try:
        r = requests.post(url, json=cfg_data)
        if r.status_code == 200:
            print(r.json())
        else:
            print(r.status_code)
    except Exception as e:
        print(e)

@app.route('/api_get_state/<cam_id>' , methods=['GET'])
def api_get_state(cam_id):
    global cam_group
    cam_id = int(cam_id)
    running_state = True if cam_group[cam_id] is not None else False
    return jsonify({"active":running_state})

@app.route('/api_get_cam_lst' , methods=['GET'])
def api_get_cam_lst():
    json_path = "../config/cam_config.json"
    with open(json_path,"r") as f:
        cfg_data = json.load(f)
    return cfg_data

@app.route('/api_get_video_lst' , methods=['GET'])
def api_get_video_lst():
    video_dir = "/home/fudan/lyl/test_video"
    video_json = find_all_videos(video_dir)
    return jsonify(video_json)

@app.route('/api_get_cfg' , methods=['GET'])
def api_get_cfg():
    json_path = "../config/start_cfg.json"
    with open(json_path,"r") as f:
        cfg_data = json.load(f)
    return cfg_data

@app.route('/api_start' , methods=['POST'])
def api_start():
    global cam_group

    cfg = request.json
    print(json.dumps(cfg, indent=4, sort_keys=True))

    cam_id = int(cfg["cam_id"])
    if cam_group[cam_id] is not None:
        return jsonify({"active":True})
    
    # update threat cfg for merge server
    update_cfg(cfg,cam_id)

    json_path = "../config/start_cfg.json"
    with open(json_path,"w") as f:
        json.dump(cfg,f)

    p = worker_group()
    p.read_cfg(cfg)
    p.start()
    cam_group[cam_id] = p
    return jsonify({"active":True})

@app.route('/api_stop/<cam_id>' , methods=['POST'])
def api_stop(cam_id):
    global cam_group
    cam_id = int(cam_id)
    if cam_group[cam_id] is not None:
        cam_group[cam_id].shutdown()
        cam_group[cam_id] = None
    return jsonify({"active":False})
    

if __name__ == '__main__':
    cam_group = [None] * 50
    app.run(debug=False, host='0.0.0.0', port=7009,threaded=False)
