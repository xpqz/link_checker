# Link Checker Implementation Plan

## Overview

Build a Docker-based documentation serving system with a multi-process link checker that validates all internal links in MkDocs-generated documentation.

## Part A: Docker Compose Setup for Documentation Serving

### Goal
Serve the MkDocs documentation via nginx in Docker for optimal performance.

### Architecture
Two-stage Docker build:
1. Builder stage: MkDocs renders static HTML
2. Runtime stage: nginx serves the static files

### Implementation Steps

#### A1: Create MkDocs Builder Dockerfile
- Base image: Python slim
- Install MkDocs and required plugins from mkdocs.yml:
  - mkdocs-material
  - mkdocs-macros-plugin
  - mkdocs-monorepo-plugin
  - mkdocs-minify-plugin
  - mkdocs-caption
  - mkdocs-privacy-plugin
  - mkdocs-markdown-tables-extended
- Copy dyalog-docs/ source
- Run `mkdocs build` to generate site/ directory
- Output: Static HTML files ready for serving

#### A2: Create nginx Runtime Dockerfile
- Base image: nginx:alpine (minimal, fast)
- Copy built static files from builder stage
- Configure nginx:
  - Single server block on port 80
  - Root: /usr/share/nginx/html
  - Index: index.html
  - Error page 404: /404.html
  - Enable gzip compression
  - Disable access logging (local development, performance)
- Expose port 80

#### A3: Create docker-compose.yml
- Single service: docs-server
- Build context: ./docker
- Port mapping: 8080:80 (host:container)
- Container name: dyalog-docs-server
- Restart policy: unless-stopped
- No volumes needed (static build)

#### A4: Create docker/ Directory Structure
```
docker/
├── Dockerfile.build    # MkDocs builder
├── Dockerfile.nginx    # nginx runtime
└── nginx.conf          # nginx configuration
```

### Testing Strategy for Part A

**A.T1: Verify MkDocs Build**
- Manually run builder stage
- Confirm site/ directory contains index.html
- Check for build errors/warnings
- Validate all includes resolved

**A.T2: Verify nginx Serving**
- Start container with `docker compose up`
- Curl http://localhost:8080/
- Verify 200 response with HTML content
- Test 404 handling: curl http://localhost:8080/nonexistent
- Check response headers (Content-Type, gzip)

**A.T3: Verify Navigation Links**
- Manually browse to 3-4 pages from different nav sections
- Verify CSS/JS assets load
- Confirm internal links are clickable
- Check browser console for errors

**A.T4: Performance Check**
- Use curl to measure response time for index page
- Should be <50ms for static files
- Verify nginx is serving, not MkDocs dev server

## Part B: Multi-Process Link Checker

### Goal
Spider the Docker-served documentation, validate all internal links, report 404s in YAML format.

### Key Constraint: CPU-Bound, Not IO-Bound
Since we're testing against localhost Docker container:
- Network latency is negligible (loopback interface)
- Bottleneck is CPU for parsing HTML, matching URLs
- Solution: Use multiprocessing, not asyncio
- Target: Saturate available CPU cores

### Architecture

#### B1: Core Components

**B1.1: Page Fetcher (link_checker/fetcher.py)**
- Function: `fetch_page(url: str) -> tuple[int, str, str]`
- Returns: (status_code, content_type, body)
- Uses requests library (simple, synchronous)
- Timeout: 5 seconds
- User-Agent: "Dyalog Link Checker/0.1.0"

**B1.2: Link Extractor (link_checker/extractor.py)**
- Function: `extract_links(base_url: str, html: str) -> set[str]`
- Parse HTML with html.parser (stdlib, fast enough)
- Extract from:
  - `<a href="...">`
  - `<link href="...">` (stylesheets)
  - `<script src="...">` (JavaScript)
- Filter to internal links only:
  - Relative URLs
  - Same-domain absolute URLs
