import serial
import argparse
import parse
import logging 
from waggle.plugin import Plugin, get_timestamp 
 
def parse_values(sample, **kwargs):
	#the es642 outputs data in a fixed length string w/ leading zeroes if necessary. fields that can be negative are precedded with a +/-.	
	data=sample.split(",") 
	#convert to floats 
	strip=[float(var) for var in data[:-1]]
	strip.append(float(data[-1][1:]))
	#zip names into a dictonary for ease of use
	label=["mg/m^3", "lpm", "C", "RH", "mb", "ss", "sum"] 
	ndict = dict(zip(label, strip))
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
    line = line.decode("utf-8")
    # Note: MetOne ES-642 has 1 second data output, need to check if bytes are returned. 
    # this is set at 40 to ignore partial readings that transmit as bytes.  
    if len(line) == 40: 
        # Define the timestamp
        timestamp = get_timestamp()
        logging.debug("Read transmitted data")
        # Check for valid command
        sample = parse_values(line) 
	#add labels to the data
        # If valid parsed values, send to publishing
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
    names = {"dust.env.conc" : "mg/m^3",
            "dust.env.flow" : "lpm",
	    "dust.env.temperature" : "C",
            "dust.env.humidity" : "RH",
	    "dust.env.pressure": "mb",
            "dust.env.status" : "ss",
            "dust.particle.checksum" : "sum" 
            }

    units = {"dust.env.conc" : "concentration of particulate matter",
             "dust.env.flow" : "liters per minute",
             "dust.env.temperature" : "degrees celcius",
             "dust.env.humidity" : "relative humidity of the sample",
             "dust.env.pressure": "absolute barometric pressure",
             "dust.env.status" : "hexidecimal",
             "dust.particle.checksum" : "sum of all digits before delim."

             }
    
    description = {"dust.env.conc" : "total concentration of suspended particulate matter",
                   "dust.env.flow" : "flow rate of the instrument",
                   "dust.env.temperature" : "ambient temperature",
                   "dust.env.humidity" : "relative humidity of the sample",
                   "dust.env.pressure": "ambient pressure in millibars",
                   "dust.env.status" : "indicator of status and error flags",
                   "dust.particle.checksum" : "check sum of all digits before the asterisk"
 		   }

    with Plugin() as plugin, serial.Serial(args.device, baudrate=args.baud_rate, timeout=1.0) as dev:
        while True:
            try:
                start_publishing(args, 
                                 plugin,
                                 dev,
                                 node_interval=args.node_interval,
                                 beehive_interval=args.beehive_interval,
                                 names=names,
                                 units=units,
                                 description=description
                                 )
            except Exception as e:
                print("keyboard interrupt")
                print(e)
                break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Plugin for Pushing MetOne dust sensor TSP data through WSN")

    parser.add_argument("--debug",
                        action="store_true",
                        dest='debug',
                        help="enable debug logs"
                        )
    parser.add_argument("--device",
                        type=str,
                        dest='device',
                        default="/dev/ttyUSB2",
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
