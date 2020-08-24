import requests
import time

#推送数据，往url推送data
def push_json(data,url):
    try:
        r = requests.post(url, json=data)
        if r.status_code == 200:
            print(r.json())
        else:
            print(r.status_code)
    except:
        pass

if __name__ == "__main__":
    host = "localhost"
    cam_id = 13
    merge_url  = "http://{}:6666/api_get_TJUdata/0".format(host,cam_id)
    print(merge_url)

    frame_idx = 0
    while(True):
        frame_idx +=1 
        time.sleep(1)
        data = {"frame_idx":frame_idx}
        print(data)
        push_json(data,merge_url)
