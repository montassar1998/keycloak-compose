#!/bin/bash

# Load environment variables from .env
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Substitute environment variables in the KrakenD config template
