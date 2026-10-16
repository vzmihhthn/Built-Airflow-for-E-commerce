import pandas as pd
from postgresql_operator import PostgresOperators


def transform_dim_dates():
    warehouse_operator = PostgresOperators('postgres')

    # Tạo bảng Date
    date_range = pd.date_range(start='2016-01-01', end='2025-12-31', freq='D')
    df = pd.DataFrame({'full_date': date_range})

    # Tạo surrogate key
    df['date_key'] = df.index + 1

    # Thông tin ngày
    df['day'] = df['full_date'].dt.day
    df['month'] = df['full_date'].dt.month
    df['year'] = df['full_date'].dt.year
    df['quarter'] = df['full_date'].dt.quarter
    df['day_of_week'] = df['full_date'].dt.dayofweek
    df['day_name'] = df['full_date'].dt.day_name()
    df['month_name'] = df['full_date'].dt.month_name()
    df['is_weekend'] = df['day_of_week'].isin([5, 6])

    # Lưu dữ liệu
    warehouse_operator.save_data_to_postgres(
        df,
        'dim_dates',
        schema='warehouse',
        if_exists='replace'
    )

    print("Đã transform và lưu dim_dates")