"""Tests for Docker directory structure (Task 1.1)."""

from pathlib import Path


def test_docker_directory_exists():
    """Verify docker/ directory exists."""
    docker_dir = Path("docker")
    assert docker_dir.exists(), "docker/ directory must exist"
    assert docker_dir.is_dir(), "docker/ must be a directory"


def test_dockerfile_exists():
    """Verify Dockerfile exists in docker/ directory."""
    dockerfile = Path("docker/Dockerfile")
    assert dockerfile.exists(), "docker/Dockerfile must exist"
    assert dockerfile.is_file(), "docker/Dockerfile must be a file"


def test_nginx_conf_exists():
    """Verify nginx.conf exists in docker/ directory."""
    nginx_conf = Path("docker/nginx.conf")
    assert nginx_conf.exists(), "docker/nginx.conf must exist"
    assert nginx_conf.is_file(), "docker/nginx.conf must be a file"


def test_docker_directory_structure_complete():
    """Verify complete directory structure matches plan.

    This test verifies that the docker/ directory contains exactly
    the expected files: Dockerfile and nginx.conf.
    """
    docker_dir = Path("docker")
    expected_files = {"Dockerfile", "nginx.conf"}

    # Get actual files (excluding hidden files and __pycache__)
    actual_files = {
        f.name
        for f in docker_dir.iterdir()
        if f.is_file() and not f.name.startswith(".")
    }

    assert actual_files == expected_files, (
        f"docker/ directory should contain exactly {expected_files}, "
        f"but found {actual_files}"
    )
