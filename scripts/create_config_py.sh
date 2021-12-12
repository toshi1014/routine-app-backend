#!/bin/bash

set -e

source config/secrets.txt

# write into config.py
cat << EOS > config.py
SECRET_KEY="${SECRET_KEY}"
MYSQL_USER="${MYSQL_USER}"
MYSQL_PASSWORD="${MYSQL_PASSWORD}"
MYSQL_HOST="${MYSQL_HOST}"
DB_NAME="${DB_NAME}"
EOS