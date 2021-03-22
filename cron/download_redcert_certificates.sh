#!/bin/bash

python3 /app/web/fixtures/fetch_redcert_certificates.py

if [ "$IMAGE_TAG" = "prod" ]; then
    python3 /app/web/fixtures/load_redcert_certificates.py --email
else
    python3 /app/web/fixtures/load_redcert_certificates.py --email --test
fi    


