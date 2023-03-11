FROM python:3.8

ENV PYTHONUNBUFFERED 1

WORKDIR .

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# CMD ["python3", "main.py"]