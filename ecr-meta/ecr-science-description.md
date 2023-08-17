## MetOne ES-642 Dust Monitor Plugin 
Waggle Sensor Plug-In for the [Met One Remote Dust Monitor ES-642](https://metone.com/products/es-642/) 

The ES-642 provides observations on particulate concentrations with a sensitivity of 0 to 100,000 μg/cubic meter. Optional inlet attachments can be used to PM1, PM2.5, or PM10 particle detection, default inlet provides total suspended particle concentrations. 

[Waggle Sensor Information](https://github.com/waggle-sensor) 
## Determine the Serial Port
The ES-642 utilzies an RS-485 serial connection to transmit data (RS-232 serial connection for manufacture dates post June 2022).

Therefore, to determine which port the instrument is plugged into, PySerial offers a handy toollist to list all serial ports currnetly in use.
```bash
python -m serial.tools.list_ports
```
## Testing 

Similar to the [Vaisala WXT536 plugin](https://portal.sagecontinuum.org/apps/app/jrobrien/waggle-wxt536) a docker container will be setup via Makefile 

### 1) Build the Container
```bash
make build
```

### 2) Deploy the Container in Background
```bash
make deploy
```

### 3) Test the plugin
```bash
make run
```

# Access the Data
```py
import sage_data_client

df = sage_data_client.query(start="2023-12-07T03:00:00Z",
                            end="2023-11-07T04:00:00Z", 
                            filter={
                                "plugin": "lizzywaz/waggle-metone",
                                "vsn": "W039",
                                "sensor": "metone-es642"
                            }
)

```

