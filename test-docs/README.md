# Test MkDocs Site

A minimal MkDocs site for rapid Docker infrastructure testing.

## Purpose

This lightweight test site builds in seconds (vs. 30 minutes for the full Dyalog documentation), enabling:

- Fast Docker infrastructure validation
- Quick plugin testing
- Rapid navigation and link checking
- Development iteration without long wait times

## Features Tested

- **Theme**: Material for MkDocs
- **Plugins**: search, macros, minify, caption
- **Extensions**: admonition, pymdownx (details, superfences, keys), footnotes, tables_extended
- **Navigation**: Multi-level nav structure with internal links
- **Content**: Tables, code blocks, admonitions, footnotes

## Structure

```
test-docs/
├── mkdocs.yml           # MkDocs configuration
├── docs/
│   ├── index.md         # Home page
│   ├── getting-started.md
│   ├── features/
│   │   ├── overview.md
│   │   └── advanced.md
│   └── api.md
└── README.md            # This file
```

## Usage with Docker

### Build and run with test docs:

```bash
# Build the image (if needed)
docker build -f docker/Dockerfile -t dyalog-docs-test .

# Run with test-docs mounted
docker run -d -p 8080:80 -v $(pwd)/test-docs:/docs dyalog-docs-test

# Access at http://localhost:8080
```

### Verify the build:

```bash
# Check container logs
docker logs <container-id>

# Should see MkDocs build output
```

## Switching to Full Docs

To use the full Dyalog documentation instead:

```bash
docker run -d -p 8080:80 -v $(pwd)/dyalog-docs:/docs dyalog-docs-test
```

## Build Time Comparison

- **test-docs**: ~2-5 seconds
- **dyalog-docs**: ~20-30 minutes

This 300-600x speedup makes test-docs ideal for development and CI pipelines.
