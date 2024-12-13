#!/usr/bin/env -S uv run

# /// script
# requires-python = "==3.13"
# dependencies = [
#   "requests",
#   "structlog",
# ]
# ///

import requests
import structlog

log = structlog.get_logger()

url = "https://ifconfig.me"

log.info("Getting public IP", url=url)

response = requests.get(url)

log.info("Found public IP", ip=response.text)
