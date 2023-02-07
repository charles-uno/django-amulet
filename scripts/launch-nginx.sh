#!/bin/bash

ROOT_DIR=$(realpath $0 | xargs dirname | xargs dirname)

# Container is launched in the background by default. Debug means launch it in
# the foreground so we can see the output
DEBUG=false
FORCE=false
for ARG in $@; do
    if [[ "$ARG" == "-d" || "$ARG" == "--debug" ]]; then
        DEBUG=true
    fi
    if [[ "$ARG" == "-f" || "$ARG" == "--force" ]]; then
        FORCE=true
    fi
done

# We generally want to just leave the existing container in place, so bail silently

CONFLICTING_CONTAINER=$(docker ps | grep "0.0.0.0:80->" | awk '{print $1}')
if [[ "$CONFLICTING_CONTAINER" != "" ]]; then
    if [[ "$FORCE" == "true" ]]; then
        echo "killing conflicting container $CONFLICTING_CONTAINER"
        docker stop "$CONFLICTING_CONTAINER"
    else
        echo "nginx already deployed, use --force to kill and restart"
        exit 0
    fi
fi

# Static content is served by nginx directly. Gotta mount it in






if [[ "$DEBUG" == "true" ]]; then
    docker run \
        -p 80:80 \
        --mount type=bind,source="$ROOT_DIR/nginx/nginx.conf",target=/etc/nginx/conf.d/default.conf,readonly \
        --mount type=bind,source="$ROOT_DIR/app/frontend/static/",target=/www/static/,readonly \
        nginx:latest
else
    docker run -d \
        -p 80:80 \
        --mount type=bind,source="$ROOT_DIR/nginx/nginx.conf",target=/etc/nginx/conf.d/default.conf,readonly \
        --mount type=bind,source="$ROOT_DIR/app/frontend/static/",target=/www/static/,readonly \
        nginx:latest
fi

