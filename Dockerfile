FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /model

# copy all the files to the container
COPY . .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# CMD ["python", "./app.py"]