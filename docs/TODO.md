# Link Checker Implementation TODO

This document breaks down the implementation plan into discrete, testable tasks.

## Epic 1: Docker-Based Documentation Serving

### Task 1.1: Create Docker Directory Structure
- [ ] Create `docker/` directory
- [ ] Create placeholder files: `Dockerfile`, `nginx.conf`
- [ ] Verify directory structure matches plan

**Test:** Directory exists with correct structure

**Acceptance:** `ls docker/` shows Dockerfile and nginx.conf

---

### Task 1.2: Create MkDocs Requirements File
- [ ] Create `docker/requirements.txt` with MkDocs dependencies:
  - mkdocs
  - mkdocs-material
  - mkdocs-macros-plugin
  - mkdocs-monorepo-plugin
  - mkdocs-minify-plugin
  - mkdocs-caption
  - mkdocs-privacy-plugin
  - mkdocs-markdown-tables-extended

**Test:** File contains all required dependencies

**Acceptance:** `cat docker/requirements.txt` shows all 8 dependencies

---

### Task 1.3: Create Multi-Stage Dockerfile
- [ ] Define builder stage with Python slim base
- [ ] Install MkDocs and plugins from requirements.txt
- [ ] Copy dyalog-docs/ directory
- [ ] Run `mkdocs build` to generate static site
- [ ] Define runtime stage with nginx:alpine base
- [ ] Copy built site from builder stage to /usr/share/nginx/html
- [ ] Copy nginx.conf to container
- [ ] Expose port 80

**Test:** `docker build -f docker/Dockerfile -t dyalog-docs-test .` succeeds

**Acceptance:** Docker build completes without errors, produces image

---

### Task 1.4: Create nginx Configuration
- [ ] Create `docker/nginx.conf`
- [ ] Configure server block on port 80
- [ ] Set root to /usr/share/nginx/html
- [ ] Set index to index.html
- [ ] Configure 404 error page
- [ ] Enable gzip compression
- [ ] Disable access logging

**Test:** nginx -t validates configuration (in container)

**Acceptance:** Configuration syntax is valid

---

### Task 1.5: Create docker-compose.yml
- [ ] Create `docker-compose.yml` in project root
- [ ] Define service: docs-server
- [ ] Set build context to ./docker
- [ ] Map port 8080:80
- [ ] Set container name: dyalog-docs-server
- [ ] Set restart policy: unless-stopped

**Test:** `docker compose config` validates YAML

**Acceptance:** Compose file is syntactically correct

---

### Task 1.6: Test MkDocs Build Stage
- [ ] Build Docker image: `docker compose build`
- [ ] Verify build completes successfully
- [ ] Check build logs for warnings/errors
- [ ] Verify image size is reasonable (<200MB)

**Test:** Manual docker compose build

**Acceptance:**
- Build succeeds
- No error messages
- Image exists in `docker images`

---

### Task 1.7: Test nginx Runtime
- [ ] Start container: `docker compose up -d`
- [ ] Test index page: `curl -I http://localhost:8080/`
- [ ] Verify 200 response
- [ ] Verify Content-Type: text/html
- [ ] Test 404 handling: `curl -I http://localhost:8080/nonexistent`
- [ ] Verify 404 response
- [ ] Check gzip encoding in headers

**Test:** Manual curl commands

**Acceptance:**
- Index returns 200
- Invalid path returns 404
- Headers show gzip encoding
- Response time <50ms

---

### Task 1.8: Test Navigation and Assets
- [ ] Manually visit http://localhost:8080/ in browser
- [ ] Verify index page loads
- [ ] Click 3-4 nav links from different sections
- [ ] Verify CSS loads correctly
- [ ] Verify JavaScript loads correctly
- [ ] Check browser console for errors

**Test:** Manual browser testing

**Acceptance:**
- All pages render correctly
- No console errors
- Navigation works
- Styling applied correctly

---

### Task 1.9: Document Docker Setup
- [ ] Add Docker usage section to README.md
- [ ] Document how to build: `docker compose build`
- [ ] Document how to start: `docker compose up -d`
- [ ] Document how to stop: `docker compose down`
- [ ] Document how to access: http://localhost:8080/

**Test:** Follow documentation instructions

**Acceptance:** Documentation is clear and accurate

---

## Epic 2: Link Checker Implementation

### Task 2.1: Add Python Dependencies
- [ ] Add `requests` dependency: `uv add requests`
- [ ] Add `pyyaml` dependency: `uv add pyyaml`
- [ ] Verify dependencies installed
- [ ] Run `uv sync` to ensure lockfile updated