- Normalize:
  - Remove fragments (#anchor)
  - Remove query strings (optional: configurable)
  - Resolve relative paths to absolute URLs
  - Deduplicate
- Return set of normalized URLs

**B1.3: Navigation Validator (link_checker/nav_validator.py)**
- Function: `validate_nav(mkdocs_yml_path: str) -> list[str]`
- Parse mkdocs.yml to extract nav structure
- Return list of all internal links defined in nav
- Uses PyYAML
- Handles nested nav sections
- Handles !include directives (monorepo plugin)

**B1.4: Link Validator (link_checker/validator.py)**
- Function: `validate_link(url: str) -> dict`
- Check if URL returns 2xx or 3xx
- Return: `{"url": str, "status": int, "source": str}`
- Handle redirects: follow once, report final status

**B1.5: Result Reporter (link_checker/reporter.py)**
- Function: `generate_report(results: dict, output_path: str) -> None`
- Output YAML structure:
```yaml
summary:
  total_pages: 150
  total_links: 1205
  broken_links: 3
  pages_with_broken_links: 2
broken_links:
  - page: "/language-reference-guide/intro/"
    broken:
      - url: "/nonexistent-page/"
        status: 404
  - page: "/programming-reference-guide/operators/"
    broken:
      - url: "/missing/reference/"
        status: 404
navigation_issues:
  - nav_entry: "Core Reference > Programming"
    url: "/programming-reference-guide/index/"
    status: 404
```

#### B2: Orchestration (link_checker/link_checker.py)

**B2.1: Discovery Phase (Single-Process)**
1. Start at base URL: http://localhost:8080/
2. Fetch index page
3. Extract all links
4. Build queue of URLs to check
5. Use BFS to discover all pages:
   - visited = set()
   - queue = deque([base_url])
   - while queue:
     - url = queue.popleft()
     - if url in visited: continue
     - fetch and extract links
     - add new internal links to queue
6. Result: Complete set of all pages on site

**B2.2: Validation Phase (Multi-Process)**
1. Take discovered URL set
2. Create worker pool: `multiprocessing.Pool(processes=cpu_count())`
3. Use `pool.map()` to validate all links in parallel
4. Each worker:
   - Takes URL from queue
   - Fetches page
   - Extracts and validates links
   - Returns results
5. Collect results in main process

**B2.3: Navigation Check Phase (Single-Process)**
1. Parse all mkdocs.yml files
2. Extract nav URLs
3. Validate each nav URL exists in discovered pages
4. Report any nav entries pointing to non-existent pages

**B2.4: Reporting Phase**
1. Aggregate results by source page
2. Generate YAML report
3. Write to link_check_report.yaml
4. Print summary to stdout

### Data Structures

**DiscoveredPage**
```python
@dataclass
class DiscoveredPage:
    url: str
    status_code: int
    links: set[str]  # All extracted links
```

**BrokenLink**
```python
@dataclass
class BrokenLink:
    source_page: str
    target_url: str
    status_code: int
```

**ValidationResult**
```python
@dataclass
class ValidationResult:
    pages_checked: list[DiscoveredPage]
    broken_links: list[BrokenLink]
    nav_issues: list[dict]
```

### Testing Strategy for Part B

**B.T1: Test Link Extractor**
Unit tests with HTML fixtures:
- Extract links from simple HTML
- Handle relative URLs
- Handle absolute URLs
- Filter external links
- Normalize URLs (remove fragments)
- Handle malformed HTML gracefully

**B.T2: Test Navigation Validator**
Unit tests with mkdocs.yml fixtures:
- Parse simple nav structure
- Parse nested nav (2-3 levels)
- Handle !include directives
- Extract all unique URLs
- Handle missing files gracefully

**B.T3: Test Page Fetcher**
Integration test against running Docker container:
- Fetch valid page returns 200
- Fetch invalid page returns 404
- Timeout handling
- Connection error handling

**B.T4: Test Link Validator**
Integration test:
- Valid internal link returns success
- Broken internal link returns 404
- Redirect handling (301/302)

**B.T5: Test End-to-End Discovery**
Integration test with minimal test site:
- Create 3-page test site in Docker
- Run discovery phase
- Verify all 3 pages discovered
- Verify links between pages extracted

**B.T6: Test Multi-Process Validation**
Integration test:
- Create test site with 20+ pages
- Run validation with 2 processes
- Verify all pages checked
- Verify broken links detected
- Check for race conditions

**B.T7: Test Report Generation**
Unit test with fixture data:
- Generate YAML from test results
- Verify structure matches specification
- Verify YAML is valid
- Verify summary counts are correct

**B.T8: Test Full Pipeline**
End-to-end integration test:
- Start Docker container
- Run full link checker
- Inject known broken link
- Verify broken link appears in report
- Verify summary counts
- Verify report file created

### Performance Considerations

**CPU vs IO**
- Loopback network is ~40 Gbps (kernel memory copy)
- Typical page fetch: <1ms
- HTML parsing: 1-5ms per page
- Bottleneck: CPU, not network
- Use `multiprocessing.Pool` to saturate all cores

**Process Pool Sizing**
- Default: `cpu_count()` (typically 4-16)
- Small sites (<100 pages): 2-4 processes sufficient
- Large sites (>1000 pages): `cpu_count()` or `cpu_count() * 2`
- Configurable via CLI argument

**Memory Management**
- Avoid keeping all page content in memory
- Process pages in batches if site is huge (>10k pages)
- Each worker operates independently
- Main process only stores URLs and results

**Optimizations**
1. Discovery phase: Single-threaded BFS is sufficient (fast enough)
2. Validation phase: Multi-process for parallel fetching
3. Cache DNS lookups (not needed for localhost)
4. Don't parse CSS/JS files (only extract their URLs)
5. Skip binary files (PDFs, images) - check Content-Type

### CLI Interface

```bash
uv run link_checker/link_checker.py \
  --base-url http://localhost:8080 \
  --output link_check_report.yaml \
  --processes 4 \
  --mkdocs-config dyalog-docs/mkdocs.yml \
  --verbose
```

**Arguments**
- `--base-url`: Base URL of documentation site (required)
- `--output`: Output YAML file path (default: link_check_report.yaml)
- `--processes`: Number of worker processes (default: cpu_count())
- `--mkdocs-config`: Path to main mkdocs.yml (required for nav validation)
- `--verbose`: Enable debug logging
- `--no-nav-check`: Skip navigation validation

### Error Handling

**Robustness**
- Timeouts: 5 seconds per request
- Retry logic: 1 retry on connection errors
- Invalid HTML: Log warning, extract what we can
- Invalid YAML: Fail fast with clear error message
- Worker crashes: Pool automatically restarts worker

**Exit Codes**
- 0: Success, no broken links
- 1: Broken links found
- 2: Configuration error
- 3: Docker container not accessible

## Implementation Order

1. **A1-A4**: Docker setup (establish test environment)
2. **A.T1-A.T4**: Verify Docker setup works
3. **B1.1**: Implement fetcher
4. **B.T3**: Test fetcher
5. **B1.2**: Implement extractor
6. **B.T1**: Test extractor
7. **B1.3**: Implement nav validator
8. **B.T2**: Test nav validator
9. **B2.1**: Implement discovery phase
10. **B.T5**: Test discovery
11. **B1.4**: Implement link validator
12. **B.T4**: Test validator
13. **B2.2**: Implement multi-process validation
14. **B.T6**: Test multi-process validation
15. **B1.5**: Implement reporter
16. **B.T7**: Test reporter
17. **B2.3-B2.4**: Implement nav check and final orchestration
18. **B.T8**: End-to-end test

## Dependencies

**Docker Setup (Part A)**
- mkdocs
- mkdocs-material
- mkdocs-macros-plugin
- mkdocs-monorepo-plugin
- mkdocs-minify-plugin
- mkdocs-caption
- mkdocs-privacy-plugin
- mkdocs-markdown-tables-extended

**Link Checker (Part B)**
- requests (HTTP client)
- pyyaml (YAML output)
- html.parser (stdlib, HTML parsing)
- multiprocessing (stdlib, parallel processing)
- argparse (stdlib, CLI)
- dataclasses (stdlib, data structures)
- pathlib (stdlib, file handling)

## Success Criteria

**Part A Complete When:**
- `docker compose up` starts nginx serving documentation
- Site accessible at http://localhost:8080/
- All pages render correctly
- CSS and JavaScript load
- Navigation works
- Build time <2 minutes
- Container size <200MB

**Part B Complete When:**
- Link checker discovers all pages
- Validates all internal links
- Reports broken links in YAML format
- Validates navigation entries
- Processes 100+ pages in <30 seconds
- All tests pass
- No false positives or false negatives
- Clean code, properly documented
