# Home Assistant Community Add-on: X10mqtt

## About

The X10 to MQTT add-on provides for X10 control when using a CM11-compatible serial powerline interface (see the docs for a list of compatible interface models), and/or a CM17A "Firecracker" serial interface connected to your Home Assistant OS system using MQTT commands.

X10mqtt currently supports the following X10 commands:
- On
- Off
- Dim

### Key features

- Allows for Home Assistant OS users to control X10 devices using MQTT, since 'heyu' is not available in the Docker-based Home Assistant.
- Monitors for external X10 commands (e.g. from an X10 remote) and updates the status in Home Assistant accordingly when using the CM11-compatible interface (the CM17A Firecracker does not support this unless a CM11 is run in-tandem, see the docs).

### Planned Features
- RCS (Residential Control Systems) X10 thermostat control protocol support for the TXB16, with possible future backward compatibility with the older TX15-B and TX10-B.
- Implementing support for the heyu aux engine, to allow using the X10 MR26A, WGL W800RF32A, or RFXCOM 310MHz receivers to monitor and transceive RF commands.
- Support for serial over telnet, allowing use of networked (and possibly remote!) terminal services routers such as an MRV or Cisco 2509 in place of USB to serial adapters.
