"""Tests for Docker build stage (Task 1.6)."""

import subprocess
import re


def test_docker_compose_build_succeeds():
    """Verify docker compose build completes successfully.

    This is the main acceptance test: the build must succeed.
    """
    # Run docker compose build
    result = subprocess.run(
        ["docker", "compose", "build"],
        capture_output=True,
        text=True,
    )

    # Check that build succeeded
    assert result.returncode == 0, (
        f"docker compose build failed with return code {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


def test_docker_compose_build_no_errors():
    """Verify docker compose build produces no error messages."""
    # Run docker compose build
    result = subprocess.run(
        ["docker", "compose", "build"],
        capture_output=True,
        text=True,
    )

    # Check stderr for error indicators
    stderr_lower = result.stderr.lower()

    # Should not contain ERROR (but may contain error_log which is ok)
    error_pattern = r"\berror\b"
    errors = re.findall(error_pattern, stderr_lower, re.IGNORECASE)
    # Filter out acceptable error references like error_log
    actual_errors = [
        e
        for e in errors
        if "error_log"
        not in stderr_lower[
            max(0, stderr_lower.find(e) - 20) : stderr_lower.find(e) + 20
        ]
    ]

    assert not actual_errors, f"Build stderr contains error messages:\n{result.stderr}"


def test_docker_image_exists():
    """Verify Docker image exists after build."""
    # First ensure build has run
    subprocess.run(
        ["docker", "compose", "build"],
        capture_output=True,
    )

    # Check that image exists
    result = subprocess.run(
        ["docker", "images", "-q", "claudews-docs-server"],
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip(), "Docker image 'claudews-docs-server' was not created"


def test_docker_image_size_reasonable():
    """Verify Docker image size is reasonable (<250MB).

    A bloated image suggests unnecessary dependencies or build artifacts.
    The threshold is set to 250MB to accommodate nginx:alpine + Python + MkDocs plugins.
    """
    # First ensure build has run
    subprocess.run(
        ["docker", "compose", "build"],
        capture_output=True,
    )

    # Get image size
    result = subprocess.run(
        ["docker", "images", "claudews-docs-server", "--format", "{{.Size}}"],
        capture_output=True,
        text=True,
    )

    size_str = result.stdout.strip()
    assert size_str, "Could not get image size"

    # Parse size (can be in MB or GB)
    # Format examples: "150MB", "1.5GB"
    match = re.match(r"([\d.]+)([MG]B)", size_str)
    assert match, f"Could not parse size: {size_str}"

    size_value = float(match.group(1))
    size_unit = match.group(2)

    # Convert to MB
    if size_unit == "GB":
        size_mb = size_value * 1024
    else:  # MB
        size_mb = size_value

    assert size_mb < 250, (
        f"Docker image is too large: {size_str} ({size_mb:.1f}MB). "
        f"Expected < 250MB. This suggests unnecessary dependencies or build artifacts."
    )
