#!/bin/bash

# Load environment variables from .env
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Substitute environment variables in the KrakenD config template
envsubst < /etc/krakend/krakend_template.json > /etc/krakend/krakend.json

# Start KrakenD
exec /usr/bin/krakend run -c /etc/krakend/krakend.json
