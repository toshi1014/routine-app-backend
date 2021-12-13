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