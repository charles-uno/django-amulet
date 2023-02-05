#!/bin/bash

# NOTE: We're running nginx in Docker. No need for a Dockerfile since we're
# just mounting our config file into the default nginx image

ROOT_DIR=$(realpath $0 | xargs dirname | xargs dirname)

RUN_IN_BACKGROUND=false
OVERRIDE_CONFLICTS=false
for ARG in $@; do
    if [[ "$ARG" == "-b" || "$ARG" == "--background" ]]; then
        RUN_IN_BACKGROUND=true
    fi
    if [[ "$ARG" == "-f" || "$ARG" == "--force" ]]; then
        OVERRIDE_CONFLICTS=true
    fi
done

# We generally want to just leave the existing container in place, so bail silently

CONFLICTING_CONTAINER=$(docker ps | grep "0.0.0.0:80->" | awk '{print $1}')
if [[ "$CONFLICTING_CONTAINER" != "" ]]; then
    if [[ "$OVERRIDE_CONFLICTS" == "true" ]]; then
        echo "killing conflicting container $CONFLICTING_CONTAINER"
        docker stop "$CONFLICTING_CONTAINER"
    else
        echo "nginx already deployed, use --force to kill and restart"
        exit 0
    fi
fi

if [[ "$RUN_IN_BACKGROUND" == "true" ]]; then
    docker run -d -p 80:80 --mount type=bind,source="$ROOT_DIR/nginx/nginx.conf",target=/etc/nginx/conf.d/default.conf,readonly nginx:latest
else
    docker run -p 80:80 --mount type=bind,source="$ROOT_DIR/nginx/nginx.conf",target=/etc/nginx/conf.d/default.conf,readonly nginx:latest
fi

