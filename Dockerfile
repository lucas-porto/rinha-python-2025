FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONOPTIMIZE=1

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache-dir -e .

COPY . .

EXPOSE 9999

CMD ["python", "-m", "app.main"]
