import psycopg2
from Settings.database_config import *
import time

class DataBase:

    connection = None

    def connection_open(self):
        try:
            self.connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                dbname=dbname,
                port=port
            )

            self.connection.autocommit = True

        except Exception as exc:
            print("[INFO] Error while working with PostgreSQL")
            print(exc)

    def connection_close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            print("[INFO] PostgreSQL connection closed")

    def check_connection(self):
        if self.connection:
            return None
        else:
            self.connection_open()

    def create_table(self, table: str):
        self.check_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {table}
                (
                    datetime bigint PRIMARY KEY,
                    price float NOT NULL,
                    self_price float NOT NULL
                )"""
            )
        self.delete_data(table)

    async def insert_data(self, table, source_data):
        self.check_connection()

        with self.connection.cursor() as cursor:
            for datetime, price in source_data.items():
                self_price = price[1]
                current_price = price[0]

                cursor.execute(
                    f"""INSERT INTO {table} VALUES
                    (
                        {datetime},
                        {current_price},
                        {self_price}
                    )"""
                )


    def delete_data(self, table: str):
        yesterday = (int((time.time() - 86400)*1000))
        self.check_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""DELETE FROM {table}
                WHERE datetime < {yesterday}"""
            )

    def get_data(self, table: str):
        self.check_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""SELECT price FROM {table}
                ORDER BY price"""
            )
            prices_list_of_tuples = cursor.fetchall()
            if prices_list_of_tuples:
                prices_list = [i[0] for i in prices_list_of_tuples]
                return prices_list
            else:
                prices_list = [0, 1]
                return prices_list