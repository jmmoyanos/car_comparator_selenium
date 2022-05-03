FROM python:3.8

# Install selenium
RUN pip install --upgrade pip \
 && pip install selenium

COPY main.py /opt/app/main.py
COPY main_async.py /opt/app/main_async.py

COPY src /opt/app/src
COPY requirements.txt /opt/app/requirements.txt

WORKDIR /opt/app
RUN pip install -r requirements.txt



