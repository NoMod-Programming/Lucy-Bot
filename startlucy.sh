#!/bin/bash

# Needed to run Lucy with this because kik stopped
# Sending updates after a few hours

# Just restarts the script every hour

while timeout -k 1 3600 ./lucy.py || true; do
	sleep 5
done