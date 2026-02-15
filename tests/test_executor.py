import tempfile
from minisql.catalog.table_manager import TableManager
from minisql.index.index_manager import IndexManager
from minisql.query.executer import QueryExecutor
from minisql.query.tokenizer import Tokenizer
from minisql.query.parser import Parser
from minisql.catalog.schema import Column


def run_query(executor, query: str):
    tokens = Tokenizer(query).tokenize()
    ast = Parser(tokens).parse()
    return executor.execute(ast)


def test_executor_insert_select_update_delete():
    tm = TableManager()
    im = IndexManager()
    executor = QueryExecutor(tm, im)

    columns = [
        Column("id", "INT", primary_key=True),
        Column("name", "STRING"),
        Column("age", "INT"),
    ]

    tm.create_table("users", columns)

    result = run_query(executor, "INSERT INTO users (id, name, age) VALUES (1, 'Alice', 25)")
    assert "Inserted" in result

    result = run_query(executor, "SELECT id, name, age FROM users WHERE age > 20")
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["name"] == "Alice"

    result = run_query(executor, "UPDATE users SET age = 26 WHERE name = 'Alice'")
    assert "Updated" in result or "UPDATE" in str(result)

    result = run_query(executor, "DELETE FROM users WHERE id = 1")
    assert "Deleted" in result or "DELETE" in str(result)

    result = run_query(executor, "SELECT id, name, age FROM users WHERE age > 20")
    assert len(result) == 0
