sudo docker build -t test -f web_start_camera/dockerfile .
sudo docker run -dt --name test -p 7010:7010 test
sudo docker stop test && sudo docker rm test && sudo docker rmi test



sudo docker build -t test -f multi_thread/dockerfile .
sudo docker run -dt --name test -p 7009:7009 test
sudo docker stop test && sudo docker rm test && sudo docker rmi test