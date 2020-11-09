#!/bin/bash

python3 /app/web/fixtures/fetch_iscc_certificates.py
python3 /app/web/fixtures/load_iscc_certificates.py
