#!/usr/bin/env python3
"""Check project structure and files."""

from pathlib import Path


def check_structure():
    """Check project structure."""
    required_files = [
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "MANIFEST.in",
        "AGENTS.md",
        "Makefile",
        "publish.py",
        "build.sh",
        "build.bat",
        "upload_pypi.sh",
        "upload_pypi.bat",
        ".pre-commit-config.yaml",
        ".github/workflows/ci.yml",
        ".github/workflows/publish.yml",
    ]

    required_dirs = [
        "bagualu",
        "bagualu/core",
        "bagualu/agents",
        "bagualu/skills",
        "bagualu/config",
        "bagualu/workflow",
        "bagualu/tools",
        "bagualu/web",
        "bagualu/utils",
        "bagualu/entrypoints",
        "tests",
        "examples",
        "scripts",
    ]

    print("Checking required files...")
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
            print(f"✗ {file}")
        else:
            print(f"✓ {file}")

    print("\nChecking required directories...")
    missing_dirs = []
    for dir in required_dirs:
        if not Path(dir).exists():
            missing_dirs.append(dir)
            print(f"✗ {dir}")
        else:
            print(f"✓ {dir}")

    if missing_files or missing_dirs:
        print("\n❌ Missing items detected!")
        return False

    print("\n✅ All required files and directories present!")
    return True


def check_python_files():
    """Check Python files."""
    print("\nChecking Python modules...")

    modules = [
        "bagualu/__init__.py",
        "bagualu/core/__init__.py",
        "bagualu/agents/__init__.py",
        "bagualu/skills/__init__.py",
        "bagualu/config/__init__.py",
        "bagualu/workflow/__init__.py",
        "bagualu/tools/__init__.py",
        "bagualu/web/__init__.py",
        "bagualu/utils/__init__.py",
        "bagualu/entrypoints/__init__.py",
    ]

    for module in modules:
        if Path(module).exists():
            print(f"✓ {module}")
        else:
            print(f"✗ {module}")


def main():
    """Main function."""
    print("=== BaGuaLu Project Structure Check ===\n")
    check_structure()
    check_python_files()
    print("\n=== Done ===")


if __name__ == "__main__":
    main()
