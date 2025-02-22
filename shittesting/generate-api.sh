#!/bin/sh

set -e
ROOT=$(dirname $0)
cd "$ROOT"

sudo rm -Rf ./endpoints/apis ./endpoints/models ./endpoints/router_init.py
mkdir -p "$ROOT/endpoints"

sudo rm -Rf ./openapi-generator-output
docker run --rm -v "${PWD}":/app openapitools/openapi-generator-cli:latest-release generate  \
    -i /app/openapi.yml  -g python-fastapi   -o /app/openapi-generator-output \
    --additional-properties=packageName=endpoints --additional-properties=fastapiImplementationPackage=endpoints