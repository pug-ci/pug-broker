FROM python:2.7.13-alpine

MAINTAINER Pug CI Team

WORKDIR /apps/rabbitmq-cloud-watch-agent

COPY requirements.txt /apps/rabbitmq-cloud-watch-agent
RUN pip install --no-cache-dir -r requirements.txt

ADD agent.py /apps/rabbitmq-cloud-watch-agent

CMD python agent.py
