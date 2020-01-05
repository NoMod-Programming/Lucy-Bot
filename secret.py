#!/usr/bin/env python3
"""
secret.py - Credentials for Lucy
"""

from kik_unofficial import device_configuration

# Get our discord token, and kik credentials.
DISCORD_TOKEN = "replacethiswithyourdiscordtoken"

KIK_USERNAME = "kikusername"
KIK_PASSWORD = "kikpassword"

# CHANGE DEVICE ID AND ANDROID ID OR YOU MAY BE BANNED
device_configuration.device_id = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
device_configuration.android_id = "aaaaaaaaaaaaaaaa"
# If you have a custom kik version, add it below as well
#device_configuration.kik_version = 