**Test:** `uv run python -c "import requests; import yaml"`

**Acceptance:** Imports succeed without errors

---

### Task 2.2: Create Link Checker Module Structure
- [ ] Create `link_checker/fetcher.py`
- [ ] Create `link_checker/extractor.py`
- [ ] Create `link_checker/nav_validator.py`
- [ ] Create `link_checker/validator.py`
- [ ] Create `link_checker/reporter.py`
- [ ] Create `link_checker/link_checker.py`
- [ ] Add module docstrings to each file

**Test:** `ls link_checker/*.py` shows all files

**Acceptance:** All module files exist with docstrings

---

### Task 2.3: Implement Page Fetcher
- [ ] Create `fetch_page(url: str) -> tuple[int, str, str]` function
- [ ] Use requests.get with 5-second timeout
- [ ] Set User-Agent header: "Dyalog Link Checker/0.1.0"
- [ ] Return (status_code, content_type, body)
- [ ] Handle connection errors gracefully
- [ ] Add type hints
- [ ] Add docstring

**Test:** Write `tests/test_fetcher.py`
- Test successful fetch returns 200
- Test invalid URL raises exception
- Test timeout handling

**Acceptance:** All fetcher tests pass

---

### Task 2.4: Write Fetcher Tests
- [ ] Create `tests/test_fetcher.py`
- [ ] Test: fetch_page returns 200 for valid page (requires Docker running)
- [ ] Test: fetch_page returns 404 for invalid page
- [ ] Test: fetch_page handles timeout
- [ ] Test: fetch_page handles connection error
- [ ] Test: fetch_page sets correct User-Agent

**Test:** `uv run pytest tests/test_fetcher.py -v`

**Acceptance:** All 5 tests pass

---

### Task 2.5: Implement Link Extractor
- [ ] Create `extract_links(base_url: str, html: str) -> set[str]` function
- [ ] Parse HTML with html.parser (stdlib)
- [ ] Extract href from `<a>` tags
- [ ] Extract href from `<link>` tags
- [ ] Extract src from `<script>` tags
- [ ] Filter to internal links only (same domain or relative)
- [ ] Normalize URLs: remove fragments, resolve relative paths
- [ ] Return deduplicated set
- [ ] Add type hints and docstring

**Test:** Write `tests/test_extractor.py` (unit tests with HTML fixtures)

**Acceptance:** Extractor implementation complete, ready for testing

---

### Task 2.6: Write Link Extractor Tests
- [ ] Create `tests/test_extractor.py`
- [ ] Test: extract simple anchor links
- [ ] Test: extract relative URLs
- [ ] Test: extract absolute same-domain URLs
- [ ] Test: filter external URLs
- [ ] Test: normalize URLs (remove fragments)
- [ ] Test: resolve relative paths correctly
- [ ] Test: handle malformed HTML gracefully
- [ ] Test: deduplicate links

**Test:** `uv run pytest tests/test_extractor.py -v`

**Acceptance:** All 8 tests pass

---

### Task 2.7: Implement Navigation Validator
- [ ] Create `extract_nav_links(mkdocs_yml_path: str) -> list[str]` function
- [ ] Parse mkdocs.yml with PyYAML
- [ ] Extract nav structure
- [ ] Handle nested nav sections (recursive)
- [ ] Handle !include directives (monorepo plugin)
- [ ] Return list of all internal URLs from nav
- [ ] Add type hints and docstring
- [ ] Handle missing files gracefully with clear error

**Test:** Write `tests/test_nav_validator.py`

**Acceptance:** Nav validator implementation complete

---

### Task 2.8: Write Navigation Validator Tests
- [ ] Create `tests/test_nav_validator.py`
- [ ] Create fixture: simple mkdocs.yml in tmp/
- [ ] Test: parse simple flat nav structure
- [ ] Test: parse nested nav (2-3 levels)
- [ ] Test: extract all unique URLs
- [ ] Test: handle missing mkdocs.yml file
- [ ] Test: handle invalid YAML syntax

**Test:** `uv run pytest tests/test_nav_validator.py -v`

**Acceptance:** All 5 tests pass

---

### Task 2.9: Implement Data Structures
- [ ] Create `link_checker/models.py`
- [ ] Define DiscoveredPage dataclass (url, status_code, links)
- [ ] Define BrokenLink dataclass (source_page, target_url, status_code)
- [ ] Define ValidationResult dataclass (pages_checked, broken_links, nav_issues)
- [ ] Add type hints
- [ ] Add docstrings

