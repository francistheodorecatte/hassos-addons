# quick script to build our own full thermostat auto report, when RCS failed to!

# use the provided housecode variable from heyu to build the houseunit code
hu="${X10_Housecode}5"

# heyu should already check for a unit code of 6, so we just need to check if the preset level is 9.
# we should have the current temperature (preset 1) due to an auto report, so call the rest ourselves.
# use rcs_req to have heyu wait for the thermostat to respond, to avoid collisions.
if [[ $X10_PresetLevel -eq 9 ]]; then
        heyu rcs_req preset $hu 2
        heyu rcs_req preset $hu 3
        heyu rcs_req preset $hu 4
        heyu rcs_req preset $hu 5
        heyu rcs_req preset $hu 6
fi

exit
