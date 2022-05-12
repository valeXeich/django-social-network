FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR user/app

COPY ./req.txt /user/req.txt
RUN pip install -r /user/req.txt

COPY ./social /user/app
