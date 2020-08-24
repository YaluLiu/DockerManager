import cv2
import numpy as np
import json
import requests

# config_host = "192.168.200.233"
config_host = "localhost"

class detector(object):
    def __init__(self,host,port,api,cam_id = 0):
        self.host = config_host
        self.port = port
        self.api = api
        self.cam_id = cam_id
        self.url = "http://{}:{}/{}/{}".format(host,port, api, cam_id)
    def post_frame(self,frame):
        # cv2.imwrite("1.jpg",frame)
        frame_encoded = cv2.imencode(".jpg", frame)[1]
        Send_file = {'image': frame_encoded.tostring()}
        response = requests.post(self.url,files=Send_file)
        return response.json()
    
    def post_image(self,image_path):
        response = requests.post(self.url,files={'image': open(image_path, 'rb')})
        return response.json()

    def detect(self,input):
        if isinstance(input,str):
            return self.post_image(input)
        elif isinstance(input,np.ndarray):
            return self.post_frame(input)

#=============================7001===============================================================
class climb_detector(detector):
    def __init__(self):
        host = config_host
        port = 7001
        api = "api_detect_person"
        detector.__init__(self,host,port,api)
    def update_mask(self,mask):
        api = "api_save_mask"
        if len(mask.shape) == 3 and mask.shape[2] == 3:
            mask = mask[:,:,0]
        self.mask_url = "http://{}:{}/{}/{}".format(self.host,self.port, api, self.cam_id)
        frame_encoded = cv2.imencode(".jpg", mask)[1]
        Send_file = {'image': frame_encoded.tostring()}
        json = requests.post(self.mask_url,files=Send_file)
        return json.status_code == 200

    # def detect(self,frame): #{'climb_data': [[126, 168, 112, 202]]}
    #     return self.post_frame(frame)
    def get_state(self,response):
        return len(response["climb_data"]) > 0
#=============================7002===============================================================
class violence_detector(detector):
    def __init__(self):
        host = config_host
        port = 7002
        api = "api_detect_violence"
        detector.__init__(self,host,port,api)
    # def detect(self,frame): #{'FindFight': 'True'}
    #     json = self.post_frame(frame)
    #     return json
    def get_state(self,response):
        return response["FindFight"] == "True"
#=============================7003===============================================================
class abnormal_detector(detector):
    def __init__(self):
        host = config_host
        port = 7003
        api = "api_detect_crowd_abnormal"
        cam_id = 0
        self.reset_flow_url = "http://{}:{}/{}/{}".format(host,port, "api_reset_flow", cam_id)
        detector.__init__(self,host,port,api)
    # def detect(self,frame): #{'crowd_abnormal': False, 'destroy_camera': False}
    #     json = self.post_frame(frame)
    #     return json
    def reset_flow(self,frame): #{'crowd_abnormal': False, 'destroy_camera': False}
        frame_encoded = cv2.imencode(".jpg", frame)[1]
        Send_file = {'image': frame_encoded.tostring()}
        
        response = requests.post(self.reset_flow_url,files=Send_file)
        return response.json()
    def get_state(self,response):
        return response["crowd_abnormal"] or response["destroy_camera"]
#=============================7004===============================================================
class firearm_detector(detector):
    def __init__(self):
        host = config_host
        port = 7004
        api = "api_detect_firearm"
        detector.__init__(self,host,port,api)
    # def detect(self,frame): #{'guns': [[625, 579, 741, 710]]}
    #     json = self.post_frame(frame)
    #     return json
    def get_state(self,response):
        return len(response["guns"]) > 0
#=============================7005===============================================================
class count_detector(detector):
    def __init__(self):
        host = config_host
        port = 7005
        api = "api_crowd_count"
        detector.__init__(self,host,port,api)
    # def detect(self,frame):      # {'crowd_count':26.6123242}
    #     json = self.post_frame(frame)
    #     return json
    def get_state(self,response):
        return False
#=============================7006===============================================================
class fire_detector(detector):
    def __init__(self):
        host = config_host
        port = 7006
        api = "api_detect_fire"
        detector.__init__(self,host,port,api)
    # def detect(self,frame): #{'fire': {'area': [], 'status': 'yes'}}
    #     json = self.post_frame(frame)
    #     return json['fire']['status'] == 'yes'
    def get_state(self,response): #{'fire': {'area': [], 'status': 'yes'}}
        return response['fire']['status'] == 'yes'
#=============================7007===============================================================
class slowfast_detector(detector):
    def __init__(self):
        host = config_host
        port = 7007
        post_frame_api = "api_post_frame"
        detector.__init__(self,host,port,post_frame_api)
    def detect(self):
        interface = "api_detect_violence"
        port = 7007
        cam_id = 0
        url = "http://localhost:{}/{}/{}".format(port, interface, cam_id)
        response = requests.get(url)
        return response.json()
    def get_state(self,response):
        return response["fight"] == True
#=============================7008===============================================================
class alphapose_detector(detector):
    def __init__(self):
        host = config_host
        port = 7008
        post_frame_api = "api_detect_climb"
        detector.__init__(self,host,port,post_frame_api)
    def get_state(self,response):
        for idx in range(len(response)):
            if response[idx]["climb"] == True:
                return True
        return False
#=============================7009===============================================================
#=============================7010===============================================================
#=============================7011===============================================================
class crowd_action_detector(detector):
    def __init__(self):
        host = config_host
        port = 7011
        post_frame_api = "api_detect"
        detector.__init__(self,host,port,post_frame_api)
    def get_state(self,response):
        print(response)
#=============================7012===============================================================
class sleep_detector(detector):
    def __init__(self):
        host = config_host
        port = 7012
        post_frame_api = "api_detect_face"
        detector.__init__(self,host,port,post_frame_api)
    def get_state(self,response):
        pass
#=============================7013===============================================================
#=============================7014===============================================================
#=============================7015===============================================================

if __name__ == "__main__":
    video_path = "/home/fudan/lyl/video/sleep_eye.mp4"
    vc = cv2.VideoCapture(video_path)
    if not vc.isOpened():
        print("Video Error!")
    frame_idx = 0
    my_detector = sleep_detector()
    while True:
        ret,frame = vc.read()
        if not ret:
            break
            
        frame_idx += 1
        if frame_idx % 12 != 0:
            continue
        json = my_detector.detect(frame)
        print(json)
        


