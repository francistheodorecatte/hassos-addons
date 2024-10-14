## x10mqtt version v0.3.5-3

### Changes since 0.3.5-1

- quick (hotfixed!!) math bugfix on the dimming value inversion fix


### Changes since 0.3.5

- build supporting files for RCS protocol status reporting (python script changes TBD)
- invert dimming values coming from Home Assistant


### Changes since 0.3.4-1

- preliminary groundwork for RCS protocol support


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
