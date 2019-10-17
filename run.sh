#!/bin/bash
# This script was built for starting run the python program using uWSGI

echo Starting...

uwsgi --http :5008 --gevent 1000 --http-websockets --wsgi-file manage.py --callable app
