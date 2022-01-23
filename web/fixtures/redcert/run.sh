#!/bin/bash

docker run -v "/tmp/redcert":"/app/downloads" -it registry.gitlab.com/la-fabrique-numerique/biocarburants/redcert_downloader:latest node index.js
