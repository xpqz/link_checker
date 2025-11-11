"""Tests for Dockerfile (Task 1.3)."""

import subprocess
from pathlib import Path


def test_dockerfile_exists():
    """Verify Dockerfile exists in docker/ directory."""
    dockerfile = Path("docker/Dockerfile")
    assert dockerfile.exists(), "docker/Dockerfile must exist"
    assert dockerfile.is_file(), "docker/Dockerfile must be a file"


def test_dockerfile_uses_nginx_alpine():
    """Verify Dockerfile uses nginx:alpine as base."""
    dockerfile = Path("docker/Dockerfile")
    content = dockerfile.read_text()
    content_lower = content.lower()

    assert "from nginx" in content_lower, "Dockerfile must use nginx as base image"
    assert (
        "alpine" in content_lower
    ), "Dockerfile should use nginx:alpine for smaller image"


def test_dockerfile_installs_python():
    """Verify Dockerfile installs Python and pip."""
    dockerfile = Path("docker/Dockerfile")
    content = dockerfile.read_text()

    # Check for Python installation (apk add python on alpine)
    assert "python" in content.lower(), "Dockerfile must install Python"
    assert "pip" in content.lower(), "Dockerfile must install pip"


def test_dockerfile_installs_requirements():
    """Verify Dockerfile installs from requirements.txt."""
    dockerfile = Path("docker/Dockerfile")
    content = dockerfile.read_text()

    # Check that requirements.txt is copied and used
    assert "requirements.txt" in content, "Dockerfile must reference requirements.txt"
    # Accept both pip and pip3
    assert (
        "pip install" in content or "pip3 install" in content
    ), "Dockerfile must install Python packages with pip"


def test_dockerfile_copies_nginx_conf():
    """Verify Dockerfile copies nginx configuration."""
    dockerfile = Path("docker/Dockerfile")
    content = dockerfile.read_text()

    assert "nginx.conf" in content, "Dockerfile must copy nginx.conf configuration file"


def test_dockerfile_has_entrypoint():
    """Verify Dockerfile has an entrypoint script."""
    dockerfile = Path("docker/Dockerfile")
    content = dockerfile.read_text()

    # Check for entrypoint script
    assert (
        "entrypoint" in content.lower() or "cmd" in content.upper()
    ), "Dockerfile must define an ENTRYPOINT or CMD"


def test_dockerfile_exposes_port_80():
    """Verify Dockerfile exposes port 80."""
    dockerfile = Path("docker/Dockerfile")
    content = dockerfile.read_text()

    assert (
        "EXPOSE 80" in content or "EXPOSE  80" in content
    ), "Dockerfile must expose port 80"


def test_docker_build_succeeds():
    """Verify Docker build completes without errors.

    This is the main acceptance test: the Docker image must build successfully.
    """
    # Run docker build command
    result = subprocess.run(
        ["docker", "build", "-f", "docker/Dockerfile", "-t", "dyalog-docs-test", "."],
        capture_output=True,
        text=True,
    )

    # Check that build succeeded
    assert result.returncode == 0, (
        f"Docker build failed with return code {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    # Verify image was created
    verify_result = subprocess.run(
        ["docker", "images", "-q", "dyalog-docs-test"],
        capture_output=True,
        text=True,
    )
    assert (
        verify_result.stdout.strip()
    ), "Docker image 'dyalog-docs-test' was not created"
