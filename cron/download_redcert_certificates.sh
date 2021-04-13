#!/bin/bash

# IMPORTANT NOTE: this script is NOT run in carbure_app docker (unlike ISCC and 2BS certificate fetchers)

docker cp carbure_app:/app/web/fixtures/redcert/cron.sh /tmp
bash /tmp/cron.sh # pulls docker image, then fetches certificates, and pushes certificates to carbure_app:/app/web/fixtures/csv/

if [ "$IMAGE_TAG" = "prod" ]; then
    docker exec carbure_app python3 /app/web/fixtures/load_redcert_certificates.py --email
else
    docker exec carbure_app python3 /app/web/fixtures/load_redcert_certificates.py --email --test
fi    

