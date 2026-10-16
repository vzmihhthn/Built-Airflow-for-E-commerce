import pandas as pd
from postgresql_operator import PostgresOperators


def transform_dim_sellers():
    staging_operator = PostgresOperators('postgres')
    warehouse_operator = PostgresOperators('postgres')

    # Đọc dữ liệu từ staging
    df = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_sellers")

    # Transform
    df['seller_zip_code_prefix'] = df['seller_zip_code_prefix'].astype(str).str.zfill(5)
    df['seller_city'] = df['seller_city'].str.title()
    df['seller_state'] = df['seller_state'].str.upper()

    # Tạo surrogate key
    df['seller_key'] = df.index + 1
    df['last_updated'] = pd.Timestamp.now().date()

    # Lưu dữ liệu
    warehouse_operator.save_data_to_postgres(
        df,
        'dim_sellers',
        schema='warehouse',
        if_exists='replace'
    )

    print("Đã transform và lưu dim_sellers")