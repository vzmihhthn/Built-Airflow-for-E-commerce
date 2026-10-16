import pandas as pd
from postgresql_operator import PostgresOperators


def transform_dim_payments():
    staging_operator = PostgresOperators('postgres')
    warehouse_operator = PostgresOperators('postgres')

    # Đọc dữ liệu từ staging
    df = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_payments")

    # Transform
    df['payment_type'] = df['payment_type'].astype(str).str.lower().str.strip()
    df['payment_installments'] = pd.to_numeric(df['payment_installments'], errors='coerce')

    # Lấy business key duy nhất
    df = df[['payment_type', 'payment_installments']].drop_duplicates().reset_index(drop=True)

    # Tạo surrogate key
    df['payment_key'] = df.index + 1

    # Lưu dữ liệu
    warehouse_operator.save_data_to_postgres(
        df,
        'dim_payments',
        schema='warehouse',
        if_exists='replace'
    )

    print("Đã transform và lưu dim_payments")