import pandas as pd
from datetime import datetime, timedelta
from postgresql_operator import PostgresOperators


def transform_dim_customers():
    staging_operator = PostgresOperators('postgres')
    warehouse_operator = PostgresOperators('postgres')

    # Đọc dữ liệu từ staging
    df = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_customers")

    # Transform
    df['customer_unique_id'] = df['customer_unique_id'].astype(str)
    df['customer_zip_code_prefix'] = df['customer_zip_code_prefix'].astype(str).str.zfill(5)
    df['customer_city'] = df['customer_city'].str.title()
    df['customer_state'] = df['customer_state'].str.upper()

    # Tạo surrogate key
    df['customer_key'] = df.index + 1

    # SCD
    current_date = datetime.now().date()
    df['effective_date'] = current_date
    df['end_date'] = current_date + timedelta(days=365 * 10)
    df['is_current'] = True

    # Lưu dữ liệu
    warehouse_operator.save_data_to_postgres(
        df,
        'dim_customers',
        schema='warehouse',
        if_exists='replace'
    )

    print("Đã transform và lưu dim_customers")