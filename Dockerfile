FROM python:3.7-alpine
WORKDIR /usr/src/app
RUN apk add --no-cache gcc bluez-dev zlib-dev jpeg-dev musl-dev
COPY requirements.txt .
RUN pip install -r requirements.txt

# Add code to Docker image
COPY .coveragerc .
COPY libband ./libband