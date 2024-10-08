## x10mqtt version v0.3.4-1

### Changes since 0.3.4

- quick bugfix because str cannot math

### Changes since 0.3.3-3

- change dimming behavior so it works intuitively with all light, at the cost of potentially causing the lights to flicker.


###  Changes since v0.3.3 

- actually fix dim topic exceptions (HA passes a float; paho-mqtt expects a string.)
  

###  Changes since v0.3.2

- fix build errors
- fix dim topic exceptions


###  Changes since v0.3.0

- Bump/revert heyu from 2.11 branch to the latest in the 2.10 branch (2.10.3) for better USB-to-Serial chipset compatibility
- Update docs with more info on CM11-compatible modules
- Update docs to include info on using CM17A with powerline modules
- Update docs with info on common X10 problems
