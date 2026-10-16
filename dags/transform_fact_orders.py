import pandas as pd
from postgresql_operator import PostgresOperators


def transform_fact_orders():
    pg = PostgresOperators('postgres')

    # 1. READ DATA
    orders = pg.get_data_to_pd("SELECT * FROM staging.stg_orders")
    items = pg.get_data_to_pd("SELECT * FROM staging.stg_order_items")
    payments = pg.get_data_to_pd("SELECT * FROM staging.stg_payments")
    customers = pg.get_data_to_pd("SELECT customer_id, customer_zip_code_prefix FROM staging.stg_customers")

    dim_customers = pg.get_data_to_pd("SELECT customer_key, customer_id FROM warehouse.dim_customers")
    dim_products = pg.get_data_to_pd("SELECT product_key, product_id FROM warehouse.dim_products")
    dim_sellers = pg.get_data_to_pd("SELECT seller_key, seller_id FROM warehouse.dim_sellers")
    dim_geo = pg.get_data_to_pd("SELECT geolocation_key, geolocation_zip_code_prefix FROM warehouse.dim_geolocation")
    dim_payments = pg.get_data_to_pd("SELECT payment_key, payment_type, payment_installments FROM warehouse.dim_payments")
    dim_dates = pg.get_data_to_pd("SELECT date_key, full_date FROM warehouse.dim_dates")

    # 2. MERGE STAGING
    df = (orders
          .merge(items, on='order_id', how='left')
          .merge(payments, on='order_id', how='left')
          .merge(customers, on='customer_id', how='left'))

    # 3. CLEAN
    date_cols = ['order_purchase_timestamp', 'order_approved_at',
                 'order_delivered_carrier_date', 'order_delivered_customer_date',
                 'order_estimated_delivery_date']

    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    for col in ['price', 'freight_value', 'payment_value']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 4. CUSTOMER / PRODUCT / SELLER KEY
    df = df.merge(dim_customers[['customer_id', 'customer_key']], on='customer_id', how='left')
    df = df.merge(dim_products[['product_id', 'product_key']], on='product_id', how='left')
    df = df.merge(dim_sellers[['seller_id', 'seller_key']], on='seller_id', how='left')

    # 5. DATE KEY
    df['full_date'] = df['order_purchase_timestamp'].dt.normalize()
    dim_dates['full_date'] = pd.to_datetime(dim_dates['full_date']).dt.normalize()
    df = df.merge(dim_dates[['full_date', 'date_key']], on='full_date', how='left')

    # 6. GEOLOCATION KEY
    df['zip_key'] = pd.to_numeric(df['customer_zip_code_prefix'], errors='coerce').astype('Int64').astype('string').str.zfill(5)
    dim_geo['zip_key'] = pd.to_numeric(dim_geo['geolocation_zip_code_prefix'], errors='coerce').astype('Int64').astype('string').str.zfill(5)

    geo_lookup = dim_geo[['zip_key', 'geolocation_key']].drop_duplicates('zip_key')
    df = df.merge(geo_lookup, on='zip_key', how='left')

    # 7. PAYMENT KEY
    df['payment_type'] = df['payment_type'].astype(str).str.lower().str.strip()
    dim_payments['payment_type'] = dim_payments['payment_type'].astype(str).str.lower().str.strip()

    df['payment_installments'] = pd.to_numeric(df['payment_installments'], errors='coerce')
    dim_payments['payment_installments'] = pd.to_numeric(dim_payments['payment_installments'], errors='coerce')

    payment_lookup = dim_payments[
        ['payment_type', 'payment_installments', 'payment_key']
    ].drop_duplicates(['payment_type', 'payment_installments'])

    df = df.merge(payment_lookup, on=['payment_type', 'payment_installments'], how='left')

    # 8. KEY TYPE
    key_cols = ['customer_key', 'product_key', 'seller_key',
                'geolocation_key', 'payment_key', 'date_key']

    for col in key_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    # 9. METRICS
    df['total_amount'] = df['price'].fillna(0) + df['freight_value'].fillna(0)
    df['delivery_time'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    df['estimated_delivery_time'] = (df['order_estimated_delivery_date'] - df['order_purchase_timestamp']).dt.days

    # 10. FACT TABLE
    fact = df[[
        'order_id', 'customer_key', 'product_key', 'seller_key',
        'geolocation_key', 'payment_key', 'date_key', 'order_status',
        'price', 'freight_value', 'total_amount', 'payment_value',
        'delivery_time', 'estimated_delivery_time'
    ]].copy()

    pg.save_data_to_postgres(
        fact,
        'fact_orders',
        schema='warehouse',
        if_exists='replace'
    )

    print(f"Đã transform và lưu fact_orders: {len(fact)} rows")