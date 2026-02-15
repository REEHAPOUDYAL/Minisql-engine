import os
import json

class RecordManager:
    def __init__(self, base_path="data"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def _table_path(self, table_name):
        return os.path.join(self.base_path, f"{table_name}.json")

    def insert(self, table_name, row, primary_key_col=None):
        rows = self.select_all(table_name)        
        if primary_key_col and primary_key_col in row:
            pk_value = row[primary_key_col]
            if any(r.get(primary_key_col) == pk_value for r in rows):
                raise ValueError(f"Integrity Error: Duplicate Primary Key '{pk_value}'")

        rows.append(row)
        self._write(table_name, rows)

    def select_all(self, table_name):
        path = self._table_path(table_name)
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def update_where(self, table_name, predicate, new_values):
        rows = self.select_all(table_name)
        updated_count = 0
        for row in rows:
            if predicate(row):
                row.update(new_values)
                updated_count += 1
        self._write(table_name, rows)
        return updated_count

    def delete_where(self, table_name, predicate):
        rows = self.select_all(table_name)
        new_rows = [r for r in rows if not predicate(r)]
        deleted = len(rows) - len(new_rows)
        self._write(table_name, new_rows)
        return deleted

    def _write(self, table_name, rows):
        path = self._table_path(table_name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)