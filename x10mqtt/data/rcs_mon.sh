# quick script to build our own full thermostat auto report, when RCS failed to!

# use the provided housecode variable from heyu to build the houseunit code
hu="${X10_Housecode}5"

# heyu should already check for a unit code of 6, so we just need to check if the preset level is 9.
# we should have the current temperature (preset 1) due to an auto report, so call the rest ourselves.
# the thermostat takes 2-3 seconds to respond, hence the sleep between calls to avoid collisions.
if [[ $X10_PresetLevel -eq 9 ]]; then
	heyu preset $hu 2
	sleep 4
	heyu preset $hu 3
	sleep 4
	heyu preset $hu 4
	sleep 4
	heyu preset $hu 5
	sleep 4
	heyu preset $hu 6
	sleep 4
fi

exit
