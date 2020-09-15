#!/bin/bash

docker build -t registry.gitlab.com/la-fabrique-numerique/biocarburants/gitlab_runner:latest .  -f docker/Dockerfile.ci
docker push registry.gitlab.com/la-fabrique-numerique/biocarburants/gitlab_runner:latest

