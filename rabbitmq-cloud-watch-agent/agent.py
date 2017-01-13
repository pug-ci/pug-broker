#!/usr/bin/env python
from __future__ import with_statement, print_function

from pyrabbit.api import Client
from pyrabbit import http
from boto.ec2 import cloudwatch
import os
from time import sleep

def get_queue_depths(cl, vhost):
    depths = {}
    queues = [q['name'] for q in cl.get_queues(vhost=vhost)]
    for queue in queues:
        if queue == "aliveness-test": #pyrabbit
            continue
        elif queue.endswith('.pidbox') or queue.startswith('celeryev.'): #celery
            continue
        depths[queue] = cl.get_queue_depth(vhost, queue)
    return depths


def publish_queue_depth_to_cloudwatch(cwc, queue_name, depth, namespace):
    print("Putting metric namespace=%s name=%s unit=Count value=%i" %
        (namespace, queue_name, depth))
    cwc.put_metric_data(namespace=namespace,
        name=queue_name,
        unit="Count",
        value=depth)


def publish_depths_to_cloudwatch(depths, namespace):
    cwc = cloudwatch.connect_to_region(os.environ.get("AWS_CLOUD_WATCH_REGION"))
    # cwc = CloudWatchConnection(region=os.environ.get("AWS_CLOUD_WATCH_REGION"))
    for queue in depths:
        publish_queue_depth_to_cloudwatch(cwc, queue, depths[queue], namespace)


def get_queue_depths_and_publish_to_cloudwatch(cl, vhost, namespace):
    depths = get_queue_depths(cl, vhost)
    publish_depths_to_cloudwatch(depths, namespace)

if __name__ == "__main__":
    host = os.environ.get("PUG_BROKER_AMQP_HOST")
    username = os.environ.get("PUG_BROKER_AMQP_USERNAME")
    password = os.environ.get("PUG_BROKER_AMQP_PASSWORD")

    cl = Client(host, username, password)

    connected = False
    while not connected:
        sleep(1)
        try:
            if cl.is_alive():
                connected = True
        except http.NetworkError:
            pass

    while True:
        get_queue_depths_and_publish_to_cloudwatch(
            cl,
            "/",
            os.environ.get("PUG_BROKER_AMQP_METRIC"))
        sleep(int(os.getenv("PUG_BROKER_METRIC_PUSH_PERIOD", 5 * 60)))
