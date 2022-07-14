# syntax=docker/dockerfile:1
FROM python:3.9.2-alpine
WORKDIR /solarproject
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["python3", "main.py"]
