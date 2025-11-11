"""Tests for docker-compose.yml (Task 1.5)."""

import subprocess
from pathlib import Path
import yaml


def test_docker_compose_file_exists():
    """Verify docker-compose.yml exists in project root."""
    compose_file = Path("docker-compose.yml")
    assert compose_file.exists(), "docker-compose.yml must exist in project root"
    assert compose_file.is_file(), "docker-compose.yml must be a file"


def test_docker_compose_valid_yaml():
    """Verify docker-compose.yml is valid YAML."""
    compose_file = Path("docker-compose.yml")
    content = compose_file.read_text()

    # Should parse without errors
    try:
        config = yaml.safe_load(content)
        assert config is not None, "docker-compose.yml should not be empty"
    except yaml.YAMLError as e:
        raise AssertionError(f"docker-compose.yml is not valid YAML: {e}")


def test_docker_compose_has_services():
    """Verify docker-compose.yml defines services."""
    compose_file = Path("docker-compose.yml")
    config = yaml.safe_load(compose_file.read_text())

    assert "services" in config, "docker-compose.yml must define services"
    assert config["services"], "services section must not be empty"


def test_docker_compose_has_docs_server_service():
    """Verify docker-compose.yml defines docs-server service."""
    compose_file = Path("docker-compose.yml")
    config = yaml.safe_load(compose_file.read_text())

    assert (
        "docs-server" in config["services"]
    ), "docker-compose.yml must define docs-server service"


def test_docker_compose_build_context():
    """Verify docs-server service has correct build context."""
    compose_file = Path("docker-compose.yml")
    config = yaml.safe_load(compose_file.read_text())

    service = config["services"]["docs-server"]
    assert "build" in service, "docs-server must have build configuration"

    build = service["build"]
    # Build can be a string (context) or dict with context key
    if isinstance(build, str):
        context = build
    else:
        context = build.get("context", "")

    assert (
        "docker" in context or context == "."
    ), "Build context should reference docker directory"


def test_docker_compose_port_mapping():
    """Verify docs-server service maps port 8080:80."""
    compose_file = Path("docker-compose.yml")
    config = yaml.safe_load(compose_file.read_text())

    service = config["services"]["docs-server"]
    assert "ports" in service, "docs-server must define port mappings"

    ports = service["ports"]
    # Ports can be strings like "8080:80" or dicts
    port_mapping_found = False
    for port in ports:
        if isinstance(port, str):
            if "8080:80" in port or "8080" in port and "80" in port:
                port_mapping_found = True
        elif isinstance(port, dict):
            if port.get("published") == "8080" and port.get("target") == 80:
                port_mapping_found = True

    assert port_mapping_found, "docs-server must map port 8080:80"


def test_docker_compose_container_name():
    """Verify docs-server service has correct container name."""
    compose_file = Path("docker-compose.yml")
    config = yaml.safe_load(compose_file.read_text())

    service = config["services"]["docs-server"]
    assert "container_name" in service, "docs-server must define container_name"
    assert (
        service["container_name"] == "dyalog-docs-server"
    ), "Container name must be dyalog-docs-server"


def test_docker_compose_restart_policy():
    """Verify docs-server service has correct restart policy."""
    compose_file = Path("docker-compose.yml")
    config = yaml.safe_load(compose_file.read_text())

    service = config["services"]["docs-server"]
    assert "restart" in service, "docs-server must define restart policy"
    assert (
        service["restart"] == "unless-stopped"
    ), "Restart policy must be unless-stopped"


def test_docker_compose_config_validation():
    """Verify docker-compose.yml validates with docker compose config.

    This is the main acceptance test: docker compose must validate the file.
    """
    # Run docker compose config to validate
    result = subprocess.run(
        ["docker", "compose", "config"],
        capture_output=True,
        text=True,
    )

    # Check that validation succeeded
    assert result.returncode == 0, (
        f"docker compose config failed with return code {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    # Should output valid YAML
    try:
        yaml.safe_load(result.stdout)
    except yaml.YAMLError as e:
        raise AssertionError(f"docker compose config output is not valid YAML: {e}")
