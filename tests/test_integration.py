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


def test_full_pipeline():
    tm = TableManager()
    im = IndexManager()
    executor = QueryExecutor(tm, im)

    tm.create_table(
        "users",
        [
            Column("id", "INT", primary_key=True),
            Column("name", "STRING"),
            Column("age", "INT"),
        ],
    )

    run_query(executor, "INSERT INTO users (id, name, age) VALUES (1, 'Alice', 25)")
    run_query(executor, "INSERT INTO users (id, name, age) VALUES (2, 'Bob', 30)")
    run_query(executor, "INSERT INTO users (id, name, age) VALUES (3, 'Charlie', 40)")

    result = run_query(executor, "SELECT id, name FROM users WHERE age > 29")
    assert len(result) == 2

    names = {row["name"] for row in result}
    assert "Bob" in names
    assert "Charlie" in names

    run_query(executor, "DELETE FROM users WHERE id = 2")

    result = run_query(executor, "SELECT id, name FROM users WHERE age > 29")
    assert len(result) == 1
    assert result[0]["name"] == "Charlie"
