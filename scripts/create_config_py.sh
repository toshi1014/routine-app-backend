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
POSTS_PER_PAGE=${POSTS_PER_PAGE}
EMAIL_HOST="${EMAIL_HOST}"
EMAIL_PORT=${EMAIL_PORT}
EMAIL_HOST_USER="${EMAIL_HOST_USER}"
EMAIL_HOST_PASSWORD="${EMAIL_HOST_PASSWORD}"
EMAIL_ADMIN="${EMAIL_ADMIN}"
BADGE_L1=${BADGE_L1}
BADGE_L2=${BADGE_L2}
BADGE_L3=${BADGE_L3}
FRONTEND_URL="${FRONTEND_URL}"
EOS


cd config/databases

db_column_list="db_column_list={\n"

for filename in *; do
    table_name="\t'${filename%.*}'"
    db_column_list="${db_column_list}${table_name}: ["
    while IFS=", " read COLUMN TYPE; do
        db_column_list="${db_column_list}'${COLUMN}',"
    done < $filename

    db_column_list="${db_column_list%,*}],\n"     ## remove last "," & add "\n);"
done
db_column_list="${db_column_list}}"

cd ../../

echo -e $db_column_list >> config.py