import numpy as numpy
import cv2
import time

import queue
from threading import Thread
from detector import *
from utils import frame_per_second

# 每秒一个json，如果画面中没有人，可以特殊处理
# json中无特殊情况，不push

class MyBasicThread(Thread):  
    def __init__(self):
        Thread.__init__(self)
        self.fq = queue.Queue(maxsize = 10)
        self.rq = queue.Queue(maxsize = 10)
        self.end = False
        self.name = None
    
    def solve_frame(self,data):
        pass

    def clean(self):
        while not self.fq.empty():
            self.fq.get()
        self.end = True
        

    def run(self):
        while not self.end:
            try:
                data = self.fq.get(timeout = 2)
                print(" "*self.id*10,end = " ")
                print("Thread{}:{}".format(self.id,data))
            except queue.Empty:
                continue
            except Exception as e:
                print("Exception:",e)
                break
        print(" "*self.id*10,end = " ")
        print("Thread end!",self.id)

#=============================7001===============================================================
def get_rect_from_mask(mask):
    (contours, hierarchy) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # cv2.drawContours(img,contours,-1,(0,0,255),3) 
    max_contour = None
    max_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            max_contour = contour
    (x,y,w,h) = cv2.boundingRect(max_contour)
    h = int(h/5)
    rect_top = (x,y,w,h*2)
    rect_bot = (x,y+3*h,w,h*2)
    return rect_top,rect_bot

def compute_overlap(rec_person,rec_mask):
    x1, y1, w1, h1 = rec_person
    x2, y2, w2, h2 = rec_mask
    if(x1>x2+w2):
        return 0
    if(y1>y2+h2):
        return 0
    if(x1+w1<x2):
        return 0
    if(y1+h1<y2):
        return 0
    colInt = abs(min(x1 +w1 ,x2+w2) - max(x1, x2))
    rowInt = abs(min(y1 + h1, y2 +h2) - max(y1, y2))
    overlap_area = colInt * rowInt
    area = w1*h1
    overlap_rate = round(overlap_area / area,2)
    return overlap_rate

def check_climb(rect,rect_top,rect_bot):
    overlap_top = compute_overlap(rect,rect_top) > 0
    overlap_bot = compute_overlap(rect,rect_bot) > 0
    is_jump = rect[1] + rect[3] < (rect_bot[1] + rect_bot[3])
    is_climb = overlap_top and is_jump
    return is_climb

class climb_worker():
    def __init__(self,mask_path=None):
        self.detector = climb_detector()
        self.rq = queue.Queue(maxsize = 10)
        self.mask = None
        self.set_mask(mask_path)
        self.name = "climb"

    def start(self):
        pass
    def clean(self):
        pass

    def set_mask(self,mask_path):
        if mask_path is None:
            self.mask = None
        else:
            mask = cv2.imread(mask_path)
            if mask.shape[0] >= 1080:
                h = int(mask.shape[0]/4)
                w = int(mask.shape[1]/4)
                dim = (w,h)
                mask = cv2.resize(mask, dim, interpolation = cv2.INTER_AREA)
            mask = mask[:,:,0]
            self.rect_top,self.rect_bot = get_rect_from_mask(mask)
            self.mask = mask

    def update_mask(self,frame):
        if self.mask is None:
            self.mask = np.zeros((frame.shape[0],frame.shape[1]),frame.dtype)
        if self.mask.shape[0] != frame.shape[0]:
            h = int(frame.shape[0])
            w = int(frame.shape[1])
            dim = (w,h)
            self.mask = cv2.resize(self.mask, dim, interpolation = cv2.INTER_AREA)
        tmp_det = climb_detector()
        tmp_det.update_mask(self.mask)
    
    def merge_json(self,act_json):
        response = self.rq.get()
        act_json["intrusion"]["area"] = response["climb_data"]
        act_json["intrusion"]["status"] = len(act_json["intrusion"]["area"]) > 0

    def make_response(self,response):
        result = {"climb_data":[]}
        for idx in range(len(response)):
            rect_person = response[idx]
            is_climb = check_climb(rect_person,self.rect_top,self.rect_bot)
            if is_climb:
                result["climb_data"].append(rect_person)
        return result
            
            


    def solve_frame(self,data):
        frame_idx = data["frame_idx"]
        # if frame_idx == 1:
        #     self.update_mask(data["frame"])
        # if frame_idx % frame_per_second == frame_per_second//2:
        #     response = self.detector.detect(data["frame"])
        #     data["person_num"] = len(response)
        #     response = self.make_response(response)
        #     if len(response["climb_data"]) > 0:
        #         self.pre_climb = True
        
        if frame_idx % frame_per_second == 1:
            response = self.detector.detect(data["frame"])
            data["person_num"] = len(response)
            response = self.make_response(response)
            self.rq.put(response)

