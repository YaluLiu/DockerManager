import cv2
import json

#frame_idx must start with 1

class video_reader:
    def __init__(self,video_path):
        # self.video_path = "/home/fudan/lyl/video/climb_2.MTS"
        self.video_path = video_path
        self.frame_idx = 0
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print("Video or Camera is Error!")
    
    def isOpened(self):
        return self.cap.isOpened()
        

    def get_frame(self):
        ret,frame = self.cap.read()
        if ret:
            self.frame_idx += 1
            if frame.shape[0] >= 1080:
                h = int(frame.shape[0]/4)
                w = int(frame.shape[1]/4)
                dim = (w,h)
                frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
            return {"frame":frame,"frame_idx":self.frame_idx,"person_num":0}
        else:
            print("Video read End!")
            return None



class cam_reader:
    def __init__(self,url):
        self.video_path = url
        self.frame_idx = 0
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print("Video or Camera is Error!")

    # def get_cam_url(self):
    #     json_path = "../config/cam_config.json"
    #     with open(json_path,"r") as f:
    #         cfg_data = json.load(f)
    #     return cfg_data[str(self.cam_id)]

    def get_frame(self):
        while True:
            ret,frame = self.cap.read()
            if not ret:
                print("Read Steam make Error,Restart Camera")
                self.cap.release()
                self.cap = cv2.VideoCapture(self.video_path)
                continue
            else:
                self.frame_idx += 1
                if frame.shape[0] >= 1080:
                    h = int(frame.shape[0]/4)
                    w = int(frame.shape[1]/4)
                    dim = (w,h)
                    frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
                return {"frame":frame,"frame_idx":self.frame_idx,"person_num":0}
