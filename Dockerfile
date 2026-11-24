# Use uv only while building; the application image stays on the existing Python base.
FROM python:3.14-alpine

# Copy a specific uv release so the lockfile is installed consistently.
COPY --from=ghcr.io/astral-sh/uv:0.13.10@sha256:a3ea1357342c1a4bf9a0c53a3deb1b55379aefa037338d8113d5771efa01774f /uv /uvx /bin/

WORKDIR /app

# Keep dependencies in a cached layer and reject an absent or stale lockfile.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

COPY . .
RUN uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

CMD [ "python", "-m", "narrowcast_content.waitress_server"]
