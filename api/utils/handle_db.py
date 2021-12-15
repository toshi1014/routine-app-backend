import mysql.connector
import config

db = mysql.connector.connect(
    user=config.MYSQL_USER,
    password=config.MYSQL_PASSWORD,
    host=config.MYSQL_HOST,
    port=config.MYSQL_PORT,
)
db.ping(reconnect=True)
cursor = db.cursor(buffered=True)
cursor.execute(f"USE {config.DB_NAME}")
db.commit()


class MySQLHandler():
    @classmethod
    def insert(cls, table_name, key_val_dict):
        key_list = ""
        val_list = ""
        for key in key_val_dict:
            key_list += key + ","
            val_list += "'" + key_val_dict[key] + "',"

        key_list, val_list = key_list[:-1], val_list[:-1]     ## remove last ","

        cmd = f"INSERT INTO {table_name} ({key_list}) VALUES ({val_list});"
        cursor.execute(cmd)
        db.commit()

    @classmethod
    def fetch(cls, table_name, key, val):
        cmd = f"SELECT * FROM {table_name} WHERE {key}='{val}';"
        cursor.execute(cmd)
        rows = cursor.fetchall()
        if len(rows) == 1:
            row = rows[0]
        elif len(rows) == 0:
            raise ValueError("value not found")
        else:
            raise ValueError("multi value found")

        ## return list row as dict
        dict_row = {}
        for column, val in zip(config.db_column_list[table_name], row):
            dict_row.update({column: val})
        return dict_row


    @classmethod
    def fetchall(cls, table_name):
        cmd = f"SELECT * FROM {table_name} WHERE id=(SELECT MAX(id) from {table_name})"
        cursor.execute(cmd)
        max_id = cursor.fetchall()[0][0]

        row_list = []
        for i in range(1, max_id+1):
            row = self.fetch(table_name, "id", i)

            ## if no val in returned dict
            if len(row) != 0:
                row_list.append(row)

        # TODO: return as dict

        return row_list

    @classmethod
    def delete(cls, table_name, key, val):
        cmd = f"DELETE * FROM {table_name} WHERE {key}='{val}';"
        cursor.execute(cmd)
        db.commit()

    @classmethod
    def update(cls, table_name, key, val, dict_update_column_val):
        str_column_val = ",".join([
            f"{column} = '{dict_update_column_val[column]}',"
                for column in dict_update_column_val
        ])[:-1]     ## [:-1] remove last ","
        cmd = f"UPDATE {table_name} SET {str_column_val} WHERE {key}='{val}';"
        cursor.execute(cmd)
        db.commit()

    @classmethod
    def drop(cls, table_name):
        cmd = f"DROP table {table_name};"
        cursor.execute(cmd)