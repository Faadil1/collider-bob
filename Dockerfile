# COLLIDER action runtime for Cloudflare Containers.
#
# Contains only what ACTIVE MODE needs: the collider/ runtime, the three
# workstreams with their behavioral tests, the failed-payment fixture, the
# action server and its container adapter. The image holds the immutable
# baseline; runtime output (.collider/) is written at run time to the
# container's ephemeral filesystem and is never baked into the image.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY cloudflare/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

WORKDIR /app

COPY collider/ collider/
COPY api/ api/
COPY ledger/ ledger/
COPY notifications/ notifications/
COPY fixtures/failed-payment/ fixtures/failed-payment/
COPY demo-ui/server.py demo-ui/server.py
COPY cloudflare/container_server.py cloudflare/container_server.py

# Baseline files are read-only to the runtime user; only .collider/ is writable.
RUN useradd --create-home --uid 10001 collider \
 && mkdir -p /app/.collider \
 && chown collider:collider /app/.collider

USER collider

EXPOSE 8080
CMD ["python3", "cloudflare/container_server.py"]
