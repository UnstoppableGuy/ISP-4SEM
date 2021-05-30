FROM python:3.8

WORKDIR /home

ENV API_TOKEN="value"
ENV WEBHOOK_HOST="value"
ENV WEBHOOK_PORT="value"
ENV WEBHOOK_SSL_CERT="value"
ENV WEBHOOK_SSL_PRIVATE_KEY="value"

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt 
COPY . .

ENTRYPOINT ["python", "app.py"]
