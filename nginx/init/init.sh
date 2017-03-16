#!/usr/bin/env bash

export DOLLAR='$'
envsubst < /init/${URL}.conf.template > /etc/nginx/sites-enabled/${URL}.conf
envsubst < /init/${URL}.conf.template > /etc/nginx/sites-enabled/${URL}.conf
nginx -g "daemon off;"