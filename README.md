# link_checker

## Description

Placeholder for project description.

## Installation

```bash
git clone https://github.com/[username]/link_checker.git
cd link_checker
uv sync
```

## Usage

Placeholder for usage instructions.

## Docker Setup

The project includes Docker infrastructure for serving the Dyalog documentation locally using MkDocs and nginx. This provides a consistent, isolated environment for development and testing.

### Prerequisites

- Docker
- Docker Compose

### Building the Docker Image

Build the documentation server image:

```bash
docker compose build
```

This creates a container with:
- nginx web server (Alpine Linux base)
- Python 3 and MkDocs with Material theme
- All required MkDocs plugins

### Starting the Documentation Server

Start the server in detached mode:

```bash
docker compose up -d
```

The documentation will be built automatically on container startup and served at:

http://localhost:8080/

### Stopping the Server

Stop and remove the container:

```bash
docker compose down
```

### Configuration

By default, the server uses test documentation from `test-docs/` for fast iteration. To serve the full Dyalog documentation:

1. Edit `docker-compose.yml`
2. Change the volume mount from `./test-docs:/docs` to `./dyalog-docs:/docs`
3. Restart the container with `docker compose up -d`

### Troubleshooting

Check container logs:

```bash
docker compose logs
```

Rebuild after configuration changes:

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Testing

Run tests:
```bash
uv run pytest
```

Format code:
```bash
uv run black link_checker/ tests/
```

Lint code:
```bash
uv run ruff check link_checker/ tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
