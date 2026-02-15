from minisql.query.ast import ASTNode
from minisql.catalog.schema import Column

class QueryError(Exception):
    pass

class QueryExecutor:
    def __init__(self, table_manager, index_manager=None, record_manager=None):
        self.table_manager = table_manager
        self.index_manager = index_manager
        self.record_manager = record_manager

    def execute(self, node: ASTNode):
        if node is None:
            raise QueryError("Empty query")
        
        nt = node.node_type.upper()
        result = None

        if nt == "INSERT": result = self._execute_insert(node)
        elif nt == "SELECT": result = self._execute_select(node)
        elif nt == "UPDATE": result = self._execute_update(node)
        elif nt == "DELETE": result = self._execute_delete(node)
        elif nt == "CREATE_TABLE": result = self._execute_create_table(node)
        elif nt == "DROP_TABLE": result = self._execute_drop_table(node)
        else:
            raise QueryError(f"Unsupported node type: {nt}")

        if nt in ["INSERT", "UPDATE", "DELETE", "CREATE_TABLE", "DROP_TABLE"]:
            self.table_manager.save()
            
        return result

    def _execute_create_table(self, node: ASTNode):
        table_name = self._get_child_value(node, "TABLE")
        raw_columns = self._get_child_value(node, "COLUMNS")
        columns = []
        col_defs = raw_columns.split(",") if isinstance(raw_columns, str) else raw_columns
        for col_def in col_defs:
            parts = col_def.strip().split()
            if len(parts) < 2: continue
            col_name = parts[0].strip().lower()
            col_type = parts[1].strip().upper()
            pk = "PRIMARY" in [p.upper() for p in parts]
            columns.append(Column(col_name, col_type, primary_key=pk))
        self.table_manager.create_table(table_name, columns)
        return f"Table {table_name} created"


    def _execute_insert(self, node: ASTNode):
            table_name = self._get_child_value(node, "TABLE")
            raw_cols = self._get_child_value(node, "COLUMNS")
            raw_vals = self._get_child_value(node, "VALUES")
            schema = self.table_manager.get_table_schema(table_name)
            col_names = [c.strip().lower() for c in (raw_cols.split(",") if isinstance(raw_cols, str) else raw_cols)]
            input_vals = raw_vals.split(",") if isinstance(raw_vals, str) else raw_vals
            val_list = [str(v).strip().replace("'", "").replace('"', "") for v in input_vals]

            primary_key_col = None
            for col in schema.columns:
                if col.primary_key:
                    primary_key_col = col.name.lower()
                    break

            row = {}
            for name, val in zip(col_names, val_list):
                col_def = next((c for c in schema.columns if c.name.lower() == name), None)
                row[name] = int(val) if (col_def and col_def.type == "INT") else val

            if not hasattr(schema, "data"): 
                schema.data = []

            if primary_key_col and primary_key_col in row:
                pk_value = row[primary_key_col]
                if any(existing_row.get(primary_key_col) == pk_value for existing_row in schema.data):
                    raise QueryError(f"Duplicate entry '{pk_value}' for primary key")

            if self.record_manager:
                self.record_manager.insert(table_name, row, primary_key_col=primary_key_col)

            schema.data.append(row)

            if self.index_manager:
                pk = schema.get_primary_key_column()
                if pk and pk.name.lower() in row:
                    self.index_manager.create_index(table_name, pk.name, schema)
                    self.index_manager.insert(table_name, pk.name, row[pk.name.lower()], row)

            self.table_manager.save()
            return f"Inserted into {table_name}"

    def _execute_select(self, node: ASTNode):
        table_name = self._get_child_value(node, "TABLE")
        raw_cols = self._get_child_value(node, "COLUMNS")
        where_node = self._get_child_node(node, "WHERE")
        schema = self.table_manager.get_table_schema(table_name)
        
        rows = getattr(schema, "data", [])
        if self.record_manager:
            storage_rows = self.record_manager.select_all(table_name)
            if storage_rows: rows = storage_rows

        if where_node:
            rows = [r for r in rows if self._evaluate_condition(r, where_node.value, schema)]

        if raw_cols and raw_cols != "*" and raw_cols != ["*"]:
            target_cols = [c.strip().lower() for c in (raw_cols.split(",") if isinstance(raw_cols, str) else raw_cols)]
            return [{c: r.get(c) for c in target_cols} for r in rows]
        
        return rows

    def _execute_update(self, node: ASTNode):
        table_name = self._get_child_value(node, "TABLE")
        set_node = self._get_child_node(node, "SET")
        where_node = self._get_child_node(node, "WHERE")
        schema = self.table_manager.get_table_schema(table_name)
        
        parts = set_node.value.split("=")
        set_col = parts[0].strip().lower()
        set_val = parts[1].strip().replace("'", "").replace('"', "")
        
        rows = getattr(schema, "data", [])
        updated_count = 0
        col_def = next((c for c in schema.columns if c.name.lower() == set_col), None)
        final_val = int(set_val) if (col_def and col_def.type == "INT") else set_val

        for row in rows:
            if not where_node or self._evaluate_condition(row, where_node.value, schema):
                row[set_col] = final_val
                updated_count += 1
        
        return f"Updated {updated_count} rows"

    def _execute_delete(self, node: ASTNode):
        table_name = self._get_child_value(node, "TABLE")
        where_node = self._get_child_node(node, "WHERE")
        schema = self.table_manager.get_table_schema(table_name)
        
        rows = getattr(schema, "data", [])
        if not where_node:
            count = len(rows)
            schema.data = []
            return f"Deleted {count} rows"

        kept = [r for r in rows if not self._evaluate_condition(r, where_node.value, schema)]
        deleted_count = len(rows) - len(kept)
        schema.data = kept
        return f"Deleted {deleted_count} rows"

    def _evaluate_condition(self, row: dict, condition: str, schema) -> bool:
        ops = [">=", "<=", "!=", "=", ">", "<"]
        op = next((o for o in ops if o in condition), None)
        if not op: return False
        
        parts = condition.split(op)
        col_name = parts[0].strip().lower()
        target = parts[1].strip().replace("'", "").replace('"', "")
        actual = row.get(col_name)
        
        col_def = next((c for c in schema.columns if c.name.lower() == col_name), None)
        if col_def and col_def.type == "INT":
            try:
                actual, target = int(actual), int(target)
            except: pass

        if op == "=": return actual == target
        if op == "!=": return actual != target
        if op == ">": return actual > target
        if op == "<": return actual < target
        if op == ">=": return actual >= target
        if op == "<=": return actual <= target
        return False

    def _get_child_value(self, node, c_type):
        child = self._get_child_node(node, c_type)
        return child.value if child else None

    def _get_child_node(self, node, c_type):
        if not node or not hasattr(node, 'children'): return None
        for child in node.children:
            if child.node_type.upper() == c_type.upper(): return child
        return None