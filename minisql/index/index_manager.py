from minisql.catalog.schema import TableSchema
from .bplustree import BPlusTree

class IndexManager:
    def __init__(self):
        self.indexes: dict[str, BPlusTree] = {}

    def create_index(self, table_name: str, column_name: str, table_schema: TableSchema):
        index_key = f"{table_name}.{column_name}"
        if index_key in self.indexes:
            return
        
        self.indexes[index_key] = BPlusTree()
        col_idx = self._get_column_index(table_schema, column_name)
        
        data = getattr(table_schema, "data", [])
        for row in data:
            if column_name in row:
                self.indexes[index_key].insert(row[column_name], row)

    def insert(self, table_name: str, column_name: str, key, value):
        index_key = f"{table_name}.{column_name}"
        if index_key in self.indexes:
            self.indexes[index_key].insert(key, value)

    def drop_index(self, table_name: str, column_name: str):
        index_key = f"{table_name}.{column_name}"
        if index_key not in self.indexes:
            raise ValueError(f"No index found on {index_key}")
        del self.indexes[index_key]

    def search_index(self, table_name: str, column_name: str, value):
        index_key = f"{table_name}.{column_name}"
        if index_key not in self.indexes:
            return None
        return self.indexes[index_key].search(value)

    def _get_column_index(self, table_schema: TableSchema, column_name: str):
        for idx, col in enumerate(table_schema.columns):
            if col.name == column_name:
                return idx
        raise ValueError(f"Column {column_name} does not exist in table {table_schema.table_name}")