#=============================7002===============================================================
#=============================7003===============================================================
#post every frame
class abnormal_worker(MyBasicThread):
    def __init__(self):
        MyBasicThread.__init__(self)
        self.detector = abnormal_detector()
        self.name = "abnormal"

    def merge_json(self,act_json):
        response = self.rq.get()
        act_json["destroy_camera"] = response["destroy_camera"]
        act_json["crowd_abnormal"] = response["crowd_abnormal"]

    def solve_frame(self,data):
        # if switch video, reset flow on the first frame of new video
        if data["frame_idx"] == 1:
            ret = self.detector.reset_flow(data["frame"])
            #print("reset_flow:",ret)
        # workon every frame
        self.detector.detect(data["frame"])
        if data["frame_idx"] % frame_per_second == 1:
            self.fq.put(data)

    def run(self):
        while not self.end:
            try:
                data = self.fq.get(timeout = 2)
                response = self.detector.detect(data["frame"])
                if data["person_num"] < 4:
                    response["crowd_abnormal"] = False
                self.rq.put(response)

            except queue.Empty:
                continue
            except Exception as e:
                print("abnormal Exception:",e)
                continue

#=============================7004===============================================================
class firearm_worker(MyBasicThread):
    def __init__(self):
        MyBasicThread.__init__(self)
        self.detector = firearm_detector()
        # detect more frames one sec to make better detection effect
        self.pre_exist_gun = False
        self.name = "firearm"

    def merge_json(self,act_json):
        response = self.rq.get()
        data = response["guns"]
        act_json["guns"]["area"] = []
        for idx_gun in range(len(data)):
            x0,y0,x1,y1,score = data[idx_gun]
            # score of confidence,if it's gun
            if score < 0.95:
                continue
            cur_gun = [int(x0),int(y0),int(x1),int(y1)]
            act_json["guns"]["area"].append(cur_gun)
        # not len(data)
        act_json["guns"]["status"] = len(act_json["guns"]["area"]) > 0

    def solve_frame(self,data):
        if data["frame_idx"] % frame_per_second == 1:
            self.fq.put(data)

    def run(self):
        while not self.end:
            try:
                data = self.fq.get(timeout = 2)
                response = self.detector.detect(data["frame"])
                self.rq.put(response)

            except queue.Empty:
                continue
            except Exception as e:
                print("firearm_worker Exception:",e)
                continue
#=============================7005===============================================================
class count_worker(MyBasicThread):
    def __init__(self):
        MyBasicThread.__init__(self)
        self.detector = count_detector()
        self.name = "crowd_count"

    def merge_json(self,act_json):
        response = self.rq.get()
        act_json["crowd_number"] = response["crowd_count"]

    def solve_frame(self,data):
        if data["frame_idx"] % frame_per_second == 1:
            self.fq.put(data)

    def run(self):
        while not self.end:
            try:
                data = self.fq.get(timeout = 2)
                response = self.detector.detect(data["frame"])
                if data["person_num"] <= 10:
                    response["crowd_count"] = data["person_num"]
                self.rq.put(response)

            except queue.Empty:
                continue
            except Exception as e:
                print("count_worker Exception:",e)
                continue
#=============================7006===============================================================
class fire_worker(MyBasicThread):
    def __init__(self):
        MyBasicThread.__init__(self)
        self.detector = fire_detector()
        self.name = "fire"

    def merge_json(self,act_json):
        response = self.rq.get()
        act_json["fire"]["area"] = response["fire"]["area"]
        act_json["fire"]["status"] = response["fire"]["status"] == 'yes'

    def solve_frame(self,data):
        if data["frame_idx"] % frame_per_second == 1:
            self.fq.put(data)

    def run(self):
        while not self.end:
            try:
                data = self.fq.get(timeout = 2)
                response = self.detector.detect(data["frame"])
                self.rq.put(response)

            except queue.Empty:
                continue
            except Exception as e:
                print("fire_worker Exception:",e)
                continue
