import re
from typing import List

class Token:
    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Tokenizer:
    def __init__(self, text: str):
        self.text = text
        self.tokens: List[Token] = []
        self.keywords = {
            "SELECT", "FROM", "WHERE", "INSERT", "INTO", 
            "VALUES", "UPDATE", "SET", "DELETE", "CREATE", "TABLE", 
            "PRIMARY", "KEY", "INT", "STRING", "TEXT"
        }

    def tokenize(self) -> List[Token]:
        token_specification = [
            ("LITERAL", r"'[^']*'|\d+"),              
            ("KEYWORD", r"[a-zA-Z_][a-zA-Z0-9_]*"),  
            ("OPERATOR", r">=|<=|!=|[>=<=]"),         
            ("PUNCTUATION", r"[(),*]"),               
            ("SKIP", r"[ \t\n]+"),                    
            ("MISMATCH", r"."),                     
        ]
        
        tok_regex = "|".join("(?P<%s>%s)" % pair for pair in token_specification)
        for mo in re.finditer(tok_regex, self.text):
            kind = mo.lastgroup
            value = mo.group()
            
            if kind == "KEYWORD":
                if value.upper() in self.keywords:
                    self.tokens.append(Token("KEYWORD", value))
                else:
                    self.tokens.append(Token("IDENTIFIER", value))
            elif kind == "LITERAL":
                self.tokens.append(Token("LITERAL", value))
            elif kind == "OPERATOR":
                self.tokens.append(Token("OPERATOR", value))
            elif kind == "PUNCTUATION":
                self.tokens.append(Token("PUNCTUATION", value))
            elif kind == "SKIP":
                continue
            elif kind == "MISMATCH":
                raise RuntimeError(f"Unexpected character: {value}")
        
        return self.tokens