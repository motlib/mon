#!/bin/sh

pipenv run python run.py --config ../config/mqtt.yaml --interface 0.0.0.0 --port 5000 --debug
