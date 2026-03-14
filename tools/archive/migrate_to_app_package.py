import pathlib
import shutil

OLD_PACKAGE = "mediacompressorpro"
NEW_PACKAGE = "app"

SRC_DIR = pathlib.Path("src")
OLD_DIR = SRC_DIR / OLD_PACKAGE
NEW_DIR = SRC_DIR / NEW_PACKAGE


def rename_package():
    if not OLD_DIR.exists():
        print("package not found")
        return

    print("renaming package folder...")
    shutil.move(str(OLD_DIR), str(NEW_DIR))


def rewrite_imports():

    print("rewriting imports...")

    for py_file in SRC_DIR.rglob("*.py"):

        text = py_file.read_text(encoding="utf8")

        text = text.replace(
            f"from {OLD_PACKAGE}.",
            f"from {NEW_PACKAGE}."
        )

        text = text.replace(
            f"import {OLD_PACKAGE}.",
            f"import {NEW_PACKAGE}."
        )

        py_file.write_text(text, encoding="utf8")


def rewrite_pyproject():

    pyproject = pathlib.Path("pyproject.toml")

    if not pyproject.exists():
        return

    text = pyproject.read_text()

    text = text.replace(OLD_PACKAGE, NEW_PACKAGE)

    pyproject.write_text(text)


def main():

    rename_package()
    rewrite_imports()
    rewrite_pyproject()

    print("migration completed")


if __name__ == "__main__":
    main()
    