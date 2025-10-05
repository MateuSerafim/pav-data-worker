FROM python:3.10-slim

WORKDIR /worker

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "worker.py"]