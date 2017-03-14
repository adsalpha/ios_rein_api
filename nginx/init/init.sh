#!/usr/bin/env bash

export DOLLAR='$'
envsubst < /etc/nginx/sites-available/${URL}.conf.template > /etc/nginx/sites-enabled/${URL}.conf
envsubst < /etc/nginx/sites-enabled/${URL}.conf.template > /etc/nginx/sites-enabled/${URL}.conf
nginx -g "daemon off;"