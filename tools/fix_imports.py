import pathlib
import re

PROJECT_PACKAGE = "app"
SRC_ROOT = pathlib.Path("src") / PROJECT_PACKAGE

IMPORT_RE = re.compile(r"^from\s+(ui|interaction_model|domain|services|infra)(\.[\w_]+)*\s+import\s+", re.MULTILINE)
IMPORT_RE2 = re.compile(r"^import\s+(ui|interaction_model|domain|services|infra)(\.[\w_]+)*", re.MULTILINE)

def fix_file(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")

    new_text = IMPORT_RE.sub(
        lambda m: m.group(0).replace(
            m.group(1),
            f"{PROJECT_PACKAGE}.{m.group(1)}",
        ),
        text,
    )

    new_text = IMPORT_RE2.sub(
        lambda m: m.group(0).replace(
            m.group(1),
            f"{PROJECT_PACKAGE}.{m.group(1)}",
        ),
        new_text,
    )

    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print("fixed:", path)

def run():
    for file in SRC_ROOT.rglob("*.py"):
        fix_file(file)

if __name__ == "__main__":
    run()
    