**Test:** `uv run python -c "from link_checker.models import *"`

**Acceptance:** Import succeeds, dataclasses defined

---

### Task 2.10: Implement Discovery Phase
- [ ] Create `discover_pages(base_url: str) -> list[DiscoveredPage]` function in link_checker.py
- [ ] Implement BFS algorithm with deque
- [ ] Track visited URLs to avoid cycles
- [ ] Use fetch_page and extract_links
- [ ] Only follow internal links
- [ ] Return list of DiscoveredPage objects
- [ ] Add type hints and docstring
- [ ] Add logging (use Python logging module)

**Test:** Write basic unit test, prepare for integration test

**Acceptance:** Discovery implementation complete

---

### Task 2.11: Create Test Site Fixture
- [ ] Create `tests/fixtures/test_site/` directory
- [ ] Create minimal mkdocs.yml (3 pages)
- [ ] Create 3 markdown pages with cross-links
- [ ] Add 1 intentionally broken link
- [ ] Create Dockerfile to serve this test site
- [ ] Document how to build/run test site

**Test:** Build and run test site, verify 3 pages accessible

**Acceptance:** Test site serves correctly on different port

---

### Task 2.12: Write Discovery Phase Tests
- [ ] Create `tests/test_discovery.py`
- [ ] Test: discover all pages from test site (requires test site Docker running)
- [ ] Test: verify correct number of pages discovered
- [ ] Test: verify links extracted from each page
- [ ] Test: verify no external links followed
- [ ] Test: handle pages with no links

**Test:** `uv run pytest tests/test_discovery.py -v`

**Acceptance:** All discovery tests pass

---

### Task 2.13: Implement Link Validator
- [ ] Create `validate_link(url: str) -> dict` function in validator.py
- [ ] Use fetch_page internally
- [ ] Check for 2xx or 3xx status codes
- [ ] Follow redirects (use requests with allow_redirects=True)
- [ ] Return dict: {"url": str, "status": int, "final_url": str}
- [ ] Add type hints and docstring

**Test:** Write `tests/test_validator.py`

**Acceptance:** Validator implementation complete

---

### Task 2.14: Write Link Validator Tests
- [ ] Create `tests/test_validator.py`
- [ ] Test: valid link returns success (requires Docker)
- [ ] Test: broken link returns 404
- [ ] Test: redirect handling (301/302)
- [ ] Test: timeout handling

**Test:** `uv run pytest tests/test_validator.py -v`

**Acceptance:** All 4 tests pass

---

### Task 2.15: Implement Multi-Process Validation
- [ ] Create `validate_pages(pages: list[DiscoveredPage], processes: int) -> list[BrokenLink]` function
- [ ] Create worker function that processes one page
- [ ] Worker: fetch page, extract links, validate each link
- [ ] Worker: return list of BrokenLink objects
- [ ] Use multiprocessing.Pool with specified process count
- [ ] Use pool.map() to distribute work
- [ ] Collect and flatten results
- [ ] Add type hints, docstring, logging

**Test:** Write `tests/test_multiprocess.py`

**Acceptance:** Multi-process validation implementation complete

---

### Task 2.16: Write Multi-Process Validation Tests
- [ ] Create `tests/test_multiprocess.py`
- [ ] Test: validate with 2 processes
- [ ] Test: detect broken links correctly
- [ ] Test: verify all pages checked
- [ ] Test: check no race conditions (run multiple times)
- [ ] Test: handle worker crashes gracefully

**Test:** `uv run pytest tests/test_multiprocess.py -v`

**Acceptance:** All tests pass

---

### Task 2.17: Implement Report Generator
- [ ] Create `generate_report(result: ValidationResult, output_path: str) -> None` function
- [ ] Build summary dict (total_pages, total_links, broken_links, pages_with_broken_links)
- [ ] Build broken_links list (group by page)
- [ ] Build navigation_issues list
- [ ] Write YAML with yaml.safe_dump
- [ ] Add type hints and docstring

**Test:** Write `tests/test_reporter.py`

**Acceptance:** Reporter implementation complete

---

### Task 2.18: Write Report Generator Tests
- [ ] Create `tests/test_reporter.py`
- [ ] Create fixture ValidationResult with test data
- [ ] Test: generate YAML report
- [ ] Test: verify YAML structure matches specification
- [ ] Test: verify summary counts correct
- [ ] Test: verify YAML is valid (parse it back)
- [ ] Test: verify file written to correct path

**Test:** `uv run pytest tests/test_reporter.py -v`

