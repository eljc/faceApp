FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -U pip wheel cmake

RUN apt-get update -y && \
    apt-get install build-essential cmake pkg-config -y

RUN pip install dlib==19.9.0

RUN pip3 install -r requirements.txt

RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python

COPY . .

ENV FLASK_APP=server.py

ENTRYPOINT [ "python" ]

CMD ["server.py" ]