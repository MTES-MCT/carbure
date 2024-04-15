#!/bin/bash
# Force restart of metabase container

install-scalingo-cli
scalingo login --api-token $SCALINGO_TOKEN
scalingo --region osc-secnum-fr1 -a carbure-metabase restart