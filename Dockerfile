FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# poppler-utils for pdf2image
RUN apt-get update \
    && apt-get -q install -y --no-install-recommends poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "worker.py"]
