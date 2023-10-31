#!/bin/bash

# Download and install a sample configuration for testing Domibus
# This was made a separate script because it is not required to make Domibus work.

DOMIBUS_SAMPLE_FILE="domibus-msh-distribution-5.1.1-sample-configuration-and-testing.zip"
DOMIBUS_SAMPLE_URL="https://ec.europa.eu/digital-building-blocks/artifact/repository/eDelivery/eu/domibus/domibus-msh-distribution/5.1.1/$DOMIBUS_SAMPLE_FILE"

if ! test -f ./downloads/$DOMIBUS_SAMPLE_FILE; then
  wget -P ./downloads $DOMIBUS_SAMPLE_URL
fi

unzip -d ./domibus ./downloads/$DOMIBUS_SAMPLE_FILE
