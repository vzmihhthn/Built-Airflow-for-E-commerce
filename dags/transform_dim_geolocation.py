import pandas as pd
from postgresql_operator import PostgresOperators


def transform_dim_geolocation():
    staging_operator = PostgresOperators('postgres')
    warehouse_operator = PostgresOperators('postgres')

    # Đọc dữ liệu từ staging
    df = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_geolocation")

    # Transform
    df['geolocation_zip_code_prefix'] = pd.to_numeric(df['geolocation_zip_code_prefix'], errors='coerce')
    df = df.dropna(subset=['geolocation_zip_code_prefix'])
    df['geolocation_zip_code_prefix'] = df['geolocation_zip_code_prefix'].astype(int).astype(str).str.zfill(5)
    df['geolocation_city'] = df['geolocation_city'].str.strip().str.title()
    df['geolocation_state'] = df['geolocation_state'].str.strip().str.upper()

    # Một ZIP một dòng
    df = df.drop_duplicates(subset=['geolocation_zip_code_prefix']).reset_index(drop=True)

    # Tạo surrogate key
    df['geolocation_key'] = df.index + 1

    # Lưu dữ liệu
    warehouse_operator.save_data_to_postgres(
        df,
        'dim_geolocation',
        schema='warehouse',
        if_exists='replace'
    )

    print("Đã transform và lưu dim_geolocation")