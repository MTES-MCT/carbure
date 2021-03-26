#!/bin/bash

docker run -v "/tmp/redcert":"/app/downloads" -it redcert_downloader node index.js
