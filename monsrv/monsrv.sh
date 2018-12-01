#!/bin/sh

export FLASK_APP=monsrv

pipenv run python run.py --config ../config/mqtt.yaml --interface 0.0.0.0 --port 5000
