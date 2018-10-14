#!/bin/sh
#
# Helper script to start the monitoring node.
#

pipenv run python -m mon --config ../config/example.yaml --all-collectors $*
