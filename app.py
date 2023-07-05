import serial
import argparse
import parse
import logging
 
from waggle.plugin import Plugin, get_timestamp

def parse_values(sample, **kwargs):
    # Note: The MetOne ES-642 data is a fixed length comma separated string w/ fixed variable positions
    # leading zeroes pad values as needed.  
    if sample.startswith(b'20'):
        data = parse.search("{ti}," +
                            "{.1F}," +
                            "{.1F}," +
                            "{.1F}," +
                            "{.3F}," +
                            "{.3F}," +
                            "{.3F}," +
                            "{.3F}," +
                            "{.1F}," +
                            "{.1F}," +
                            "{.1F}," +
                            "{w}," +
                            "{d}\r\n" ,
                            sample.decode('utf-8')
                            )
        # Parse the variable names from the datastring
        # Captured by the {w} flag
        parms = data['w'].split(',')
        # Convert the variables to floats
        strip = [float(var) for var in data]
        # Create a dictionary to match the parameters and variables
        ndict = dict(zip(parms, strip))
        # Add the ES-642 datetime to the dictionary
        ndict['datetime'] = data['ti']
        ndict['uptime'] = int(data['d'])

    else:
        ndict = None

    return ndict


def start_publishing(args, plugin, dev, **kwargs):
    """
    start_publishing initializes the MetOne ES-642
    Begins sampling and publishing data

    Functions
    ---------


    Modules
    -------
    plugin
    logging
    sched
    parse
    """
    # Note: MetOne ASCII interface configuration described in manual
    line = dev.readline()
    # Note: MetOne ES-642 has 1 second data output, need to check if bytes are returned
    if len(line) > 0: 
        # Define the timestamp
        timestamp = get_timestamp()
        logging.debug("Read transmitted data")
        # Check for valid command
        sample = parse_values(line) 
    
        # If valid parsed values, send to publishing
        if sample:
            # setup and publish to the node
            if kwargs['node_interval'] > 0:
                # publish each value in sample
                for name, key in kwargs['names'].items():
                    try:
                        value = sample[key]
                    except KeyError:
                        continue
                    # Update the log
                    if kwargs.get('debug', 'False'):
                        print('node', timestamp, name, value, kwargs['units'][name], type(value))
                    logging.info("node publishing %s %s units %s type %s", name, value, kwargs['units'][name], str(type(value)))
                    plugin.publish(name,
                                   value=value,
                                   meta={"units" : kwargs['units'][name],
                                         "sensor" : "metone_es-642",
                                         "missing" : '-9999.9',
                                         "description" : kwargs['description'][name]
                                         },
                                   scope="node",
                                   timestamp=timestamp
                                   )
            # setup and publish to the beehive                        
            if kwargs['beehive_interval'] > 0:
                # publish each value in sample
                for name, key in kwargs['names'].items():
                    try:
                        value = sample[key]
                    except KeyError:
                        continue
                    # Update the log
                    if kwargs.get('debug', 'False'):
                        print('beehive', timestamp, name, value, kwargs['units'][name], type(value))
                    logging.info("beehive publishing %s %s units %s type %s", name, value, kwargs['units'][name], str(type(value)))
                    plugin.publish(name,
                                   value=value,
                                   meta={"units" : kwargs['units'][name],
                                         "sensor" : "metone_ES-642",
                                         "missing" : '-9999.9',
                                         "description" : kwargs['description'][name]
                                        },
                                   scope="beehive",
                                   timestamp=timestamp
                                  )

def main(args):
    publish_names = {"es624.env.temp" : "T",
                     "es624.env.pressure" : "P",
                     "es624.env.humidity" : "H", 
                     "es624.particle.tsp" : "mg/m^3",
                     "es624.house.datetime" : "datetime",
                     "es624.house.uptime" : "uptime",
                    }

    units = {"es624.env.temp" : "degrees Celsius",
             "es624.env.pressure" : "mb",
             "es624.env.humidity" : "percent relative humidity from inside the instrument"
             "es624.particle.tsp" : "milligram per cubic meter",
             "es624.house.datetime" : "UTC time",
             "es624.house.uptime" : "seconds"
             }
    
    description = {"es624.env.temp" : "Ambient Temperature",
                   "es624.env.pressure" : "Ambient Atmospheric Pressure",
                   "es624.env.humidity" : "Sample Relative Humidity",
                   "es624.particle.tsp" : "total suspended particle count", 
                   "es624.house.datetime" : "UTC time in YYYY-MM-DDTHH:MM:SS format",
                   "es624.house.uptime" : "Time in seconds since instrument startup"
                  }

    with Plugin() as plugin, serial.Serial(args.device, baudrate=args.baud_rate, timeout=1.0) as dev:
        while True:
            try:
                start_publishing(args, 
                                 plugin,
                                 dev,
                                 node_interval=args.node_interval,
                                 beehive_interval=args.beehive_interval,
                                 names=publish_names,
                                 units=units,
                                 description=description
                                 )
            except Exception as e:
                print("keyboard interrupt")
                print(e)
                break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Plugin for Pushing Viasala WXT 2D anemometer data through WSN")

    parser.add_argument("--debug",
                        action="store_true",
                        dest='debug',
                        help="enable debug logs"
                        )
    parser.add_argument("--device",
                        type=str,
                        dest='device',
                        default="/dev/ttyUSB3",
                        help="serial device to use"
                        )
    parser.add_argument("--baudrate",
                        type=int,
                        dest='baud_rate',
                        default=9600,
                        help="baudrate to use, defined in manual"
                        )
    parser.add_argument("--node-publish-interval",
                        default=1.0,
                        dest='node_interval',
                        type=float,
                        help="interval to publish data to node " +
                             "(negative values disable node publishing)"
                        )
    parser.add_argument("--beehive-publish-interval",
                        default=1.0,
                        dest='beehive_interval',
                        type=float,
                        help="interval to publish data to beehive " +
                             "(negative values disable beehive publishing)"
                        )
    args = parser.parse_args()


    main(args)
