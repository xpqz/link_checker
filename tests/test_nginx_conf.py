"""Tests for nginx configuration (Task 1.4)."""

import subprocess
from pathlib import Path


def test_nginx_conf_exists():
    """Verify nginx.conf exists in docker/ directory."""
    nginx_conf = Path("docker/nginx.conf")
    assert nginx_conf.exists(), "docker/nginx.conf must exist"
    assert nginx_conf.is_file(), "docker/nginx.conf must be a file"


def test_nginx_conf_has_events_section():
    """Verify nginx.conf has required events section."""
    nginx_conf = Path("docker/nginx.conf")
    content = nginx_conf.read_text()

    assert "events" in content, "nginx.conf must have events section"


def test_nginx_conf_has_http_section():
    """Verify nginx.conf has http section."""
    nginx_conf = Path("docker/nginx.conf")
    content = nginx_conf.read_text()

    assert "http" in content, "nginx.conf must have http section"


def test_nginx_conf_has_server_block():
    """Verify nginx.conf has server block."""
    nginx_conf = Path("docker/nginx.conf")
    content = nginx_conf.read_text()

    assert "server" in content, "nginx.conf must have server block"


def test_nginx_conf_listens_on_port_80():
    """Verify nginx.conf configures server to listen on port 80."""
    nginx_conf = Path("docker/nginx.conf")
    content = nginx_conf.read_text()

    assert (
        "listen 80" in content or "listen  80" in content
    ), "nginx.conf must configure server to listen on port 80"


def test_nginx_conf_sets_root_directory():
    """Verify nginx.conf sets root to /usr/share/nginx/html."""
    nginx_conf = Path("docker/nginx.conf")
    content = nginx_conf.read_text()

    assert (
        "/usr/share/nginx/html" in content
    ), "nginx.conf must set root to /usr/share/nginx/html"


def test_nginx_conf_sets_index():
    """Verify nginx.conf sets index to index.html."""
    nginx_conf = Path("docker/nginx.conf")
    content = nginx_conf.read_text()

    assert "index.html" in content, "nginx.conf must set index to index.html"


def test_nginx_conf_has_error_page_config():
    """Verify nginx.conf configures 404 error page."""
    nginx_conf = Path("docker/nginx.conf")
    content = nginx_conf.read_text()

    assert (
        "404" in content or "error_page" in content
    ), "nginx.conf should configure 404 error handling"


def test_nginx_conf_syntax_validation():
    """Verify nginx.conf has valid syntax using nginx -t in container.

    This is the main acceptance test: nginx must validate the configuration.
    """
    # Run nginx -t in container to validate configuration
    # Need to override entrypoint since default runs nginx in foreground
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "nginx",
            "dyalog-docs-test:latest",
            "-t",
            "-c",
            "/etc/nginx/nginx.conf",
        ],
        capture_output=True,
        text=True,
    )

    # Check that validation succeeded
    assert result.returncode == 0, (
        f"nginx configuration validation failed with return code {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    # Verify success message in output
    assert (
        "syntax is ok" in result.stderr.lower()
        or "test is successful" in result.stderr.lower()
    ), f"nginx -t did not report success. Output:\n{result.stderr}"
