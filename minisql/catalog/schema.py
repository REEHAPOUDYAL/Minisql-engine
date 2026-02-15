from typing import Literal, Any
DataType = Literal["INT", "FLOAT", "STRING", "BOOL"]

class Column:
    def __init__(self, name: str, col_type: str, primary_key: bool = False):
        self.name = name
        self.type = col_type
        self.primary_key = primary_key


class TableSchema:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self.data = []

    def get_primary_key_column(self):
        for col in self.columns:
            if getattr(col, "primary_key", False):
                return col
        return None
