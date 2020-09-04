import multiprocessing
import time
from my_workers import climb_worker,alphapose_worker
from my_workers import abnormal_worker,firearm_worker
from my_workers import count_worker,fire_worker,slowfast_worker
from my_workers import sleep_worker,crowd_action_worker
from my_reader import video_reader,cam_reader
from utils import *
 
class worker_group(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()

    def read_cfg(self,cfg):
        # id of camera,if use local video it's zero
        self.cam_id  = cfg["cam_id"]

        # test function by local video
        self.use_test_video = self.cam_id == 0
        self.video_path = cfg["video_path"]

        # test function by online-camera
        self.cam_url = cfg["cam_url"]



        # set url of server
        self.merge_url = 'http://{}:6666/api_get_FUdata/{}'.format("localhost",self.cam_id)
        # if push to server
        self.flag_push = True
        # if print json to console
        self.flag_print = True

        self.workers = []

        flag_need_person_detect = False

        if cfg["docker_climb"]:
            self.workers.append(alphapose_worker(cfg["docker_climb"]))
        
        if cfg["docker_abnormal"]:
            self.workers.append(abnormal_worker())
            flag_need_person_detect = True

        if cfg["docker_fight"]:
            self.workers.append(slowfast_worker())
            flag_need_person_detect = True

        if cfg["docker_count"]:
            self.workers.append(count_worker())
            flag_need_person_detect = True

        if cfg["docker_gun"]:
            self.workers.append(firearm_worker())

        if cfg["docker_fire"]:
            self.workers.append(fire_worker())

        if cfg["docker_sleep"]:
            self.workers.append(sleep_worker())

        if cfg["docker_crowd_action"]:
            self.workers.append(crowd_action_worker())
        
        if flag_need_person_detect and cfg["docker_climb"] is False:
            self.workers.append(alphapose_worker())

        self.dockers_num = len(self.workers)


    def run(self):
        # start all threads of workers
        for worker in self.workers:
            print("{} start !".format(worker.name))
            worker.start()

        # init reader
        if self.use_test_video:
            vr = video_reader(self.video_path)
        else:
            vr = cam_reader(self.cam_url)
            
        # start work
        while not self.exit.is_set():
            data = vr.get_frame()
            if data is None:
                break

            if data["frame_idx"] % 24 == 0 and data["frame_idx"] > 48:
                ret_json = get_default_json()
                ret_json["camera_id"] = self.cam_id
                act_json = ret_json["action_analysis_result"]
                merge_json(self.workers,act_json)
                if self.flag_print:
                    print_json(data["frame_idx"],act_json)
                if self.flag_push:
                    push_json(ret_json,self.merge_url)
            
            for worker_id in range(self.dockers_num):
                self.workers[worker_id].solve_frame(data)

        self.shutdown()
        
    def shutdown(self):
        if not self.exit.is_set():
            self.exit.set()
            for worker in self.workers:
                print("{} end !".format(worker.name))
                worker.clean()


if __name__=='__main__':
    p = worker_group()
    json_path = "../config/start_cfg.json"
    with open(json_path,"r") as f:
        cfg_data = json.load(f)
    # print(cfg_data)
    p.read_cfg(cfg_data)
    p.start()






    

        
    