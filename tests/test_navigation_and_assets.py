"""Tests for navigation and assets (Task 1.8).

These tests verify that:
- Navigation links work correctly
- CSS assets load and are served with correct content type
- JavaScript assets load and are served with correct content type
- Pages render with proper styling
- No critical resources return 404 errors
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def test_index_page_has_navigation_links(docker_container):
    """Verify index page contains navigation links."""
    response = requests.get("http://localhost:8080/", timeout=5)
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")

    # Find navigation links - Material theme uses nav element
    nav_links = soup.find_all("a", href=True)
    assert len(nav_links) > 0, "Page should contain navigation links"


def test_internal_navigation_links_accessible(docker_container):
    """Verify internal navigation links are accessible and return 200.

    This test:
    1. Gets the index page
    2. Extracts all internal navigation links
    3. Verifies each link returns HTTP 200
    """
    base_url = "http://localhost:8080/"
    response = requests.get(base_url, timeout=5)
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")

    # Find all links in the page
    links = soup.find_all("a", href=True)

    # Extract internal links (relative or same domain)
    internal_links = []
    for link in links:
        href = link["href"]
        # Skip anchors, external links, javascript, mailto
        if (
            href.startswith("#")
            or href.startswith("javascript:")
            or href.startswith("mailto:")
        ):
            continue
        if href.startswith("http") and not href.startswith(base_url):
            continue

        # Convert relative to absolute
        full_url = urljoin(base_url, href)
        # Remove fragment
        full_url = full_url.split("#")[0]
        internal_links.append(full_url)

    # Remove duplicates
    internal_links = list(set(internal_links))

    # Verify we found some internal links
    assert len(internal_links) > 0, "Should find internal navigation links"

    # Test each internal link
    failed_links = []
    for url in internal_links:
        try:
            link_response = requests.get(url, timeout=5)
            if link_response.status_code != 200:
                failed_links.append((url, link_response.status_code))
        except requests.RequestException as e:
            failed_links.append((url, str(e)))

    assert (
        len(failed_links) == 0
    ), f"All internal links should return 200. Failed links: {failed_links}"


def test_specific_navigation_links_work(docker_container):
    """Test specific navigation links from mkdocs.yml nav structure."""
    base_url = "http://localhost:8080"

    # These are from the mkdocs.yml nav structure
    expected_pages = [
        "/",
        "/getting-started/",
        "/features/overview/",
        "/features/advanced/",
        "/api/",
    ]

    for page_path in expected_pages:
        url = f"{base_url}{page_path}"
        response = requests.get(url, timeout=5)
        assert (
            response.status_code == 200
        ), f"Navigation link {page_path} should be accessible, got {response.status_code}"
        assert "text/html" in response.headers.get("Content-Type", "")


def test_css_assets_load_correctly(docker_container):
    """Verify CSS assets load and have correct content type.

    This test:
    1. Gets the index page
    2. Extracts CSS link references
    3. Verifies each CSS file returns 200 with text/css content type
    """
    base_url = "http://localhost:8080/"
    response = requests.get(base_url, timeout=5)
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")

    # Find all CSS link tags
    css_links = soup.find_all("link", rel="stylesheet", href=True)

    assert len(css_links) > 0, "Page should reference CSS files"

    failed_css = []
    for link in css_links:
        href = link["href"]
        css_url = urljoin(base_url, href)

        # Skip external CDN links
        if not css_url.startswith(base_url):
            continue

        try:
            css_response = requests.get(css_url, timeout=5)
            if css_response.status_code != 200:
                failed_css.append((css_url, css_response.status_code, "wrong status"))
                continue

            content_type = css_response.headers.get("Content-Type", "")
            if "text/css" not in content_type:
                failed_css.append(
                    (
                        css_url,
                        css_response.status_code,
                        f"wrong content-type: {content_type}",
                    )
                )

        except requests.RequestException as e:
            failed_css.append((css_url, 0, str(e)))

    assert (
        len(failed_css) == 0
    ), f"All CSS assets should load correctly. Failed: {failed_css}"


def test_javascript_assets_load_correctly(docker_container):
    """Verify JavaScript assets load and have correct content type.

    This test:
    1. Gets the index page
    2. Extracts JavaScript script references
    3. Verifies each JS file returns 200 with correct content type
    """
    base_url = "http://localhost:8080/"
    response = requests.get(base_url, timeout=5)
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")

    # Find all script tags with src
    script_tags = soup.find_all("script", src=True)

    assert len(script_tags) > 0, "Page should reference JavaScript files"

    failed_js = []
    for script in script_tags:
        src = script["src"]
        js_url = urljoin(base_url, src)

        # Skip external CDN links
        if not js_url.startswith(base_url):
            continue

        try:
            js_response = requests.get(js_url, timeout=5)
            if js_response.status_code != 200:
                failed_js.append((js_url, js_response.status_code, "wrong status"))
                continue

            content_type = js_response.headers.get("Content-Type", "")
            # JavaScript can be served as application/javascript or text/javascript
            if "javascript" not in content_type:
                failed_js.append(
                    (
                        js_url,
                        js_response.status_code,
                        f"wrong content-type: {content_type}",
                    )
                )

        except requests.RequestException as e:
            failed_js.append((js_url, 0, str(e)))

    assert (
        len(failed_js) == 0
    ), f"All JavaScript assets should load correctly. Failed: {failed_js}"


def test_page_contains_expected_styling_elements(docker_container):
    """Verify pages contain expected Material theme styling elements.

    This confirms CSS is being applied by checking for Material theme classes.
    """
    response = requests.get("http://localhost:8080/", timeout=5)
    assert response.status_code == 200

    content = response.text

    # Material for MkDocs should have these characteristics
    expected_indicators = [
        "md-",  # Material Design class prefix
        "material",  # Theme name
    ]

    found_indicators = []
    for indicator in expected_indicators:
        if indicator in content:
            found_indicators.append(indicator)

    assert (
        len(found_indicators) > 0
    ), f"Page should contain Material theme styling indicators. Expected one of: {expected_indicators}"


def test_no_404_errors_for_critical_resources(docker_container):
    """Verify no critical resources (CSS, JS, images) return 404.

    This simulates checking browser console for loading errors.
    """
    base_url = "http://localhost:8080/"
    response = requests.get(base_url, timeout=5)
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")

    # Collect all resource URLs
    resources = []

    # CSS files
    for link in soup.find_all("link", rel="stylesheet", href=True):
        resources.append(("css", urljoin(base_url, link["href"])))

    # JavaScript files
    for script in soup.find_all("script", src=True):
        resources.append(("js", urljoin(base_url, script["src"])))

    # Images
    for img in soup.find_all("img", src=True):
        resources.append(("img", urljoin(base_url, img["src"])))

    # Filter to only local resources
    local_resources = [
        (res_type, url) for res_type, url in resources if url.startswith(base_url)
    ]

    assert len(local_resources) > 0, "Should find local resources to test"

    # Check each resource
    failed_resources = []
    for res_type, url in local_resources:
        try:
            res_response = requests.get(url, timeout=5)
            if res_response.status_code == 404:
                failed_resources.append((res_type, url, 404))
        except requests.RequestException as e:
            failed_resources.append((res_type, url, str(e)))

    assert (
        len(failed_resources) == 0
    ), f"No critical resources should return 404. Failed: {failed_resources}"


def test_navigation_between_pages_works(docker_container):
    """Verify we can navigate from index to other pages following links.

    This simulates clicking navigation links in the browser.
    """
    base_url = "http://localhost:8080/"

    # Start at index
    response = requests.get(base_url, timeout=5)
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")

    # Find Getting Started link (from the content)
    getting_started_link = None
    for link in soup.find_all("a", href=True):
        if "getting-started" in link["href"]:
            getting_started_link = urljoin(base_url, link["href"])
            break

    assert getting_started_link is not None, "Should find link to getting-started page"

    # Navigate to Getting Started page
    gs_response = requests.get(getting_started_link, timeout=5)
    assert gs_response.status_code == 200, "Getting Started page should load"
    assert "text/html" in gs_response.headers.get("Content-Type", "")


def test_multiple_page_navigation_from_different_sections(docker_container):
    """Verify navigation works from different sections of the site.

    Tests navigation from:
    - Home to Features
    - Features/Overview to API
    - API back to Home
    """
    base_url = "http://localhost:8080"

    navigation_tests = [
        ("/", "/features/overview/", "Home to Features Overview"),
        ("/features/overview/", "/api/", "Features to API"),
        ("/api/", "/", "API to Home"),
    ]

    for start_path, target_path, description in navigation_tests:
        # Get start page
        start_url = f"{base_url}{start_path}"
        response = requests.get(start_url, timeout=5)
        assert response.status_code == 200, f"{description}: start page should load"

        # Verify target page is accessible
        target_url = f"{base_url}{target_path}"
        target_response = requests.get(target_url, timeout=5)
        assert (
            target_response.status_code == 200
        ), f"{description}: target page should be accessible"