#=============================7007===============================================================
#post every two frame
#post_frame when 
class slowfast_worker(MyBasicThread):
    def __init__(self):
        MyBasicThread.__init__(self)
        self.detector = slowfast_detector()
        self.is_fight = False
        self.name = "slowfast"

    def merge_json(self,act_json):
        act_json["fighting"] = self.is_fight

    def solve_frame(self,data):
        # 3s detect once
        if data["frame_idx"] % 72 == 0:
            self.fq.put(data)
        elif data["frame_idx"] % 2 == 1:
            self.detector.post_frame(data["frame"])

    def run(self):
        while not self.end:
            try:
                data = self.fq.get(timeout = 2)
                if data["person_num"] > 0:
                    response = self.detector.detect()
                    self.is_fight = response["fight"]
                else:
                    self.is_fight = False

            except queue.Empty:
                continue
            except Exception as e:
                print("slowfast_worker Exception:",e)
                continue
#=============================7008===============================================================
class alphapose_worker():
    def __init__(self,flag_detect_climb = False):
        self.detector = alphapose_detector()
        self.rq = queue.Queue(maxsize = 10)
        # self.mask = None
        # self.set_mask(mask_path)
        self.only_detect_person = not flag_detect_climb
        self.name = "alphapose"

    def start(self):
        pass
    def clean(self):
        pass

    def set_mask(self,mask_path):
        if mask_path is None:
            self.mask = None
        else:
            mask = cv2.imread(mask_path)
            if mask.shape[0] >= 1080:
                h = int(mask.shape[0]/4)
                w = int(mask.shape[1]/4)
                dim = (w,h)
                mask = cv2.resize(mask, dim, interpolation = cv2.INTER_AREA)
            mask = mask[:,:,0]
            self.rect_top,self.rect_bot = get_rect_from_mask(mask)
            self.mask = mask

    def update_mask(self,frame):
        if self.mask is None:
            self.mask = np.zeros((frame.shape[0],frame.shape[1]),frame.dtype)
        if self.mask.shape[0] != frame.shape[0]:
            h = int(frame.shape[0])
            w = int(frame.shape[1])
            dim = (w,h)
            self.mask = cv2.resize(self.mask, dim, interpolation = cv2.INTER_AREA)

    def merge_json(self,act_json):
        response = self.rq.get()

        if self.only_detect_person:
            act_json["intrusion"]["area"] = []
            act_json["intrusion"]["status"] = False
        else:
            act_json["intrusion"]["area"] = response["climb_data"]
            act_json["intrusion"]["status"] = len(act_json["intrusion"]["area"]) > 0

    def make_response(self,response):
        # for idx in range(len(response)):
        #     print(response[idx])
        result = {"climb_data":[]}
        
        for idx in range(len(response)):
            score = response[idx]["score"]
            rect_person = response[idx]["box"]
            is_climb = response[idx]["climb"]
            if is_climb:
                result["climb_data"].append(rect_person)
        return result

    def solve_frame(self,data):
        frame_idx = data["frame_idx"]
        
        if frame_idx % frame_per_second == 1:
            response = self.detector.detect(data["frame"])
            data["person_num"] = len(response)
            response = self.make_response(response)
            self.rq.put(response)
#=============================7011===============================================================
class crowd_action_worker(MyBasicThread):
    def __init__(self):
        MyBasicThread.__init__(self)
        self.detector = crowd_action_detector()
        self.name = "crowd_behavior"

    def merge_json(self,act_json):
        response = self.rq.get()
        # print(type(response))
        act_json["crowd_behavior"] = response


    def solve_frame(self,data):
        if data["frame_idx"] % frame_per_second == 1:
            self.fq.put(data)

    def run(self):
        while not self.end:
            try:
                data = self.fq.get(timeout = 2)
                response = self.detector.detect(data["frame"])
                self.rq.put(response)

            except queue.Empty:
                continue
            except Exception as e:
                print("abnormal Exception:",e)
                continue
#=============================7012===============================================================
class sleep_worker(MyBasicThread):
    def __init__(self):
        MyBasicThread.__init__(self)
        self.detector = sleep_detector()
        self.name = "sleep"

    def merge_json(self,act_json):
        eye_aspect_ratio = 0

        frame_num = self.rq.qsize()
        while not self.rq.empty():
            response = self.rq.get()
            if response['find_face']:
                eye_aspect_ratio += response['Lear'] + response['Rear']
            else:
                eye_aspect_ratio += 0.25

        if frame_num == 0:
            act_json["sleep"] = False
        elif eye_aspect_ratio/frame_num < 0.23:
            act_json["sleep"] = True
        else:
            act_json["sleep"] = False

    def solve_frame(self,data):
        if data["frame_idx"] % frame_per_second == 1:
            self.fq.put(data)

    def run(self):
        while not self.end:
            try:
                data = self.fq.get(timeout = 2)
                response = self.detector.detect(data["frame"])
                self.rq.put(response)

            except queue.Empty:
                continue
            except Exception as e:
                print("abnormal Exception:",e)
                continue
