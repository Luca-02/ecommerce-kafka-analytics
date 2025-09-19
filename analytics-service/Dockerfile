FROM python:3.13.5-slim

RUN pip install --upgrade pip

WORKDIR /app

COPY ./shared ./shared

RUN pip install --no-cache-dir ./shared

COPY ./analytics-service .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]