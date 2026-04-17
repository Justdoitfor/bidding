# Allow dynamic injection of registry mirror if needed, fallback to default Docker Hub
ARG PYTHON_IMAGE=python:3.11-slim
FROM ${PYTHON_IMAGE}

WORKDIR /app

# Install uv (using mirror)
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple uv

# Copy uv dependency files
COPY pyproject.toml uv.lock ./

# Set domestic mirror for uv to speed up downloads in China
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV UV_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu
ENV UV_PYTHON=3.11

# Tell uv to prefer binary wheels to avoid building from source, and use the system Python
ENV UV_COMPILE_BYTECODE=1
ENV UV_SYSTEM_PYTHON=1

# Print detailed logs during uv sync to prevent appearing "stuck"
ENV UV_NO_PROGRESS=1
ENV UV_VERBOSE=1

# Install dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv uv sync --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the FastAPI application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
