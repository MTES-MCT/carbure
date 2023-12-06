#!/bin/bash
# Force restart of metabase container

install-scalingo-cli
scalingo login --api-token $SCALINGO_TOKEN
scalingo -a carbure-metabase restart