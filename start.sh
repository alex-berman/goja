#!/bin/sh

#cd web && FLASK_ENV=development python3 serve.py
cd web && gunicorn --worker-class eventlet -w 1 serve:app --log-file -
