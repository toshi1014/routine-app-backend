#!/bin/bash/

set -e

source config/config.txt
source config/secrets.txt


cd config/databases

create_table_cmd=""

for filename in *; do
    table_name="${filename%.*}"
    create_table_cmd="${create_table_cmd}CREATE TABLE ${table_name}(\n"
    while IFS=", " read COLUMN TYPE; do
        create_table_cmd="${create_table_cmd}${COLUMN} ${TYPE},\n"
    done < $filename

    create_table_cmd="${create_table_cmd%,*}\n);\n"     ## remove last "," & add "\n);"
done


CMD="
    DROP DATABASE IF EXISTS $DB_NAME;\n
    create database $DB_NAME;\n
    use $DB_NAME;\n
    $create_table_cmd
"

echo -e $CMD

echo -e $CMD | mysql -u root -p$MYSQL_PASSWORD