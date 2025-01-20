import ast
import dataclasses
import importlib.metadata
from typing import Type, Any, Generator, Tuple


@dataclasses.dataclass
class Flake8MissingIsAuthenticatedPermissionError:
    lineno: int
    col_offset: int
    msg: str


class Visitor(ast.NodeVisitor):
    parent = None

    def __init__(self) -> None:
        self.errors: list[Flake8MissingIsAuthenticatedPermissionError] = []

    def visit(self, node):
        node.parent = self.parent
        self.parent = node

        return super().visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        body = node.body
        for statement in body:
            if isinstance(statement, ast.Assign):
                if len(statement.targets) == 1:
                    target = statement.targets[0]
                    if isinstance(target, ast.Name):
                        if target.id == 'permission_classes' and isinstance(statement.value, (ast.List, ast.Tuple)):
                            permission_names = [
                                el.id for el in statement.value.elts if isinstance(el, ast.Name)
                            ]
                            if 'IsAuthenticated' not in permission_names:
                                self.errors.append(
                                    Flake8MissingIsAuthenticatedPermissionError(
                                        lineno=statement.lineno,
                                        col_offset=statement.col_offset,
                                        msg='PDR001 IsAuthenticated permission is missing in permission_classes',
                                    )
                                )

        self.generic_visit(node)


class Plugin:
    name = __name__
    version = importlib.metadata.version(__name__)

    def __init__(self, tree: ast.AST, filename: str):
        self.tree = tree
        self.filename = filename

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self.tree)
        for error in visitor.errors:
            yield error.lineno, error.col_offset, error.msg, type(self)