**Acceptance:** All 5 tests pass

---

### Task 2.19: Implement Navigation Checking
- [ ] Create `check_navigation(mkdocs_config: str, discovered_pages: set[str]) -> list[dict]` function
- [ ] Use extract_nav_links to get nav URLs
- [ ] Compare against discovered pages
- [ ] Report any nav URLs not in discovered pages (likely 404s)
- [ ] Return list of issues with nav entry path and URL
- [ ] Add type hints and docstring

**Test:** Write `tests/test_nav_check.py`

**Acceptance:** Nav checking implementation complete

---

### Task 2.20: Write Navigation Checking Tests
- [ ] Create `tests/test_nav_check.py`
- [ ] Create fixture mkdocs.yml with known nav structure
- [ ] Test: detect nav entry pointing to non-existent page
- [ ] Test: handle valid nav entries
- [ ] Test: handle nested nav correctly

**Test:** `uv run pytest tests/test_nav_check.py -v`

**Acceptance:** All 3 tests pass

---

### Task 2.21: Implement CLI Interface
- [ ] Create main function in link_checker.py
- [ ] Use argparse for CLI arguments:
  - --base-url (required)
  - --output (default: link_check_report.yaml)
  - --processes (default: cpu_count())
  - --mkdocs-config (required)
  - --verbose (flag)
  - --no-nav-check (flag)
- [ ] Set up logging based on --verbose
- [ ] Add __main__ block
- [ ] Add type hints and docstring

**Test:** `uv run python link_checker/link_checker.py --help`

**Acceptance:** Help text displays correctly

---

### Task 2.22: Implement Main Orchestration Logic
- [ ] Wire together all phases in main():
  1. Validate Docker container accessible
  2. Run discovery phase
  3. Run multi-process validation phase
  4. Run navigation check phase (if not disabled)
  5. Generate report
  6. Print summary to stdout
- [ ] Add error handling for each phase
- [ ] Set appropriate exit codes (0/1/2/3)
- [ ] Add logging throughout

**Test:** Manual execution with test site

**Acceptance:** Full pipeline executes without errors

---

### Task 2.23: Write End-to-End Test
- [ ] Create `tests/test_e2e.py`
- [ ] Test: run full link checker against test site
- [ ] Verify report generated
- [ ] Verify broken link detected
- [ ] Verify summary counts correct
- [ ] Verify navigation issues reported
- [ ] Test with different process counts (1, 2, 4)

**Test:** `uv run pytest tests/test_e2e.py -v`

**Acceptance:** E2E test passes

---

### Task 2.24: Test Against Real Documentation
- [ ] Start dyalog-docs Docker container
- [ ] Run link checker against http://localhost:8080/
- [ ] Review generated report
- [ ] Verify no false positives
- [ ] Fix any real broken links found (separate task)
- [ ] Verify performance (<30s for 100+ pages)

**Test:** Manual execution and review

**Acceptance:**
- Link checker completes successfully
- Report is accurate
- Performance acceptable

---

### Task 2.25: Add Link Checker Documentation
- [ ] Update README.md with link checker usage
- [ ] Document installation of dependencies
- [ ] Document CLI arguments
- [ ] Document output format
- [ ] Add example command
- [ ] Add example output snippet

**Test:** Follow documentation to run link checker

**Acceptance:** Documentation clear and complete

---

### Task 2.26: Create Run Script
- [ ] Create `scripts/check_links.sh`
- [ ] Script should:
  1. Start Docker container if not running
  2. Wait for container to be ready
  3. Run link checker
  4. Print summary
  5. Exit with appropriate code
- [ ] Make script executable
- [ ] Add usage instructions in comment header

**Test:** `./scripts/check_links.sh` runs successfully

**Acceptance:** Script automates full workflow

---

### Task 2.27: Final Integration Test
- [ ] Run full test suite: `uv run pytest`
- [ ] Verify all tests pass
- [ ] Run black: `uv run black --check link_checker/ tests/`
- [ ] Run ruff: `uv run ruff check link_checker/ tests/`
- [ ] Fix any formatting or linting issues
- [ ] Verify pre-commit hook works

**Test:** `uv run pytest && uv run black --check . && uv run ruff check .`

**Acceptance:** All checks pass

---

## Summary

- Total tasks: 27
- Epic 1 (Docker): 9 tasks
- Epic 2 (Link Checker): 18 tasks

Each task is designed to be:
- Independently testable
- Completable in 15-60 minutes
- Clearly defined with acceptance criteria
- Ordered to minimize dependencies
