#!/bin/sh

cd web && FLASK_ENV=development python3 serve.py $GOJA_SETUP
