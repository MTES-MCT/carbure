#!/bin/bash

docker cp carbure_app:/app/web/fixtures/fetch_2bs_certificates.py /tmp
python3 /tmp/fetch_2bs_certificates.py
docker cp /tmp/Certificates_2bs_$(date +%Y_%m_%d).csv carbure_app:/tmp
docker exec carbure_app python3 /app/web/fixtures/load_2bs_certificates.py
