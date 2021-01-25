#!/bin/bash

scp docker-compose.server.yml $1:/home/deploy/docker-compose.yml

ssh $1 docker-compose up -d
