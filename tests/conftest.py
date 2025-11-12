"""Shared pytest fixtures for all tests."""

import subprocess
import time
import pytest
import requests


@pytest.fixture(scope="session")
def docker_container():
    """Start docker compose container for tests, tear down after all tests.

    Uses HTTP readiness probe instead of fixed sleep to handle variable
    container startup times (e.g. MkDocs build duration).

    Session scope ensures single container lifecycle across all test modules,
    preventing conflicts when running tests in parallel (pytest -n auto).
    """
    # Start container
    subprocess.run(
        ["docker", "compose", "up", "-d"],
        capture_output=True,
        check=True,
    )

    # Wait for container to be ready using HTTP readiness probe
    base_url = "http://localhost:8080/"
    timeout = 30  # seconds
    start_time = time.time()
    ready = False

    while time.time() - start_time < timeout:
        try:
            response = requests.get(base_url, timeout=2)
            if response.status_code == 200:
                ready = True
                break
        except requests.RequestException:
            # Container not ready yet, continue polling
            pass
        time.sleep(0.5)

    if not ready:
        # Clean up and fail
        subprocess.run(["docker", "compose", "down"], capture_output=True)
        raise RuntimeError(f"Container did not become ready within {timeout}s timeout")

    # Yield to run tests
    yield

    # Tear down container after all tests complete
    subprocess.run(
        ["docker", "compose", "down"],
        capture_output=True,
    )
