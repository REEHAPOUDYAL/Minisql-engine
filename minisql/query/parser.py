from typing import List, Optional
from minisql.query.tokenizer import Token

class ASTNode:
    def __init__(self, node_type: str, value: Optional[str] = None):
        self.node_type = node_type
        self.value = value
        self.children: List[ASTNode] = []

    def add_child(self, child: "ASTNode") -> None:
        self.children.append(child)

    def __repr__(self):
        if self.children:
            return f"{self.node_type}({self.value}, children={self.children})"
        return f"{self.node_type}({self.value})"

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

    def parse(self) -> ASTNode:
        if not self.tokens:
            return ASTNode("EMPTY")
        
        token = self._peek()
        if token.type == "KEYWORD":
            command = token.value.upper()
            if command == "SELECT":
                return self._parse_select()
            elif command == "INSERT":
                return self._parse_insert()
            elif command == "UPDATE":
                return self._parse_update()
            elif command == "DELETE":
                return self._parse_delete()
            elif command == "CREATE":
                return self._parse_create_table()
        
        return ASTNode("UNKNOWN")

    def _parse_create_table(self) -> ASTNode:
            node = ASTNode("CREATE_TABLE")
            self._expect_keyword("CREATE")
            self._expect_keyword("TABLE")
            
            table_name = self._expect_identifier()
            node.add_child(ASTNode("TABLE", table_name))
            
            self._expect_punctuation("(")
            
            column_definitions = []
            while True:
                col_name_token = self._consume()
                col_name = col_name_token.value
                
                col_type_token = self._consume()
                col_type = col_type_token.value
                
                current_col = [col_name, col_type]
                
                if self._peek_value("PRIMARY"):
                    self._expect_keyword("PRIMARY")
                    self._expect_keyword("KEY")
                    current_col.append("PRIMARY KEY")
                
                column_definitions.append(" ".join(current_col))
                
                if self._peek_value(","):
                    self._expect_punctuation(",")
                else:
                    break
            
            node.add_child(ASTNode("COLUMNS", ",".join(column_definitions)))
            self._expect_punctuation(")")
            return node

    def _parse_select(self) -> ASTNode:
            node = ASTNode("SELECT")
            self._expect_keyword("SELECT")            
            if self._peek_value("*"):
                self._consume() 
                node.add_child(ASTNode("COLUMNS", "*"))
            else:
                columns = self._parse_column_list()
                node.add_child(ASTNode("COLUMNS", ",".join(columns)))
                
            self._expect_keyword("FROM")
            table = self._expect_identifier()
            node.add_child(ASTNode("TABLE", table))
            
            if self._peek_value("WHERE"):
                self._expect_keyword("WHERE")
                condition = self._parse_condition()
                node.add_child(ASTNode("WHERE", condition))
            return node

    def _parse_insert(self) -> ASTNode:
        node = ASTNode("INSERT")
        self._expect_keyword("INSERT")
        self._expect_keyword("INTO")
        
        table = self._expect_identifier()
        node.add_child(ASTNode("TABLE", table))
        
        self._expect_punctuation("(")
        columns = self._parse_column_list()
        node.add_child(ASTNode("COLUMNS", ",".join(columns)))
        self._expect_punctuation(")")
        
        self._expect_keyword("VALUES")
        self._expect_punctuation("(")
        values = self._parse_value_list()
        node.add_child(ASTNode("VALUES", ",".join(values)))
        self._expect_punctuation(")")
        return node

    def _parse_update(self) -> ASTNode:
        node = ASTNode("UPDATE")
        self._expect_keyword("UPDATE")
        table = self._expect_identifier()
        node.add_child(ASTNode("TABLE", table))
        
        self._expect_keyword("SET")
        assignments = self._parse_assignments()
        node.add_child(ASTNode("SET", ",".join(assignments)))
        
        if self._peek_value("WHERE"):
            self._expect_keyword("WHERE")
            condition = self._parse_condition()
            node.add_child(ASTNode("WHERE", condition))
        return node

    def _parse_delete(self) -> ASTNode:
        node = ASTNode("DELETE")
        self._expect_keyword("DELETE")
        self._expect_keyword("FROM")
        table = self._expect_identifier()
        node.add_child(ASTNode("TABLE", table))
        
        if self._peek_value("WHERE"):
            self._expect_keyword("WHERE")
            condition = self._parse_condition()
            node.add_child(ASTNode("WHERE", condition))
        return node

    def _parse_column_list(self) -> List[str]:
        columns = []
        while True:
            columns.append(self._expect_identifier())
            if self._peek_value(","):
                self._expect_punctuation(",")
            else:
                break
        return columns

    def _parse_value_list(self) -> List[str]:
        values = []
        while True:
            values.append(self._expect_literal_or_identifier())
            if self._peek_value(","):
                self._expect_punctuation(",")
            else:
                break
        return values

    def _parse_assignments(self) -> List[str]:
        assignments = []
        while True:
            column = self._expect_identifier()
            self._expect_operator("=")
            value = self._expect_literal_or_identifier()
            assignments.append(f"{column}={value}")
            if self._peek_value(","):
                self._expect_punctuation(",")
            else:
                break
        return assignments

    def _parse_condition(self) -> str:
        left = self._expect_identifier()
        op = self._expect_operator()
        right = self._expect_literal_or_identifier()
        return f"{left} {op} {right}"

    def _peek(self) -> Token:
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return Token("EOF", "")

    def _peek_value(self, value: str) -> bool:
        token = self._peek()
        return token.value.upper() == value.upper()

    def _consume(self) -> Token:
        token = self._peek()
        self.position += 1
        return token

    def _expect_keyword(self, value: str) -> str:
        token = self._consume()
        if token.type != "KEYWORD" or token.value.upper() != value.upper():
            raise ValueError(f"Expected keyword {value}, got {token.value}")
        return token.value

    def _expect_identifier(self) -> str:
        token = self._consume()
        if token.type != "IDENTIFIER":
            raise ValueError(f"Expected identifier, got {token.value}")
        return token.value

    def _expect_operator(self, expected: Optional[str] = None) -> str:
        token = self._consume()
        if token.type != "OPERATOR" or (expected and token.value != expected):
            raise ValueError(f"Expected operator {expected}, got {token.value}")
        return token.value

    def _expect_punctuation(self, value: str) -> str:
        token = self._consume()
        if token.type != "PUNCTUATION" or token.value != value:
            raise ValueError(f"Expected punctuation {value}, got {token.value}")
        return token.value

    def _expect_literal_or_identifier(self) -> str:
        token = self._consume()
        if token.type not in {"LITERAL", "IDENTIFIER"}:
            raise ValueError(f"Expected literal or identifier, got {token.value}")
        return token.value