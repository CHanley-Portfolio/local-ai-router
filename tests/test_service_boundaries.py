"""
Architecture-boundary tests for the standalone Local AI Router.

The router must remain independently installable and runnable without importing
implementation packages owned by the separate Local AI Benchmark repository.
"""

import ast
from pathlib import Path


ROUTER_SOURCE_ROOTS = (
    Path(__file__).resolve().parents[1] / "src" / "local_ai_router",
    Path(__file__).resolve().parents[1] / "src" / "local_ai_inference",
)

FORBIDDEN_IMPORT_ROOTS = {
    "local_ai_benchmark",
}


def test_router_does_not_import_benchmark_service() -> None:
    """
    Verify router-owned source has no implementation dependency on Benchmark Service.

    Python source is parsed through the abstract syntax tree so comments and
    documentation may still mention Benchmark Service as an optional external
    producer of capability data.
    """

    forbidden_imports: list[str] = []

    for source_root in ROUTER_SOURCE_ROOTS:
        for python_file in source_root.rglob("*.py"):
            syntax_tree = ast.parse(
                python_file.read_text(encoding="utf-8"),
                filename=str(python_file),
            )

            for syntax_node in ast.walk(syntax_tree):
                imported_modules: list[str] = []

                if isinstance(syntax_node, ast.Import):
                    imported_modules.extend(
                        imported_name.name
                        for imported_name in syntax_node.names
                    )

                elif isinstance(syntax_node, ast.ImportFrom):
                    if syntax_node.module is not None:
                        imported_modules.append(syntax_node.module)

                for imported_module in imported_modules:
                    import_root = imported_module.split(".", maxsplit=1)[0]

                    if import_root in FORBIDDEN_IMPORT_ROOTS:
                        forbidden_imports.append(
                            f"{python_file}: {imported_module}"
                        )

    assert forbidden_imports == [], (
        "Local AI Router must not import Benchmark Service implementation "
        "packages:\n"
        + "\n".join(forbidden_imports)
    )
