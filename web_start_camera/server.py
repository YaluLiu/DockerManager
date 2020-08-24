import json
import flask
from flask import Flask,url_for,render_template,request,redirect,send_file,jsonify
from flask_cors import *

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/start_camera' , methods=['GET'])
def start_camera():
    return render_template('index.html')

# http://192.168.200.233:7010/start_camera
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=7010,threaded=False)
