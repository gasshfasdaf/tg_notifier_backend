FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including build tools and PostgreSQL client libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml uv.lock README.md ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uv", "run", "python", "-m", "app.main"]