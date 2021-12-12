#!/bin/bash

set -e

source config/config.txt
source config/secrets.txt


# write into config.py
cat << EOS > config.py
SECRET_KEY="${SECRET_KEY}"
MYSQL_USER="${MYSQL_USER}"
MYSQL_PASSWORD="${MYSQL_PASSWORD}"
MYSQL_HOST="${MYSQL_HOST}"
MYSQL_PORT="${MYSQL_PORT}"
DB_NAME="${DB_NAME}"
EOS