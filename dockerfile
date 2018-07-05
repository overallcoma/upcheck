FROM alpine:latest
RUN mkdir /upcheck
COPY requirements.txt /upcheck
COPY upcheck.py /upcheck
RUN apk update
RUN apk add python3-dev
RUN apk add sqlite
RUN pip3 install --upgrade pip
RUN pip3 install -r /upcheck/requirements.txt

WORKDIR /upcheck
CMD [ "python3", "./upcheck.py" ]
