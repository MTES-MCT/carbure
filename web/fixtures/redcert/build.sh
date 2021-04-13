#!/bin/bash

docker build . --no-cache -t registry.gitlab.com/la-fabrique-numerique/biocarburants/redcert_downloader:latest
docker push registry.gitlab.com/la-fabrique-numerique/biocarburants/redcert_downloader:latest

