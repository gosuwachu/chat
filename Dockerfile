FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl netcat-openbsd && apt-get clean