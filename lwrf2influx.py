import json
import logging
import os
import pytz
import socket

from influxdb import InfluxDBClient
from datetime import datetime

# Get the Environment variables
log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
influx_host = os.getenv("INFLUXDB_URL")
influx_db = os.getenv("INFLUXDB_DATABASE")
influx_port = os.getenv("INFLUXDB_PORT")
influxdb_user = os.getenv("INFLUXDB_USER")
influxdb_pass = os.getenv("INFLUXDB_PASS")

# Set the log level as appropriate
logging.basicConfig(level=log_level)

### SETUP THE UDP LISTENER ###
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP

# Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
# Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
# For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
# So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
# Thanks to @stevenreddie
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# Enable broadcasting mode
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

logging.info("Starting UDP Listener")
client.bind(("", 9761))

### SETUP INFLUXDB ###

logging.info("Configuring InfluxDB Client")
# Check for a username and password, if they exist use them, otherwise connect anonymously
if influxdb_user is not None:
    idb = InfluxDBClient(influx_host, influx_port, influxdb_user, influxdb_pass, database=influx_db)
else:
    idb = InfluxDBClient(influx_host, influx_port, database=influx_db)

tz = pytz.timezone("UTC")

### LISTEN AND FORWARD TO INFLUXDB ###

while True:
    # Thanks @seym45 for a fix
    data, addr = client.recvfrom(1024)
    decoded = data.decode("UTF-8").replace("!", "").replace("*","")
    dec_json = json.loads(decoded)
    if "serial" in dec_json:
        pwr_data = [{
            "measurement": "lwrf_current_power_usage",
            "tags": {
            "application": "lightwaverf",
            "source_monitor": dec_json["serial"],
            },
            "time": datetime.now(tz),
            "fields": {
            "value": dec_json["cUse"],
            }
        },
        {
            "measurement": "lwrf_power_usage_today_so_far",
            "tags": {
            "application": "lightwaverf",
            "source_monitor": dec_json["serial"],
            },
            "time": datetime.now(tz),
            "fields": {
            "value": dec_json["todUse"],
            }
        }
        ]
        # Print out the data received if we're in debug mode
        logging.debug(pwr_data)
        # Write the data to the database
        idb.write_points(pwr_data, time_precision="ms")

