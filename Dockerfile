FROM python:3.10.2-alpine

## Multi commands in same line to Minimize the Number of Layers
RUN pip install flask && pip install kubernetes

## for better caching
# recommended to add the lines which are used for installing dependencies & packages earlier inside the Dockerfile
RUN mkdir /app
ADD . /app
WORKDIR /app

CMD ["python", "app.py"]