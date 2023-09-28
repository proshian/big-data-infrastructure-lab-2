FROM python:3.10-slim
# FROM proshian/python-with-reqs

ENV PYTHONUNBUFFERED 1

WORKDIR /model_app

# copy all the files to the container
COPY . .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# CMD ["python", "./app.py"]