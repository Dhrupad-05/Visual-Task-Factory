import ast
from pathlib import Path


def test_scene_render_and_questions_modules_do_not_import_model_clients() -> None:
    forbidden_fragments = ("openai", "anthropic", "google.generativeai", "model_sdk")
    module_paths = [
        Path("vtf/scene"),
        Path("vtf/render"),
        Path("vtf/questions"),
    ]

    for directory in module_paths:
        for path in directory.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    imported = [node.module or ""]
                else:
                    continue
                assert not any(
                    any(fragment in name.lower() for fragment in forbidden_fragments)
                    for name in imported
                ), f"Forbidden model import in {path}: {imported}"
