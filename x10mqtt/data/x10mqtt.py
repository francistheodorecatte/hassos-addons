# -------------------------------------------------------------------------------
#
#  X10mqtt Home Assistant Addon
#
#   This script allows for bridging between MQTT and X10.
#
#   It utilizes the 'heyu' command (https://www.heyu.org) for X10 control
#   and monitoring.
#
#   This was written and tested using a CM11a attached via a USB-to-Serial
#   adapter.  It should work with a CM17 Firecracker as well.
#
#   This does NOT support the USB devices like the SmartHome PowerLinc 1132B,
#   or the X10 CM15A.
#
# -------------------------------------------------------------------------------


import paho.mqtt.client as mqtt
import re
import subprocess
import os

try:
  broker = os.environ['MQTTBROKER']
except:
  print("Must define MQTT Broker in configuration!")
  exit(1)

try:
  port = int(os.environ['MQTTPORT'])
except:
  print("Must define MQTT port in configuration!")
  exit(1)

try:
  mqttuser = os.environ['MQTTUSER']
except:
  mqttuser = ""

try:
  mqttpass = os.environ['MQTTPASS']
except:
  mqttpass = ""

# rcvihc stores the house code from the monitor

rcvihc = ""

# FIFO is our named pipe from rcs_mon.sh

FIFO = '/tmp/rcsmon'

# cmdtopic for commands.  Housecode is appended.
# e.g. 'x10/cmd/A1' to command A1 device.
#
# Payload is either "ON" to turn on a unit, or "OFF" to turn it off
#
# Defaults to 'x10/cmd' if not defined
#
try:
  cmdtopic = os.environ['MQTTCMDTOPIC']
except:
  cmdtopic = "x10/cmd"

# dimtopic for dimmer commands.  Housecode is appended.
# e.g. 'x10/dim/A1' to command A1 device.
#
# Payload is a numeric value 0-255
#
# Defaults to 'x10/dim' if not defined
#
try:
  dimtopic = os.environ['MQTTDIMTOPIC']
except:
  dimtopic = "x10/dim"

# rcscmdtopic for RCS TX15-B thermostat protocol. Only needs housecode; unit code is appended automatically.
# e.g. 'x10/rcscmd/A'
#
# Payload is a JSON object with the desired command and a value (if applicable)
# e.g. '{"fan": "AUTO", "mode": "HEAT", "setpoint": "20", "setback": "FALSE"}
# see docs for full list of supported commands
#
# Defaults to 'x10/rcscmd' if not defined.
try:
  rcscmdtopic = os.environ['MQTTRCSREQTOPIC']
except:
  rcscmdtopic = "x10/rcscmd"

# rcsreqtopic for RCS TX15-B thermostat protocol. Only needs housecode; unit code 5 is appended automatically.
# e.g. 'x10/rcsreq/A'
#
# Returns a JSON payload on changes w/ autosend enabled on the device, e.g.:
# {"temperature": "75", "setpoint": "75", "mode": "HEAT", "fan": "AUTO", "sb_mode": "FALSE", "sb_delta": "6"}
# See RCS protocol for more info on autosend.
#
# Defaults to 'x10/rcsreq' if not defined
try:
  rcsreqtopic = os.environ['MQTTRCSREQTOPIC']
except:
  rcsreqtopic = "x10/rcsreq"

# status topic is for status updates
#
# We set the payload to "ON" or "OFF" for status updates
# This was added to support X10 remote buttons in order to keep
# the switch/light state correct in Home Assistant.
#
try:
  stattopic = os.environ['MQTTSTATTOPIC']
except:
  stattopic = "x10/stat"

#
# Whether a CM17A is in use
#
if os.getenv('CM17') != None:
  cm17 = True
else:
  cm17 = False

#
# Execute Heyu command
# cmd is one of:
#   ON - turn on housecode
#   OFF - Turn off housecode
#
#
def execute(client, cmd, housecode):
  # For the CM11, send command to heyu as-is (ON or OFF)
  # For the CM17, we need to change it to FON or FOFF.
  heyucmd = cmd
  if cm17:
    if cmd.lower() == "on":
      heyucmd = "fon"
    if cmd.lower() == "off":
      heyucmd = "foff"
  result = subprocess.run(["heyu", heyucmd.lower(), housecode.lower()])
  if result.returncode:
    print("Error running heyu, return code: "+str(result.returncode))
  print("Device Status Update: "+stattopic+"/"+housecode.lower())
  client.publish(stattopic+"/"+housecode.lower(),cmd.upper(),retain=True)
  return (result.returncode)

# use obdim to dim to level 0-22 after on & full bright w/ the CM11A for best compatibility
# if the light supports it, xpreset could be used with a value 0-63 (but we won't)
# with the CM17A, use fdimbo to dim to 0-22 after on
# for the CM17A w/ PLC lights, you *need* an RF to PLC transceiver

def dim(client, housecode, dimvalue):
  heyucmd = "obdim"
  if cm17:
    heyucmd = "fdimbo"
  #take passed 0-255 dim value, invert, and round it down to the nearest value 0-22
  heyudim = str(int(round((255 - int(dimvalue))/11.59, 0)))
  result = subprocess.run(["heyu", heyucmd.lower(), housecode.lower(), heyudim])
  if result.returncode:
    print("Error running heyu, return code: "+str(result.returncode))
  print("Device Status Update: "+stattopic+"/"+housecode.lower())
  client.publish(stattopic+"/"+housecode.lower(), dimvalue ,retain=True)
  return (result.returncode)

