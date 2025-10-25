FROM python:3.12.3-slim

WORKDIR /backend

COPY ./requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /backend