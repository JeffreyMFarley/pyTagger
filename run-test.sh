#!/bin/sh

docker rmi $(docker images -f "dangling=true" -q)

docker build -t jeffreymfarley/pytagger . && \

docker run -it \
--env-file /home/vagrant/.env \
-v "/home/vagrant:/home/project" \
--name pytagger jeffreymfarley/pytagger /bin/sh && \

docker stop pytagger && docker rm pytagger

