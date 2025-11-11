# Dockerfile for serving MkDocs documentation with nginx
# Architecture: Install dependencies at build time, build docs at runtime
# The dyalog-docs directory is volume-mounted at runtime for flexibility

FROM nginx:alpine

# Install Python and pip
RUN apk add --no-cache python3 py3-pip

# Copy and install Python requirements
COPY docker/requirements.txt /tmp/requirements.txt
RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Create entrypoint script that builds docs and starts nginx
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'set -e' >> /entrypoint.sh && \
    echo 'if [ -d "/docs" ]; then' >> /entrypoint.sh && \
    echo '  cd /docs' >> /entrypoint.sh && \
    echo '  mkdocs build --site-dir /usr/share/nginx/html' >> /entrypoint.sh && \
    echo 'else' >> /entrypoint.sh && \
    echo '  echo "Warning: /docs directory not found, nginx will serve empty content"' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec nginx -g "daemon off;"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
