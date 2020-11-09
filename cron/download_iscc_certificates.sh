#!/bin/bash

docker cp carbure_app:/app/web/fixtures/fetch_iscc_certificates.py /tmp
python3 /tmp/fetch_iscc_certificates.py
docker cp /tmp/Certificates_$(date +%Y_%m_%d).csv carbure_app:/tmp
docker exec carbure_app python3 /app/web/fixtures/load_iscc_certificates.py
