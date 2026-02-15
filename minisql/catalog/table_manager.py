from minisql.catalog.schema import TableSchema, Column
from minisql.utils.exceptions import SchemaError
from minisql.storage.serializer import Serializer 
import pickle
import os

class TableManager:
    def __init__(self, db_path=r"C:\Users\poudy\Downloads\DSA\data\data.db"):
        self.db_path = db_path
        self.tables = {}
        self.load() 

    def create_table(self, table_name: str, columns: list[Column]) -> None:
        if table_name in self.tables:
            raise SchemaError(f"Table {table_name} already exists")
        self.tables[table_name] = TableSchema(table_name, columns)
        self.save() 

    def drop_table(self, table_name: str) -> None:
        if table_name not in self.tables:
            raise SchemaError(f"Table {table_name} does not exist")
        del self.tables[table_name]
        self.save()

    def get_table_schema(self, table_name: str) -> TableSchema:
        if table_name not in self.tables:
            raise SchemaError(f"Table {table_name} does not exist")
        return self.tables[table_name]

    def list_tables(self) -> list[str]:
        return list(self.tables.keys())

    def save(self) -> None:
        try:
            with open(self.db_path, 'wb') as f:
                pickle.dump(self.tables, f)
        except Exception as e:
            pass

    def load(self) -> None:
        if os.path.exists(self.db_path) and os.path.getsize(self.db_path) > 0:
            try:
                with open(self.db_path, 'rb') as f:
                    data = pickle.load(f)
                    if isinstance(data, dict):
                        self.tables = data
            except Exception as e:
                pass