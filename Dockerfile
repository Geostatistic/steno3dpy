FROM python:2.7
MAINTAINER "Dan Gonzalez <dan.gonzalez@3ptscience.com>"

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt requirements_dev.txt setup.py README.rst /usr/src/app/
COPY steno3d /usr/src/app/steno3d
RUN pip install -r requirements.txt
RUN pip install -r requirements_dev.txt
