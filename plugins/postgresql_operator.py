from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import create_engine


class PostgresOperators:
    def __init__(self, conn_id):
        self.hook = PostgresHook(postgres_conn_id=conn_id)

    def get_connection(self):
        return self.hook.get_conn()

    def get_data_to_pd(self, sql):
        return self.hook.get_pandas_df(sql)

    def create_schema_if_not_exists(self, schema):
        self.hook.run(f"CREATE SCHEMA IF NOT EXISTS {schema};")

    def save_data_to_postgres(self, df, table_name, schema='public', if_exists='replace'):
        self.create_schema_if_not_exists(schema)
        engine = create_engine(self.hook.get_uri())

        try:
            df.to_sql(
                name=table_name,
                con=engine,
                schema=schema,
                if_exists=if_exists,
                index=False
            )
        finally:
            engine.dispose()

    def execute_query(self, sql):
        self.hook.run(sql)