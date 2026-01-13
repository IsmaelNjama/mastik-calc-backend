#!/bin/bash

# Build the Lambda image
docker build -f Dockerfile.lambda -t mastik-calculator-lambda .

# Run with Lambda Runtime Interface Emulator
docker run -p 9000:8080 mastik-calculator-lambda