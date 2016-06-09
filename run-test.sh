#!/bin/sh

docker stop $(docker ps -a -q) 
docker rm $(docker ps -a -q) 
docker rmi $(docker images -f "dangling=true" -q)

docker build -t jeffreymfarley/pytagger-dev . && \

docker run -it \
--env-file /home/vagrant/.env \
--name pytagger-dev jeffreymfarley/pytagger-dev && \

docker stop pytagger-dev && docker rm pytagger-dev

# -v "/home/vagrant:/home/project" \
