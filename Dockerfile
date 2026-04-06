FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir --default-timeout=180 --retries 10 --prefer-binary -r /app/requirements.txt

COPY . /app/

RUN mkdir -p /app/staticfiles /app/media

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
