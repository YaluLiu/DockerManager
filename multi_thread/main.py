import json
from worker_group import worker_group

if __name__=='__main__':
    group = worker_group()
    json_path = "../config/start_cfg.json"
    with open(json_path,"r") as f:
        cfg_data = json.load(f)
    group.read_cfg(cfg_data)
    group.start()