#!/bin/bash
# quick script to build our own full thermostat auto report, when RCS failed to!

# use the provided housecode variable from heyu to build the houseunit code
hu="${X10_Housecode}5"

pipe="/tmp/rcsmon"

# heyu should already check for a unit code of 6, so we just need to check if the preset level is 9 or 10.
# we don't care what auto send status register called this script, so just request status from all six registers.
# use rcs_req to request each register directly w/o having to parse live heyu monitor, then mangle output into usability.
# then concat all register variables into a json payload for x10mqtty, and send down a named pipe placed in /tmp.
if [[ $X10_PresetLevel -eq 9 ]] || [[ $X10_PresetLEvel -eq 10 ]]; then

        # check if our pipe exists; create it if not.
        if [[ ! -p $pipe ]]; then
                mkfifo $pipe
        fi

        temp=`heyu rcs_req preset ${hu} 1 | cut -d "=" -f2- | cut -d ":" -f1 | awk '{gsub(/^ +| +$/,"")} {print $0}'`
        setpnt=`heyu rcs_req preset ${hu} 2 | cut -d "=" -f2- | cut -d ":" -f1 | awk '{gsub(/^ +| +$/,"")} {print $0}'`
        mode=`heyu rcs_req preset ${hu} 3 | cut -d "=" -f2- | cut -d ":" -f1 | awk '{gsub(/^ +| +$/,"")} {print $0}'`
        fanstat=`heyu rcs_req preset ${hu} 4 | cut -d "=" -f2- | cut -d ":" -f1 | awk '{gsub(/^ +| +$/,"")} {print $0}'`
        sbmode=`heyu rcs_req preset ${hu} 5 | cut -d "=" -f2- | cut -d ":" -f1 | awk '{gsub(/^ +| +$/,"")} {print $0}'`
        sbdelt=`heyu rcs_req preset ${hu} 6 | cut -d "=" -f2- | cut -d ":" -f1 | awk '{gsub(/^ +| +$/,"")} {print $0}'`

        # assemble the payload and echo it down the pipe (will wait in background until x10mqtt reads it in)
        payload="{\"housecode\": \"$X10_Housecode\", \"temperature\": \"$temp\", \"setpoint\": \"$setpnt\", \"mode\": \"$mode\", \"fan\": \"$fanstat\", \"sb_mode\": \"$sbmode\", \"sb_delta\": \"$sbdelt\"}"
        echo $payload > $pipe &

fi

exit
