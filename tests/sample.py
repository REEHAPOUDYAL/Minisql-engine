from minisql.catalog.schema import Column
from minisql.catalog.table_manager import TableManager
from minisql.query.tokenizer import Token
from minisql.query.parser import Parser

# Create table
tm = TableManager()
columns = [
    Column("id", "INT", primary_key=True),
    Column("name", "TEXT"),
    Column("age", "INT")
]
tm.create_table("users", columns)

# Insert example manually
tm.insert("users", ["id", "name", "age"], ["1", "Alice", "25"])
tm.insert("users", ["id", "name", "age"], ["2", "Bob", "30"])

print(tm.data["users"])

# Example tokens for update
tokens = [
    Token("KEYWORD", "UPDATE"),
    Token("IDENTIFIER", "users"),
    Token("KEYWORD", "SET"),
    Token("IDENTIFIER", "age"),
    Token("OPERATOR", "="),
    Token("LITERAL", "31"),
    Token("KEYWORD", "WHERE"),
    Token("IDENTIFIER", "name"),
    Token("OPERATOR", "="),
    Token("LITERAL", "Bob")
]

ast = Parser(tokens).parse()
print(ast)
