class TemplateOperatorDB:
    def __init__(self, table_name):
        self.table_name = table_name

    def create_query_insert_into(self, dataframe):
        columns = ", ".join(dataframe.columns)
        values = ", ".join(["%s"] * len(dataframe.columns))
        odku = ", ".join([f"{col}=VALUES({col})" for col in dataframe.columns])

        return (
            f"INSERT INTO {self.table_name} ({columns}) "
            f"VALUES ({values}) "
            f"ON DUPLICATE KEY UPDATE {odku}"
        )

    def create_delete_query(self, key_field, values):
        placeholders = ", ".join(["%s"] * len(values))

        return (
            f"DELETE FROM {self.table_name} "
            f"WHERE {key_field} IN ({placeholders})"
        )