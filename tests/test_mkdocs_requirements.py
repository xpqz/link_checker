"""Tests for MkDocs requirements file (Task 1.2)."""

from pathlib import Path
import yaml


def _get_required_dependencies_from_mkdocs_config():
    """Extract required dependencies from the actual MkDocs configuration.

    This reads dyalog-docs/mkdocs.yml to determine which MkDocs plugins
    and markdown extensions are actually used, then maps them to their
    corresponding Python packages.
    """
    mkdocs_config = Path("dyalog-docs/mkdocs.yml")
    with open(mkdocs_config) as f:
        config = yaml.safe_load(f)

    # Base requirement
    required = {"mkdocs"}

    # Add theme requirement
    if config.get("theme", {}).get("name") == "material":
        required.add("mkdocs-material")

    # Map plugins to their package names
    # Note: privacy plugin is built into mkdocs-material, no separate package needed
    plugin_to_package = {
        "macros": "mkdocs-macros-plugin",
        "monorepo": "mkdocs-monorepo-plugin",
        "minify": "mkdocs-minify-plugin",
        "caption": "mkdocs-caption",
    }

    # Add plugin requirements
    for plugin in config.get("plugins", []):
        # Plugins can be strings or dicts
        plugin_name = plugin if isinstance(plugin, str) else list(plugin.keys())[0]
        if plugin_name in plugin_to_package:
            required.add(plugin_to_package[plugin_name])

    # Map markdown extensions to their package names
    # Note: Most markdown extensions are built into Python-Markdown or pymdown-extensions
    # Only list here if they require a separate package
    extension_to_package = {
        "markdown_tables_extended": "markdown-tables-extended",
    }

    # Add markdown extension requirements
    for ext in config.get("markdown_extensions", []):
        # Extensions can be strings or dicts
        ext_name = ext if isinstance(ext, str) else list(ext.keys())[0]
        if ext_name in extension_to_package:
            required.add(extension_to_package[ext_name])

    return required


def test_requirements_file_exists():
    """Verify docker/requirements.txt exists."""
    requirements_file = Path("docker/requirements.txt")
    assert requirements_file.exists(), "docker/requirements.txt must exist"
    assert requirements_file.is_file(), "docker/requirements.txt must be a file"


def test_requirements_contains_all_dependencies():
    """Verify requirements.txt contains all dependencies from mkdocs.yml.

    This test derives the required dependencies from the actual MkDocs
    configuration in dyalog-docs/mkdocs.yml, ensuring the Docker
    requirements match the actual documentation needs.
    """
    requirements_file = Path("docker/requirements.txt")
    content = requirements_file.read_text()

    # Get required dependencies from actual configuration
    required_dependencies = _get_required_dependencies_from_mkdocs_config()

    # Parse the requirements file to extract package names
    # Handle both "package" and "package==version" formats
    found_dependencies = set()
    for line in content.strip().split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            # Extract package name (before any version specifier)
            package_name = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
            found_dependencies.add(package_name)

    missing = required_dependencies - found_dependencies
    assert not missing, (
        f"Missing required dependencies: {missing}. " f"Found: {found_dependencies}"
    )

    assert found_dependencies == required_dependencies, (
        f"Requirements file should contain exactly the required dependencies. "
        f"Expected: {required_dependencies}, Found: {found_dependencies}"
    )


def test_requirements_file_format():
    """Verify requirements.txt has valid format.

    Each line should be either:
    - A package name
    - A package name with version (package==version)
    - A comment (starting with #)
    - Empty/whitespace
    """
    requirements_file = Path("docker/requirements.txt")
    content = requirements_file.read_text()

    for line_num, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()
        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            continue

        # Check that line contains a valid package specification
        # Should have a package name (alphanumeric, hyphens, underscores)
        assert any(
            c.isalnum() or c in "-_" for c in stripped
        ), f"Line {line_num} has invalid format: '{line}'"
