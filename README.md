# Lightwave Energy Monitoring with InfluxDB

This application is designed to run on a Raspberry Pi via [Balena Cloud](www.balena.io), however it can also be executed directly on any hardware capable of running Python 3.x.

The code listens for the network broadcast messages from the energy monitor and converts these into a suitable format to push to InfluxDB.  You can then view the data either by uploading the custom graphs to Grafana or by querying the database directly.

## Installation

The recommended method of installing this application is using Balena Cloud as it removes a lot of the complexity around maintaining and deploying a python application.

To deploy this application, follow the [Getting Started with Raspberry Pi 2 and Python](https://www.balena.io/docs/learn/getting-started/raspberry-pi2/python/), however when you get to the part which starts `A nice first project to get started is a simple Flask web server`, clone this LightwaveRF Git repository and use that as the source instead of the link they give you.

**NOTE:** This application should work on any device for which Balena provide an image.  It has been tested on both RaspberryPI 2 and 3

### Manual Installation

Manual installation is a bit more involved, however there are times when it can be useful (for example, local debugging)

The steps are as follows:

   1. Clone this repository onto the relevant hardware and `cd` into that directory
   2. Create a python virtual env `venv .venv`
   3. Activate the virtual environment `source .venv/bin/activate`
   4. Install the required dependencies `pip install -r requirements.txt`
   5. Export the environment variables as listed under **Configuration**
   6. Start the script by running `python lwrf2influx.py`

## Configuration

You will need to set the following variables at either device or application level in the Balena Cloud Dashboard (*or on the command line via `export` commands for a manual installation*):

| Variable Name | Description | Example |
|---------------|-------------|---------|
| INFLUXDB_URL | The hostname of the InfluxDB instance *without* any protocol | `influxdb.mydomain.com` or `192.168.1.x` where `x` is the local IP Address |
| INFLUXDB_PORT | The port number we should be talking to | `8086` by default, otherwise check with the database provider to see how yours is configured. |
| INFLUXDB_USER | *Optional* The username for connecting to the database | `influx` |
| INFLUXDB_USER | *Optional* The password for authenticating to the database | `influx` |
| LOG_LEVEL | *Optional* The amount of logging you want to see from the application | `INFO` is the default, possible values include `INFO`, `WARNING`, `ERROR`, and `DEBUG`

