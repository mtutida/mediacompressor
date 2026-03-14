import ast
import pathlib

PROJECT_PACKAGE = "app"
SRC_ROOT = pathlib.Path("src") / PROJECT_PACKAGE


def normalize_imports(file_path: pathlib.Path):
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    lines = source.splitlines()
    changed = False

    for node in ast.walk(tree):

        if isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue

            if not node.module.startswith(PROJECT_PACKAGE):

                top = node.module.split(".")[0]

                module_path = SRC_ROOT / top

                if module_path.exists():
                    new_module = f"{PROJECT_PACKAGE}.{node.module}"

                    line_index = node.lineno - 1
                    old_line = lines[line_index]

                    new_line = old_line.replace(
                        f"from {node.module}",
                        f"from {new_module}"
                    )

                    lines[line_index] = new_line
                    changed = True

        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name

                if not name.startswith(PROJECT_PACKAGE):

                    top = name.split(".")[0]

                    module_path = SRC_ROOT / top

                    if module_path.exists():

                        new_name = f"{PROJECT_PACKAGE}.{name}"

                        line_index = node.lineno - 1
                        old_line = lines[line_index]

                        new_line = old_line.replace(name, new_name)

                        lines[line_index] = new_line
                        changed = True

    if changed:
        file_path.write_text("\n".join(lines), encoding="utf-8")
        print("fixed:", file_path)


def main():

    for py_file in SRC_ROOT.rglob("*.py"):
        normalize_imports(py_file)


if __name__ == "__main__":
    main()
    