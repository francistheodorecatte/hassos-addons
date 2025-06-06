# Home Assistant Community Add-On:  X10 to MQTT Bridge



This add-on provides MQTT control of X10 devices via CM10/CM11 and/or CM17A "Firecracker" RS232 serial interfaces and [heyu](https://github.com/HeyuX10Automation/heyu).

CM10&CM11-compatible serial interfaces include:

- X10 CM10A (NA)
- IBM HD16 (NA)(CM10A)
- X10 CM11A (NA)
- Marmitek CM12U (EU)
- IBM HD11A (NA)
- RCA HC60RX (NA
- ACT TI103 (NA)
- ACT TI213 (EU)
- ACT TI203 (AU)
- ACT TI223 (UK)
- JV Digital Engineering XTB-232 (NA/EU)

Incompatible interfaces include:

- SmartHome 1132B (NA)
- X10 CM15A (NA)
- Marmitek CM15Pro (EU)

Note that while the CM11 has EU derivatives meant for use with 240v/50Hz mains power, the CM17A is for use in North America only as it uses 310MHz for transmission, not 433MHz. For 433MHz X10 RF controls, you would need to use the CM19, which along with the aforementioned CM15, heyu does not support and will never support. Listening to 433MHz devices however, is possible with an RFX433 and the heyu aux engine (support for which is forthcoming; see below).

When using a CM11 interface, the addon also monitors for X10 changes that occur outside of Home Assistant (e.g. the use of X10 remote controls) and updates the status in Home Assistant.

ON, OFF, and DIM commands (DIM being slightly broken!) are supported. Support for RCS bidrectional thermostat protocol TBD.

## Configuration

Example add-on configuration via yaml:

```yaml
serial_port: /dev/ttyS0
cm10a_in_use: false
cm17a_in_use: false
mqtt_host: core-mosquitto
mqtt_port: 1883
mqtt_user: mqttuser
mqtt_pass: mqttpass
cmd_topic: x10/cmd
stat_topic: x10/stat
dim_topic: x10/dim
rcsreq_topic: x10/rcsreq
rcscmd_topic: x10/rcscmd
rcs_housecodes: A,B,C
```

The add-on can also be configured in Home Assistant web interface, via the "Configuration" tab.

#### Option: `serial_port`

The serial port for the CM11A interface, which is usually connected via a USB-to-Serial device.  You can find this by going to "Supervisor" screen, selecting the "System" tab.   On the "Host" card, select the 3-dot option and select "Hardware"

#### Option: `cm10a_in_use`

Boolean.

Enable this option (set to '**true**') if you are using a CM10A instead of a CM11A or compatible, as the serial protocol it uses is slightly different.

#### Option: `cm17_in_use`

Boolean.  

If you are using a CM17A "Firecracker" interface as your primary controller, enable this option (set to '**true**').  

If you are *only* using a CM11 interface, leave it set to '**false**'. 

Note that you can run the CM11 and CM17A together (see below for details).  Normally you would still set this option to **true** to use the CM17A as the primary X10 controller.

See below for issues with keeping your X10 and HASS environment in-sync.

#### Option: `mqtt_host`

The MQTT broker.  

If using the Home Assistant OS Mosquitto add-on as your broker, you can leave this as the default, `core-mosquitto`.  Otherwise, either the hostname or IP address of the broker you wish to use.

#### Option: `mqtt_port`

The port of the broker, typically 1883.  Note that SSL is not currently supported.

#### Options: `mqtt_user` and `mqtt_pass`

Used for MQTT authentication.  If left blank, then an anonymous connection will be attempted.  

If using the Mosquitto add-on, enter the username and password for a valid Home Assistant user account (or a MQTT internal acccount if you defined that).  See the Mosquitto add-on documentation for details on how user accounts are defined.

#### Option: `cmd_topic`

This is the base topic for X10 commands from Home Assistant.

MQTT topics are composed of the cmd_topic plus the housecode to control.  

For example, to control device with code G7 with the default `cmd_topic` of `x10/cmd`, the topic for that device will be `x10/cmd/g7`.

Publishing a message to that topic with payload of "ON" will turn G7 on, likewise a payload of "OFF" will turn G7 off.  NOTE:  Only payloads of "ON" or "OFF" are supported.

#### Option: `stat_topic`

When the status of X10 devices change, either through Home Assistant control or from an X10 remote, a status message is published to update Home Assistant. 

The topic structure follows the same format as `cmd_topic`.  For example, when G7 is turned on, a status message will be published to `x10/stat/g7` with a payload of "ON".

**NOTE:** Status messages are published with the Retain flag so that Home Assistant is able to retrieve the last known state when restarting.

#### Option: `dim_topic`

dim_topic is for dimmer commands.  Housecode is appended.

e.g. 'x10/dim/A1' to command A1 device.
Payload is a numeric value 0-255

Defaults to 'x10/dim' if not defined

#### Option: `rcsreq_topic`

rcsreq_topic is for status reports sent by x10mqtt for one or more RCS compatible thermostats.

A JSON payload similar to the following will be sent on to a subtopic `rcs_{housecode}` if the RCS (or compatible) thermostat is configured to auto-send temperature changes:
```json
{"housecode": "A", "temperature": "75", "setpoint": "75", "mode": "COOL", "fan": "OFF", "sb_mode": "FALSE", "sb_delta": "8"}
```

See the RCS bidirectional protocol manual for more info on configuring autosend.

#### Option: 'rcscmd_topic'

rcscmd_topic is for sending commands to RCS compatible thermostats.

Protocol implementation for commands is TBD.

#### Option: 'rcs_housecodes'

rcs_housecodes is a list of one or more RCS compatible thermostat housecodes. This can either be a single housecode letter, or a comma-separated list of multiple housecodes. This is used to build a section of status reporting scripts in the heyu configuration, among other things. Leave blank to disable the RCS thermostat status reporting feature.

## Home Assistant Configuration

Setting up a device in Home Assistant can use either the `switch` or `light` integration.  When using `light`, note that brightness is NOT supported.

Here is an example of an X10 `switch` for device with house code G7 and `cmd_topic` set to "x10/cmd" and `stat_topic` set to "x10/stat".

```yaml
switch:
  - platform: mqtt
    name: "X10 Switch"
    state_topic: "x10/stat/g7"
    command_topic: "x10/cmd/g7"
    payload_on: "ON"
    payload_off: "OFF"
    retain: false
```

A `light` is configured in a similar way.  See the Home Assistant documentation for "MQTT Light" for details. Dimming should work out of the box with `brightness_command_topic` set to the "x10/dim" topic.

### Potential Sync Issues

Most X10 devices do not have a way to determine their status via a query.  Therefore, it is possible that Home Assistant could get out-of-sync with the status of the device.  

The add-on makes every effort to mitigate this by using retained MQTT status messages.  Additionally, when using a CM11, the add-on monitors for any outside changes to an X10 device via X10 remotes or local toggles (by using 'heyu monitor' and searching for specific events). 

With the CM11, Home Assistant can get out of sync by:

- Making changes to an X10 device when the add-on is not running.
- X10 device changes that do not advertise their change, and hence not picked up by 'heyu monitor'

Note that the CM17A is a transmit-only device and does not report X10 changes, therefore it is much more likely that Home Assistant and your X10 environment can get out-of-sync unless you only make X10 on/off events through Home Assistant.

In most cases, you can resync Home Assistant and your X10 device by toggling the device power in the Home Assistant interface.

### Using a CM17A and a CM11A Together

You can use both the CM17A for transmitting codes and a CM11 for receiving X10 updates simultaenously!  Simply connect the CM11 to the DB9 pass-through port on the CM17A module.

This is helpful if you have a CM11 that is not transmitting properly, or you simply wish to use RF transmission instead of power line for control.  Using the CM11 in tandem allows for X10 commands outside Home Assistant to be read by the add-on to mitigate the out-of-sync issues discussed in the section above.

Note that if you intend on using a CM17A with certain powerline only modules (usually hard-wired modules, such as the WS467/WS469), you will also need an RF-to-powerline transceiver module such as the TM751 or RR501 (see below).

## Troubleshooting and extra info

### Notes for X10 Newcomers

- If you have split-phase or three phase power (such as in North American or German homes, respectively) and your CM11 interface or tranceiver is on a different phase from your remote powerline modules, you will need to install a passive coupler or active phase amplifier/repeater near or at your breaker panel, such as the X10 PRO XPCR or Leviton HCA02-10E, or more simply via a dryer plug module like the SmartHome SignaLinc 4826 series.
	- This usually shows up as an intermittent problem, and can be diagnosed by turning on a 240v or 400v appliance such as baseboard electric heat, heatpumps, electric stoves/ranges, or a resistive electric dryer to couple the phases together, before testing an X10 powerline transmission.
	- Do not, **under any circumstance**, use a bare capacitor-based phase coupler! These are dangerous for reasons beyond the scope of this project, suffice to say, you should pay the extra money for an off-the-shelf coupler/repeater module for safety reasons.
- If your CM11 locks up or does not transmit intermittently, you may need to install X10 filters on nearby appliances on the same breaker. Uninterruptable Power Supplies are particularly bad in this regard. For post-1999 CM11 reference designs, there is a modification you can do to mitigate this: [CM11A Overheating](https://web.archive.org/web/20080519131426/http://www.idobartana.com/hakb/CM11Aoverheating.htm)

### Controlling PLC devices with a CM17A/Monitoring X10 RF with a CM11A (transceiving)

If you wish to monitor RF signals, or want RF commands repeated to the powerline, you will need an RF to PLC transceiver such as:

- X10 TM571/PAT02
- X10 RR501/PAT01
- RCA HC50RX (RR501)
- Leviton HCPRF-1TW
- Insteon EZX10RF (allegedly when programmed via Smartenit Utility Suite)
- X10 CM15A (when configured correctly via mochad or AHP)

Note that the X10 TM571 and its bidirectional control counterpart, the RR501, while having many cheap and available white-label rebrands, are single housecode only. While the HCPRF-1TW can transceive all housecodes (bi-directionally!), the CM15A can only do so (unidirectionally, RF to PLC, while standalone) if so configured with mochad (Linux/MacOS) or AHP (Windows), which is outside of the scope of this document.

Also note that the CM15A and HCPRF-1TW are both known to have poor range, and in the CM15A's case, poor reliability due to distinctly lacking in decoupling capacitors. That can be rectified with modifications, but that is also outside of the scope of this document.

Support in this addon for running the heyu aux engine, which in combination with another serial port and very cheap X10 MR26A adapters, or an RFXCOM RFX310/433, is planned for in the future. This will allow directly monitoring RF, and tranceiving all housecodes to powerline (by default, selecting housecodes for RF to PLC transceiving is also planned) when used in combination with a CM11 and CM17.

### Slow/intermittent CM11 Serial Connection Issues

May be caused when using a Prolific USB-to-Serial adapter chipset, such as the PL2302 or PL2303. Using a (genuine) FTDI chipset is recommended to mitigate this. If at all possible, use a hardware UART for the best compatibility.

### Resetting/Unlocking the CM11A

Per the [official X10 wiki page on the matter](https://kbase.x10.com/wiki/CM11A_Unlock_Procedure), if your CM11A does not respond to commands:

>     1. Unplug the CM11A Computer Interface and remove its batteries.
>     2. Plug the Interface back into the outlet, without battery power.
>     3. Plug your Transceiver (the module with the silver antenna) into the pass-through outlet of the CM11A.
>     4. Push the physical ON/OFF button on the Transceiver a couple times to hear the click of the relay. This will ensure you have power to the Interface.
>     5. Using any standard X10 remote control, turn the transceiver On and Off several times. Again, you should hear the unit audibly “clicking”.
>     6. Return to the TOOLS | TEST COMMUNICATIONS menu, and select TEST to verify successful communication to the CM11A has been restored.

Note that this procedure requires a transceiver or similar module with a TEST or ON/OFF button that transmits ON/OFF messages to device code A1, like the TM571. This also applies to any of the white label rebrands of the CM11A.

The only difference in this application would be step six, where you retry transmitting via MQTT and heyu; the offical instructions assume you are using [ActiveHome](https://kbase.x10.com/wiki/ActiveHome). Step 5 is also redundant.

For best results leave the CM11A unplugged with the batteries removed for 10-15 minutes prior to plugging it back into an outlet.

If this procedure does not work, you either have a very noisy power system (see the notes above), or your CM11A is faulty. Try moving the CM11A to an outlet somewhere 'quiet' before giving up on it.

### Hardware Reliability

It's recommended to avoid the CM11A and its white label rebrands, easily spotted as they all have the same case molding and FCC ID of B4SCM10A, in a 'modern' home (modern being codeword for 'full of devices with switching power supplies') for reliability reasons unless you're handy with a soldering iron. The XTB-232 is a much better experience out of the box as it's not prone to lockups or command collisions. The older CM10A and its HD16 relabel (discernable from their lack of a battery compartment on the front), while not "polite", are purportedly more reliable and can still (as of late 2024) be found cheaply in older new-old-stock IBM Home Director starter kits with the duotone blue/white box art and Aptiva branding.

## Support

At the moment, the best way to obtain support is via the thread on the Home Assistant Community (https://community.home-assistant.io/t/home-assistant-add-on-x10-cm11-to-mqtt-gateway/276064)

## Authors and contributors

The original author of this add-on is [Mark Motley](https://github.com/mmotley999/) based some ideas gathered from [kevineye/docker-heyu-mqtt](https://github.com/kevineye/docker-heyu-mqtt), specifically around using 'heyu monitor' to check for changes.

## License

MIT License

Copyright (c) 2021 Mark Motley

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

