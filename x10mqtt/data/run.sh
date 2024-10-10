#!/usr/bin/with-contenv bashio
set -e

HEYUCONFIG="/etc/heyu/x10.conf"

bashio::log.info "Configuring Heyu..."

# Generate basic X10 configuration file

SERIAL=$(bashio::config "serial_port")
echo -e "TTY\t\t  ${SERIAL}\n" > "${HEYUCONFIG}"
echo -e "RCS_DECODE\t\t  ALL\n" >> "${HEYUCONFIG}"

# Export enviornment variables for the main script

export MQTTBROKER=$(bashio::config "mqtt_host")
export MQTTPORT=$(bashio::config "mqtt_port")
export MQTTUSER=$(bashio::config "mqtt_user")
export MQTTPASS=$(bashio::config "mqtt_pass")
export MQTTCMDTOPIC=$(bashio::config "cmd_topic")
export MQTTSTATTOPIC=$(bashio::config "stat_topic")
export MQTTDIMTOPIC=$(bashio::config "dim_topic")
export MQTTRCSREQTOPIC=$(bashio::config "rcsreq_topic")
export MQTTRCSCMDTOPIC=$(bashio::config "rcscmd_topic")

# Export environement if CM17 is defined

if bashio::config.true "cm17_in_use" ; then
  bashio::log.info "CM17 is enabled"
  export CM17="True"
else
  bashio::log.info "CM11 is enabled"
fi

# Start heyu engine
heyu engine

# Run main script
python3 -u /usr/local/bin/x10mqtt.py
