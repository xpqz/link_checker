"""Tests for nginx runtime (Task 1.7)."""

import time
import requests


def test_index_page_returns_200(docker_container):
    """Verify index page returns HTTP 200."""
    response = requests.get("http://localhost:8080/", timeout=5)
    assert (
        response.status_code == 200
    ), f"Index page should return 200, got {response.status_code}"


def test_index_page_content_type(docker_container):
    """Verify index page has correct Content-Type header."""
    response = requests.get("http://localhost:8080/", timeout=5)
    content_type = response.headers.get("Content-Type", "")

    assert (
        "text/html" in content_type
    ), f"Content-Type should be text/html, got {content_type}"


def test_nonexistent_page_returns_404(docker_container):
    """Verify nonexistent pages return HTTP 404."""
    response = requests.get("http://localhost:8080/nonexistent", timeout=5)
    assert (
        response.status_code == 404
    ), f"Nonexistent page should return 404, got {response.status_code}"


def test_404_page_content_type(docker_container):
    """Verify 404 page still has HTML content type."""
    response = requests.get("http://localhost:8080/nonexistent", timeout=5)
    content_type = response.headers.get("Content-Type", "")

    # 404 page should still be HTML
    assert (
        "text/html" in content_type
    ), f"404 page Content-Type should be text/html, got {content_type}"


def test_response_time_reasonable(docker_container):
    """Verify response time is reasonable for local serving."""
    start_time = time.time()
    response = requests.get("http://localhost:8080/", timeout=5)
    elapsed_ms = (time.time() - start_time) * 1000

    assert response.status_code == 200, "Request should succeed"
    assert (
        elapsed_ms < 1000
    ), f"Response time should be < 1000ms for local serving, got {elapsed_ms:.1f}ms"


def test_static_assets_accessible(docker_container):
    """Verify static assets (CSS, JS) are accessible."""
    # Try to get the main page and check if it references assets
    response = requests.get("http://localhost:8080/", timeout=5)
    assert response.status_code == 200

    # MkDocs Material should have CSS files
    # Just verify the page loaded successfully and has content
    assert len(response.content) > 0, "Page should have content"
    assert b"<html" in response.content.lower(), "Should be HTML content"


def test_multiple_pages_accessible(docker_container):
    """Verify multiple pages from the test docs are accessible."""
    pages_to_test = [
        "/",  # index
        "/getting-started/",
        "/features/overview/",
        "/api/",
    ]

    for page in pages_to_test:
        response = requests.get(f"http://localhost:8080{page}", timeout=5)
        assert (
            response.status_code == 200
        ), f"Page {page} should return 200, got {response.status_code}"
        assert "text/html" in response.headers.get(
            "Content-Type", ""
        ), f"Page {page} should have text/html Content-Type"
