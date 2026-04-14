# Allow dynamic injection of registry mirror if needed, fallback to default Docker Hub
ARG PYTHON_IMAGE=python:3.11-slim
FROM ${PYTHON_IMAGE}

WORKDIR /app

# Install uv
RUN pip install uv

# Copy uv dependency files
COPY pyproject.toml uv.lock ./

# Set domestic mirror for uv to speed up downloads in China
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# Install dependencies using uv
RUN uv sync --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the FastAPI application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
