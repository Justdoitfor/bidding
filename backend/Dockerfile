# Allow dynamic injection of registry mirror if needed, fallback to default Docker Hub
ARG PYTHON_IMAGE=python:3.12-slim
FROM ${PYTHON_IMAGE}

WORKDIR /app

RUN pip install uv

# Copy pyproject.toml first (uv sync will auto-generate/update uv.lock if missing)
COPY pyproject.toml ./
# If you have uv.lock locally, uncomment the next line, but it's safer to let uv resolve it freshly when changing python versions
# COPY uv.lock ./

ENV UV_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu
ENV UV_PYTHON=3.12

# Tell uv to prefer binary wheels to avoid building from source, and use the system Python
ENV UV_COMPILE_BYTECODE=1
ENV UV_SYSTEM_PYTHON=1

# Print detailed logs during uv sync to prevent appearing "stuck"
ENV UV_NO_PROGRESS=1
ENV UV_VERBOSE=1

# Install dependencies using uv
# --index-strategy unsafe-best-match is used to prevent uv from failing when 
# it finds an older version of a package (like requests) in the pytorch index 
# and refuses to look in the default PyPI index for the newer required version.
RUN --mount=type=cache,target=/root/.cache/uv uv sync --no-dev --index-strategy unsafe-best-match

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the FastAPI application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
