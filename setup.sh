#!/bin/bash

set -e

source config/secrets.txt

# write into config.py
cat << EOS > config.py
SECRET_KEY="${SECRET_KEY}"
EOS