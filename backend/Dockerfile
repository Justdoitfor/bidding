# Allow dynamic injection of registry mirror if needed, fallback to default Docker Hub
ARG PYTHON_IMAGE=python:3.12-slim
FROM ${PYTHON_IMAGE}

# Install curl for fetching PyTorch directly
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

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

# Manually fetch and install PyTorch CPU wheel first to completely bypass uv's resolution conflicts
RUN curl -L -o torch-2.1.0+cpu-cp312-cp312-linux_x86_64.whl https://download.pytorch.org/whl/cpu/torch-2.1.0%2Bcpu-cp312-cp312-linux_x86_64.whl && \
    uv pip install --system ./torch-2.1.0+cpu-cp312-cp312-linux_x86_64.whl && \
    rm torch-2.1.0+cpu-cp312-cp312-linux_x86_64.whl

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
