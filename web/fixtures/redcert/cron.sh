#!/bin/bash

docker pull registry.gitlab.com/la-fabrique-numerique/biocarburants/redcert_downloader:latest
docker run -v "/tmp/redcert":"/app/downloads" -it registry.gitlab.com/la-fabrique-numerique/biocarburants/redcert_downloader:latest node index.js
docker cp /tmp/redcert/REDcert-certificates-$(date +%Y-%m-%d).xlsx carbure_app:/app/web/fixtures/csv/REDcert-certificates.xlsx
