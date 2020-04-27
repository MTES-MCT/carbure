#!/bin/sh

# create config file from template
envsubst '$$NGINX_HOSTS $$NGINX_SSL_FOLDER' < /etc/nginx/conf.d/web.template > /etc/nginx/conf.d/default.conf

while :;
do sleep 6h & wait $${!}; nginx -s reload;
done & nginx -g "daemon off;"
