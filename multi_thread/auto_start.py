import requests
import json
import random
from worker_group import worker_group

import flask
from flask import Flask,url_for,render_template,request,redirect,send_file,jsonify
from flask_cors import *

app = Flask(__name__)
CORS(app, supports_credentials=True)


def update_cfg(cfg_data,cam_id):
    host = "localhost"
    port = 6666
    api = "api_update_cfg"
    url = "http://{}:{}/{}/{}".format(host,port,api,cam_id)
    try:
        r = requests.post(url, json=cfg_data)
        if r.status_code == 200:
            print(r.json())
        else:
            print(r.status_code)
    except Exception as e:
        print(e)


@app.route('/api_get_info/<cam_id>' , methods=['GET'])
def api_get_info(cam_id):
    global cam_group
    cam_id = int(cam_id)
    if cam_group[cam_id] is None:
        is_running = False
    else:
        is_running = True

    ret = {"is_running":is_running}
    return jsonify(ret)

@app.route('/api_get_cam_lst' , methods=['GET'])
def api_get_cam_lst():
    json_path = "../config/cam_config.json"
    with open(json_path,"r") as f:
        cfg_data = json.load(f)
    # print("cam_list:",cfg_data)
    return cfg_data

@app.route('/api_start/<cam_id>' , methods=['POST'])
def api_start(cam_id):
    global cam_group

    cam_id = int(cam_id)
    if cam_group[cam_id] is not None:
        return jsonify("Have already started!")
    
    cfg = request.json
    # update threat cfg for merge server
    update_cfg(cfg,cam_id)
    print(json.dumps(cfg, indent=4, sort_keys=True))
    
    p = worker_group()
    p.read_cfg(cfg)
    p.start()
    cam_group[cam_id] = p
    return jsonify("ok")

@app.route('/api_stop/<cam_id>' , methods=['POST'])
def api_stop(cam_id):
    global cam_group
    cam_id = int(cam_id)
    cam_group[cam_id].shutdown()
    cam_group[cam_id] = None
    return jsonify("ok")
    

if __name__ == '__main__':
    cam_group = [None] * 50
    app.run(debug=False, host='0.0.0.0', port=7009,threaded=False)
