# mon

This project is a system monitor based on MQTT protocol. It consists of the
`mon` monitoring agent, which collects monitoring data and the `monsrv` web UI
to display it.

`mon` is intended to run on all nodes which shall be monitored. It will publish
its data to a MQTT broker. 

The web application implemented in `monsrv` can run on any host. It will
subscribe to the MQTT topics published by `mon` and display the data on a web
page.

Both `mon` and `monsrv` are implemented in Python 3.


## Requirements and Setup

Note: The following instructions assume that you already have an MQTT broker
(e.g. `mosquitto`) running in your network.

To get started, clone the git repository:

    git clone https://github.com/motlib/mon.git
    
Now we need to set up the Python runtime environment. For this, `pipenv` is
used. (TODO: Add reference to install instructions for pipenv. )

As `mon` and `monsrv` are separate applications residing in the same repository,
you need to set up their environment separately. On each host where mon shall
run, run `pipenv` to set up python and the package dependencies:

```sh
cd mon
pipenv sync
```

And the same for the web application:

```sh 
cd monsrv
pipenv sync
```


## Configuration

To specify the address of the MQTT broker, edit the configuration file in
`config/mqtt.yaml` and update the broker address and port if necessary.

The file `mqtt.yml` looks similar to this:

```yaml
# MQTT configuration
# hostname of the broker
broker: opi2
  
# MQTT port
port: 1883
  
# MQTT topic prefix
prefix: mon
```


## Running

To start the monitoring agent, change to the `mon` directory and run `mon.sh`. 

