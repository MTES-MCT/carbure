#!/bin/bash

python3 /app/web/fixtures/fetch_iscc_certificates.py

if [ "$IMAGE_TAG" = "prod" ]; then
    python3 /app/web/fixtures/load_iscc_certificates.py --email
else
    python3 /app/web/fixtures/load_iscc_certificates.py
fi    


