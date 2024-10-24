#!/usr/bin/with-contenv bashio
set -e

HEYUCONFIG="/etc/heyu/x10.conf"

bashio::log.info "Configuring Heyu..."

# Generate basic X10 configuration file

SERIAL=$(bashio::config "serial_port")
HOUSECODE=$(bashio::config "rcs_housecodes")
if bashio::config.true "cm10a_in_use" ; then
	bashio::log.info "CM10A is in use"
	echo -e "TTY\t\t${SERIAL}\tCM10A" > "${HEYUCONFIG}"
else
	echo -e "TTY\t\t${SERIAL}" > "${HEYUCONFIG}"
fi
echo -e "RCS_DECODE\t\tALL" >> "${HEYUCONFIG}"
echo -e "START_ENGINE\t\tAUTO\n" >> "${HEYUCONFIG}"
if [[ ! -z $HOUSECODE ]]; then
	for FOO in ${HOUSECODE//,/ }; do
		echo "SCRIPT -l rcs_mon_${FOO} ${FOO}6 preset rcvi :: /etc/heyu/rcs_mon.sh" >> "${HEYUCONFIG}"
	done
else
	bashio::log.info "Housecode var empty, skipping"
fi

# Export environment variables for the main script

export MQTTBROKER=$(bashio::config "mqtt_host")
export MQTTPORT=$(bashio::config "mqtt_port")
export MQTTUSER=$(bashio::config "mqtt_user")
export MQTTPASS=$(bashio::config "mqtt_pass")
export MQTTCMDTOPIC=$(bashio::config "cmd_topic")
export MQTTSTATTOPIC=$(bashio::config "stat_topic")
export MQTTDIMTOPIC=$(bashio::config "dim_topic")
export MQTTRCSREQTOPIC=$(bashio::config "rcsreq_topic")
export MQTTRCSCMDTOPIC=$(bashio::config "rcscmd_topic")

# Export environment if CM17 is defined

if bashio::config.true "cm17_in_use" ; then
	bashio::log.info "CM17 is enabled"
	export CM17="True"
else
	bashio::log.info "CM11 is enabled"
fi

# Start heyu engine manually
heyu engine

# Dump config with IFS shenanigans (resetting IFS when done)
bashio::log.info "Dumping heyu config:"
heyu webhook config_dump | while IFS= read -r ROW; do
	bashio::log.info $ROW
done
IFS=$0

# Run main script
python3 -u /usr/local/bin/x10mqtt.py
