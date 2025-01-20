import ast
from typing import Set

from flake8_drf_permissions import Plugin


def _results(s: str) -> Set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree, 'file.py')
    return {
        f'{line}:{col} {msg}' for line, col, msg, _ in plugin.run()
    }

