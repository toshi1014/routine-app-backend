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
        str_keys = ""
        str_vals = ""
        for key in key_val_dict:
            str_keys += key + ","
            if isinstance(key_val_dict[key], int):
                str_vals += "" + str(key_val_dict[key]) + ","
            else:
                str_vals += "'" + key_val_dict[key] + "',"

        str_keys, str_vals = str_keys[:-1], str_vals[:-1]  # remove last ","

        cmd = f"INSERT INTO {table_name} ({str_keys}) VALUES ({str_vals});"
        print("\n\t", cmd, "\n")
        cursor.execute(cmd)
        db.commit()
        return cursor.lastrowid

    def change_into_dict(table_name, row_list):
        dict_row_list = []
        for row in row_list:
            dict_row = {}
            for column, val in zip(config.db_column_list[table_name], row):
                dict_row.update({column: val})
            dict_row_list.append(dict_row)
        return dict_row_list

    def join_with_AND(key_val_dict):
        str_conditions = ""
        for key in key_val_dict:
            if isinstance(key_val_dict[key], int):
                str_conditions += f"{key}=" + str(key_val_dict[key]) + " AND "
            else:
                str_conditions += f"{key} = '{key_val_dict[key]}' AND "

        return str_conditions[:-5]  # remove last " AND "

    def fetch_base(cls, table_name, key_val_dict):
        str_conditions = cls.join_with_AND(key_val_dict)
        cmd = f"SELECT * FROM {table_name} WHERE {str_conditions};"
        print("\n\t", cmd, "\n")
        cursor.execute(cmd)
        row_list = cursor.fetchall()
        return cls.change_into_dict(table_name, row_list)

    @classmethod
    def fetch(cls, table_name, key_val_dict, allow_empty=False):
        row_list = cls.fetch_base(cls, table_name, key_val_dict)
        if len(row_list) == 1:
            return row_list[0]
        elif len(row_list) == 0:
            if not allow_empty:
                raise ValueError("value not found")
            return row_list
        else:
            raise ValueError("multi value found")

    @classmethod
    def fetchall(cls, table_name, key_val_dict, allow_empty=False):
        row_list = cls.fetch_base(cls, table_name, key_val_dict)
        if (len(row_list) == 0) & (not allow_empty):
            raise ValueError("value not found")
        else:
            return row_list

        # cmd = f"SELECT * FROM {table_name} WHERE id=(SELECT MAX(id) from {table_name})"
        # cursor.execute(cmd)
        # max_id = cursor.fetchall()[0][0]
        #
        # row_list = []
        # for i in range(1, max_id+1):
        #     row = self.fetch(table_name, "id", i)
        #
        #     ## if no val in returned dict
        #     if len(row) != 0:
        #         row_list.append(row)
        #
        # # TODO: return as dict
        #
        # return row_list

    @classmethod
    def delete(cls, table_name, key_val_dict):
        str_conditions = cls.join_with_AND(key_val_dict)
        cmd = f"DELETE FROM {table_name} WHERE {str_conditions};"
        print("\n\t", cmd, "\n")
        cursor.execute(cmd)
        db.commit()

    @classmethod
    def update(cls, table_name, key_val_dict, dict_update_column_val):
        str_column_val = ", ".join([
            f"{column}='{dict_update_column_val[column]}'"
            for column in dict_update_column_val
        ])

        str_conditions = cls.join_with_AND(key_val_dict)
        cmd = f"UPDATE {table_name} SET {str_column_val} WHERE {str_conditions};"
        print("\n\t", cmd, "\n")
        cursor.execute(cmd)
        db.commit()

    @classmethod
    def drop(cls, table_name):
        cmd = f"DROP table {table_name};"
        cursor.execute(cmd)

    @classmethod
    def search(cls, keyword, table_column_dict):
        result_list = []
        id_list = []

        for table in table_column_dict:
            cmd = f"SELECT * FROM {table} WHERE "
            for column in table_column_dict[table]:
                cmd += f"{column} LIKE '%{keyword}%' OR "

            cmd = cmd[:-4] + ";"  # remove last " OR "
            print("\n\t", cmd, "\n")
            cursor.execute(cmd)
            row_list = cursor.fetchall()
            row_dict_list = cls.change_into_dict(table, row_list)

            # if xx_contents, check not to append duplicate post
            if table[-8:] == "contents":
                for contents_row_dict in row_dict_list:
                    if not contents_row_dict["post_id"] in id_list:
                        id_list.append(contents_row_dict["post_id"])

                        row_dict = cls.fetch(
                            table[:-9] + "s",  # get parent table
                            {"id": contents_row_dict["post_id"]},
                            allow_empty=False
                        )
                        result_list.append(row_dict)
            else:
                result_list = row_dict_list
                id_list = [row_dict["id"] for row_dict in row_dict_list]

        return result_list

    @classmethod
    def get_all_records(cls, db_name):
        cmd = f" SELECT * FROM {db_name};"
        print("\n\t", cmd, "\n")
        cursor.execute(cmd)
        return cursor.fetchall()