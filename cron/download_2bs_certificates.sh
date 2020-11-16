#!/bin/bash

python3 /app/web/fixtures/fetch_2bs_certificates.py

if [ "$IMAGE_TAG" = "prod" ]; then
    python3 /app/web/fixtures/load_2bs_certificates.py --email
else
    python3 /app/web/fixtures/load_2bs_certificates.py --email --test
fi    


