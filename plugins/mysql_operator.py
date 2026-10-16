from airflow.providers.mysql.hooks.mysql import MySqlHook
from support_processing import TemplateOperatorDB
from contextlib import closing
import logging
import os


class MySQLOperators:
    def __init__(self, conn_id="mysql"):
        try:
            self.mysqlhook = MySqlHook(mysql_conn_id=conn_id)
            self.mysql_conn = self.mysqlhook.get_conn()
        except Exception as e:
            logging.error(f"Can't connect to {conn_id} database: {e}")

    def get_data_to_pd(self, query):
        return self.mysqlhook.get_pandas_df(query)

    def get_records(self, query):
        return self.mysqlhook.get_records(query)

    def execute_query(self, query):
        try:
            cur = self.mysql_conn.cursor()
            cur.execute(query)
            self.mysql_conn.commit()
        except Exception as e:
            logging.error(f"Can't execute {query}: {e}")

    def insert_dataframe_into_table(self, table_name, dataframe, data, chunk_size=10000):
        query = TemplateOperatorDB(table_name).create_query_insert_into(dataframe)
        try:
            with closing(self.mysql_conn) as conn:
                cur = conn.cursor()
                for i in range(0, len(data), chunk_size):
                    values = [
                        [self.mysqlhook._serialize_cell(cell, conn) for cell in row]
                        for row in data[i:i + chunk_size]
                    ]
                    cur.executemany(query, values)
                    conn.commit()
                    print(f"Merged or updated {len(values)} records")
        except Exception as e:
            logging.error(f"Can't execute {query}: {e}")

    def delete_records_in_table(self, table_name, key_field, values):
        query = TemplateOperatorDB(table_name).create_delete_query(key_field, values)
        try:
            cur = self.mysql_conn.cursor()
            del_values = tuple(self.mysqlhook._serialize_cell(x, self.mysql_conn) for x in values)
            cur.execute(query, del_values)
            self.mysql_conn.commit()
            print(f"Deleted {len(values)} records")
        except Exception as e:
            logging.error(f"Can't execute {query}: {e}")

    def remove_table_if_exists(self, table_name):
        self.execute_query(f"DROP TABLE IF EXISTS {table_name};")

    def truncate_all_data_from_table(self, table_name):
        self.execute_query(f"TRUNCATE TABLE {table_name};")

    def dump_table_into_path(self, table_name):
        try:
            priv = self.mysqlhook.get_first("SELECT @@global.secure_file_priv")
            if priv and priv[0]:
                tbl_name = list(table_name)[0]
                file_name = tbl_name.replace(".", "__")
                self.mysqlhook.bulk_dump(tbl_name, os.path.join(priv[0], f"{file_name}.txt"))
        except Exception as e:
            logging.error(f"Can't dump {table_name}: {e}")

    def load_data_into_table(self, table_name):
        try:
            priv = self.mysqlhook.get_first("SELECT @@global.secure_file_priv")
            if priv and priv[0]:
                file_path = os.path.join(priv[0], "TABLES.txt")
                self.execute_query(f"LOAD DATA INFILE '{file_path}' INTO TABLE {table_name};")
        except Exception as e:
            logging.error(f"Can't load {table_name}: {e}")