# RCS command
# here be dragons!
#
# this will likely require setting up some heyu scripts to act as macros for each command
# see the RCS TXB16 X10 Protocol Manual for more info.
#
# temperature setpoints will require a decoding array and converting celcius to fahrenheit.
# e.g. 'set temperature to 68' requires, per the RCS protocol:
# 'heyu preset A3 1'
# whereas, 'set temperature to 62' requires:
# 'heyu preset A2 27'
#
# commands are slightly easier as they will not require decoding arrays:
# e.g. 'set mode to heat' only requires:
# 'heyu preset A4 2'
#
# the table for the complete list of setpoints, commands, etc. is on page 8 of the protocol manual.

# RCS status
#
# this is a _little bit_ simpler as heyu already has built-in macros for these functions.
# heyu returns something like this for 'rcs_req preset A5 1' (current temperature):
# 10/10 11:41:42  Temperature = 75    : hu A0  (_no_alias_)
# a script on heyu's side calls presets 1-6, parses fields, and builds a JSON object to return via a named pipe, e.g.:
# '{"temperature": "75", "setpoint": "75", "mode": "HEAT", "fan": "AUTO", "sb_mode": "FALSE", "sb_delta": "6"}'

def rcs_stat(client):
  try:
    with open (FIFO) as fifo:
      while True:
        payload = fifo.read()
        if len(payload) == 0:
          break
        print("RCS payload received: "+payload)
        client.publish(rcsreqtopic+"/"+payload, retain=True)
  except:
    os.mkfifo(FIFO)

#
# Execute heyu monitor
# This is a long-lived process that monitors for X10 changes,
# like from a remote control.
#


def monitor():
    popen = subprocess.Popen(["heyu","monitor"], stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


#
# The monitor lines are broken out into 2 lines for one event:
#   rcvi addr unit - Declares the full unit number
#   rcvi func - The function on that unit
#

#
# Monitor rcvi addr unit - save the unit address in a variable for later
#
# Argument:  housecode, which is the housecode involved.  This is captured from the regex in the main loop and passed.
#

def rcviaddr(housecode):
  global rcvihc
  # Store the received housecode for when rcvifunc is received
  rcvihc = housecode

#
# Monitor rcvi func - the function that was applied to the housecode
#
# This happens after the 'rcvi addr unit', so the housecode that is stored
# from that is what is used.
#
# Argument:  func, which is the function (On or Off).  This is captured from the regex in the main loop and passed.
#

def rcvifunc(client,func):
  global rcvihc
  if rcvihc:
   print("Remote status change, publishing stat update: "+stattopic+"/"+rcvihc.lower()+" is now "+func.upper())
   client.publish(stattopic+"/"+rcvihc.lower(),func.upper(), retain=True)
   rcvihc = ""

#
# Define MQTT Connect Callback
#

def on_connect (client, userdata, flags, rc):

  # Set up MQTT subscription
  if rc:
    print("Error connecting to MQTT broker rc "+str(rc))

  print("Connected to MQTT broker, result code "+str(rc))
  client.subscribe(cmdtopic+"/+")
  client.subscribe(dimtopic+"/+")

#
# Callback for MQTT message received
#

def on_message(client, userdata, message):

  # Determine the device from the topic
  # Topics are cmdtopic/dev, e.g. 'x10/cmd/A1'
  # So the last part is the device we want to control

  command = str(message.payload.decode('utf-8')).upper()
  print("Received: "+message.topic+" "+command)
  topiclist = message.topic.split("/")

  # Get the homecode and convert it to upper case
  hc = topiclist[len(topiclist)-1].upper()
  command_type = topiclist[len(topiclist)-2].upper()


  # Check that everything is right
  hcpattern = re.compile("^[A-P][0-9]+$")
  if command in ["ON", "OFF"] and hcpattern.match(hc):
    print("Sending X10 command to homecode "+hc)
    result = execute(client, command, hc)
  elif command_type == "DIM":
    print("Sending X10 dim command to homecode "+hc);
    result = dim(client, hc, command)
  else:
    print("Invalid command or home code")

# ---------------------------
# Main program
# ---------------------------

# MQTT connect


print("Establishing MQTT to "+broker+" port "+str(port)+"...")
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Check if mqttuser or mqttpass is not blank
# If not, then configure the username and password

if mqttuser and mqttpass:
  print("(Using MQTT username "+mqttuser+")")
  client.username_pw_set(mqttuser,mqttpass)

try:
  client.connect(broker,port)
except:
  print("Connection failed. Make sure broker, port, and user is defined correctly")
  exit(1)

if cm17:
  print("CM17 is in use")

# Start the MQTT loop

print("Waiting for MQTT messages and monitoring for remote changes")
client.loop_start()

# We run 'heyu monitor' in the background to monitor for any X10 changes outside of us (e.g. X10 remotes)
# This way, we can send MQTT status changes if something does change.

# Regular expressions used to catch X10 updates, e.g. from X10 remotes

rercviaddr = re.compile(r"rcvi addr unit.+hu ([A-P][0-9]+)")
rercvifunc = re.compile(r"rcvi func.*(On|Off) :")


# Start the monitor process, which runs all the time.
# Catch any updates we care about so we can handle sending status updates via MQTT

for line in monitor():
  addrsearch = rercviaddr.search(line)
  funcsearch = rercvifunc.search(line)
  if addrsearch:
    rcviaddr(str(addrsearch.group(1)))
  if funcsearch:
    rcvifunc(client,str(funcsearch.group(1)))

  # Check rcs_mon FIFO and send an MQTT message w/ payload
  rcs_stat(client)
