#!/bin/bash

# Check that networking is up.
[ "$NETWORKING" = "no" ] && exit 0

# -----------------------------------------------------------------------------

image_name=es
docker_tag="elasticsearch"

# -----------------------------------------------------------------------------

run() {
    docker run -d -p "9200:9200" \
    --name "$image_name" "$docker_tag"
    return $?
}

stop() {
    docker stop "$image_name" && docker rm "$image_name"
}

# -----------------------------------------------------------------------------

case $1 in
    run)
        run
        ;;
    stop)
        stop
        ;;
    *)
        echo "Usage: $0 {run | test}"
        exit 2
        ;;
esac
