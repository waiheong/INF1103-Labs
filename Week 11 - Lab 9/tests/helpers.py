import ast
import io
from contextlib import redirect_stdout
from pathlib import Path

from supplier import Supplier

PROJECT_DIR = Path(__file__).resolve().parent.parent

def output_of(func, *args, **kwargs) -> str:
    """Run func and return everything it printed."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        func(*args, **kwargs)
    return buffer.getvalue()


def make_supplier() -> Supplier:
    return Supplier("SUP1", "FreshFarm Pte Ltd", "sales@freshfarm.sg")


def project_sources() -> dict[str, ast.Module]:
    return {path.name: ast.parse(path.read_text()) for path in PROJECT_DIR.glob("*.py")}
