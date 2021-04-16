#!/bin/bash

docker build $CARBURE_HOME/web/fixtures/redcert --no-cache -t registry.gitlab.com/la-fabrique-numerique/biocarburants/redcert_downloader:latest
docker push registry.gitlab.com/la-fabrique-numerique/biocarburants/redcert_downloader:latest

