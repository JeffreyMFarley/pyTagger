#!/bin/bash

# Check that networking is up.
[ "$NETWORKING" = "no" ] && exit 0

# -----------------------------------------------------------------------------

image_name=pytagger-dev
docker_tag="jeffreymfarley/$image_name"

# -----------------------------------------------------------------------------

build() {
    docker build -t "$docker_tag" .
    return $?
}

clean() {
    dangle=$(docker images -f "dangling=true" -q 2>/dev/null)
    if [ -n "$dangle" ]
    then
        docker rmi "$dangle"
    fi
    return $?
}

nuke() {
    docker stop $(docker ps -a -q)
    docker rm $(docker ps -a -q)
    docker rmi $(docker images -a -q)
}

push() {
    if [ -z "$1" ]
    then
        docker push "$docker_tag"
    else
        docker tag "$docker_tag" "$docker_tag:$1"        
        docker push "$docker_tag:$1"
    fi
    return $?
}

run() {
    docker run -it \
    --env-file /home/vagrant/.env \
    --name "$image_name" "$docker_tag" /bin/sh
    return $?
}

run-test() {
    docker run -it \
    --env-file /home/vagrant/.env \
    --name "$image_name" "$docker_tag"
    return $?
}

stop() {
    docker stop "$image_name" && docker rm "$image_name"
}

# -----------------------------------------------------------------------------

case $1 in
    build)
        clean
        build
        ;;
    nuke)
        nuke
        ;;
    push)
        clean
        build && \
        push $2
        ;;
    run)
        clean
        build && \
        run
        stop
        ;;
    stop)
        stop
        ;;
    test)
        clean
        build && \
        run-test
        stop
        ;;
    *)
        echo "Usage: $0 {build | push | run | stop | test}"
        exit 2
        ;;
esac
