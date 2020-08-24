# -*- coding: UTF-8 -*-

import queue
from threading import Thread
from queue import Queue
from detector import *
from rejson import Client, Path

class myThread(Thread):  
    def __init__(self,rj,detector,fq):
        Thread.__init__(self)
        detectors = detector
        self.rj = rj
        self.detector = detector
        self.fq = fq

    def send_to_redis(self,json_name,json_value):
        print(json_name,json_value)
        self.rj.jsonarrappend(json_name, Path(".detect_result"), json_value)


    def run(self):
        while True:
            try:
                data = self.fq.get(timeout = 2)
                # 初始化json
                ret_json = self.detector.detect(data['image_path'])
                print(ret_json)
                if 'json_name' in data:
                    json_name = data['json_name']
                    self.send_to_redis(json_name,ret_json)
            
            except queue.Empty:
                print("Work End")
                break
            except Exception as e:
                print("Exception:",e)
                break


def update_fake_mask(frame):
    assert(len(frame.shape) == 3)
    mask = np.zeros((frame.shape[0],frame.shape[1]),frame.dtype)
    tmp_det = climb_detector()
    tmp_det.update_mask(mask)

if __name__ == "__main__":
    video_path = "/home/fudan/lyl/docker/fire/data/test.mp4"
    video_reader = cv2.VideoCapture(video_path)

    docker_num = 6

    #数据库连接
    rj = Client(host='localhost', port=6379, decode_responses=True)

    #检测器列表
    detector_num = docker_num
    detectors = [None] * detector_num
    detectors[0] = climb_detector()
    detectors[1] = violence_detector()
    detectors[2] = abnormal_detector()
    detectors[3] = firearm_detector()
    detectors[4] = count_detector()
    detectors[5] = fire_detector()

    #frame队列列表
    fqs = [None] * docker_num
    for idx in range(docker_num):
        fqs[idx] = queue.Queue(maxsize = 10)
    
    #线程列表
    threads = [None] * docker_num
    for idx in range(docker_num):
        threads[idx] = myThread(rj,detectors[idx], fqs[idx])

    
    # 为攀爬更新mask
    ret,frame = video_reader.read()
    update_fake_mask(frame)

    for frame_idx in range(100):
        ret,frame = video_reader.read()
        if not ret:
            break
        
        print(frame_idx, end= ":")

        #在redis中初始化json
        json_name = str(frame_idx)
        rj.jsonset(json_name, Path.rootPath(), {"detect_result":[]})

        if frame_idx % 10 == 0:
            image_path = "imgs/" + str(frame_idx) + ".jpg"
            cv2.imwrite(image_path,frame)
            data = {'image_path':image_path,'json_name':json_name}
            for idx in range(docker_num):
                fqs[idx].put(data)
        # else:
        #     data = {'image_path':image_path}
        #     fqs[2].put(data)
        
        if frame_idx == 20:
            for idx in range(docker_num):
                threads[idx].start()
            
            print("Thread start")

    
        
    
    
        
            
        
    

    