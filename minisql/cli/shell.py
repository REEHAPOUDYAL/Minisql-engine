from minisql.query.parser import Parser
from minisql.query.executer import QueryExecutor
from minisql.catalog.table_manager import TableManager
from minisql.index.index_manager import IndexManager
from minisql.query.tokenizer import Tokenizer

class MiniSQLShell:
    def __init__(self):
        self.table_manager = TableManager()
        self.index_manager = IndexManager()
        self.executor = QueryExecutor(self.table_manager, self.index_manager)

    def start(self):
        print("Welcome to MiniSQL CLI. Type 'exit' to quit.")
        while True:
            try:
                query = input("MiniSQL> ").strip()
                if query.lower() in {"exit", "quit"}:
                    print("Exiting MiniSQL CLI.")
                    break
                if not query:
                    continue
                tokens = Tokenizer(query).tokenize()
                ast = Parser(tokens).parse()
                result = self.executor.execute(ast)
                if result is not None:
                    print(result)
            except Exception as e:
                print(f"Error: {e}")
