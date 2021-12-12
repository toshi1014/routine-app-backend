import mysql.connector
import config

db = mysql.connector.connect(
    # user=config.MYSQL_USER,
    # password=config.MYSQL_PASSWORD,
    # host=config.MYSQL_HOST,
    user="root",
    password="password",
    host="localhost",
    database="routine_app",
)

cursor = db.cursor(buffered=True)
cursor.execute(f"USE {config.DB_NAME};")
db.commit()


class MySQLHandler():
    @classmethod
    def insert(cls, table_name, key_val_dict):
        key_list = ""
        val_list = ""
        for key in key_val_dict:
            key_list += key + ", "
            val_list += "'" + val + "', "

        cmd = f"INSERT INTO {table_name} ({key_list}) VALUES ({val_list});"
        cursor.execute(cmd)

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

        # TODO: return as dict

        return row

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
    def update(cls, cmd):
        cursor.execute(cmd)
        db.commit()

    @classmethod
    def drop(cls, table_name):
        cmd = f"DROP table {table_name};"
        cursor.execute(cmd)