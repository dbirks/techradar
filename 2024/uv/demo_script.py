# /// script
# requires-python = "==3.12"
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
