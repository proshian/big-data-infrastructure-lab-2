FROM python:3.10

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# copy all the files to the container
COPY . .

# Install Thrift
RUN apt-get update && \
    apt-get install -y libthrift-dev && \
    apt-get clean

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt