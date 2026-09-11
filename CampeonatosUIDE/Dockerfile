FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .

RUN mkdir -p /data /app/staticfiles /app/media
RUN addgroup --system django && adduser --system --ingroup django django \
    && chown -R django:django /app /data
USER django
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn CampeonatosUIDE.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120"]
