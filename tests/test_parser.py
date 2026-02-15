import pytest
from minisql.query.tokenizer import Tokenizer
from minisql.query.parser import Parser


def parse_query(query: str):
    tokens = Tokenizer(query).tokenize()
    return Parser(tokens).parse()

def test_parse_insert():
    query = "INSERT INTO users (id, name, age) VALUES (1, 'Alice', 25)"
    ast = parse_query(query)
    assert ast.node_type == "INSERT"
    assert ast.children[0].node_type == "TABLE"
    assert ast.children[0].value == "users"

def test_parse_select_with_where():
    query = "SELECT id, name FROM users WHERE age > 20"
    ast = parse_query(query)
    assert ast.node_type == "SELECT"
    assert any(child.node_type == "WHERE" for child in ast.children)

def test_parse_update():
    query = "UPDATE users SET age = 30 WHERE id = 1"
    ast = parse_query(query)
    assert ast.node_type == "UPDATE"
    assert any(child.node_type == "SET" for child in ast.children)

def test_parse_delete():
    query = "DELETE FROM users WHERE id = 1"
    ast = parse_query(query)
    assert ast.node_type == "DELETE"
    assert any(child.node_type == "WHERE" for child in ast.children)
