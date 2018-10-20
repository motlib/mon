#!/bin/sh

export FLASK_APP=monsrv

pipenv run flask run --host=0.0.0.0
