# RAG Service Production Dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --user --no-cache-dir --upgrade pip
RUN pip install --user --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runner

WORKDIR /app

RUN useradd -m -u 1000 appuser

RUN apt-get update && apt-get install -y \
    libopenblas0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /home/appuser/.local

ENV PATH=/home/appuser/.local/bin:$PATH

COPY . .
RUN chown -R appuser:appuser /app

USER appuser

ENV PORT 8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
