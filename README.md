


# 攀爬检测
sudo docker run -dt -p 7008:7008 --name alphapose --gpus 'device=1' --restart=always  detect_climb

# 暴力检测
sudo docker run -dt -p 7007:7007 --name detect_violence --gpus 'device=0'  --restart=always  detect_violence

# 枪械检测
sudo docker run -dt -p 7004:7004 --name detect_firearm --gpus 'device=2' --restart=always detect_firearm

# 人群计数
sudo docker run -dt -p 7005:7005 --name crowd_count  --gpus 'device=3'  --restart=always  353942829/crowd_count

# 火焰检测
sudo docker run -dt -p 7006:7006 --name detect_fire  --restart=always  353942829/detect_fire

# 打砸摄像头，人群异常奔跑
sudo docker run -dt -p 7003:7003 --name shake_cam --gpus 'device=1'  --restart=always  shake_cam

# 瞌睡检测
sudo docker run -dt -p 7012:7012 --name detect_sleep --gpus 'device=2' --restart=always detect_sleep

# 群体行为，打砸抢
sudo docker run -dt -p 7011:7011 --name crowd_action --gpus 'device=3' --restart=always crowd_action

# 打印空镜像id
sudo docker images|grep none|awk '{print $3}'

# 删除none镜像
sudo docker image rm `sudo docker images|grep none|awk '{print $3}'`

# 打印镜像tag
sudo docker images|grep swr|awk '{print $1":"$2}'

# 删除带swr的镜像tag，仅仅删除tag
sudo docker image rm `sudo docker images|grep swr.|awk '{print $1":"$2}'`

# 打印 不带 / 的镜像名:label
sudo docker images|grep -v /|awk '{print $1":"$2}'
# 删除不带 / 的镜像名:label
sudo docker image rm `sudo docker images|grep -v /|awk '{print $1":"$2}'`

# 根据用户id打印 容器
sudo docker ps -a |grep 353942829|awk '{print $1}'
# 删除自己的容器
sudo docker rm `sudo docker ps -a |grep apt|awk '{print $1}'`


# putty scp 到 远程服务器
pscp  -r ../lyl/deploy admincn@192.168.50.27:/home/admincn/ViolenceDetection
pscp local_file_path  


# 导出镜像
docker save <myimage>:<tag> | gzip > <myimage>_<tag>.tar.gz
docker save slowfast | gzip > slowfast.tar.gz

# 导入镜像
gunzip -c <myimage>_<tag>.tar.gz | docker load
gunzip -c slowfast.tar.gz | docker load

# 修改slowfast
sudo docker exec -it slowfast /bin/bash
vim flask/get_person_boxes.py

# 修改ip
sudo docker stop $(sudo docker ps -a -q)
