from typing import List, Optional, Union

class ASTNode:
    def __init__(self, node_type: str, value: Optional[Union[str, int, float]] = None):
        self.node_type = node_type
        self.value = value
        self.children: List[ASTNode] = []

    def add_child(self, child: "ASTNode") -> None:
        self.children.append(child)

    def __repr__(self):
        if self.children:
            return f"{self.node_type}({self.value}, children={self.children})"
        return f"{self.node_type}({self.value})"

class SelectNode(ASTNode):
    def __init__(self):
        super().__init__("SELECT")
        self.columns: List[str] = []
        self.table: Optional[str] = None
        self.where: Optional[str] = None

    def set_table(self, table: str):
        self.table = table

    def set_columns(self, columns: List[str]):
        self.columns = columns

    def set_where(self, condition: str):
        self.where = condition

class InsertNode(ASTNode):
    def __init__(self):
        super().__init__("INSERT")
        self.table: Optional[str] = None
        self.columns: List[str] = []
        self.values: List[Union[str, int, float]] = []

class UpdateNode(ASTNode):
    def __init__(self):
        super().__init__("UPDATE")
        self.table: Optional[str] = None
        self.assignments: List[str] = []
        self.where: Optional[str] = None

class DeleteNode(ASTNode):
    def __init__(self):
        super().__init__("DELETE")
        self.table: Optional[str] = None
        self.where: Optional[str] = None
