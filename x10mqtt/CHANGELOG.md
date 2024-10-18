## x10mqtt version v0.3.8-3

### Changes since 0.3.8

- Hotfix(es) for when housecode config line is left empty
- Also, sorry the config migration will wipe your config

### Changes since 0.3.7-9

- rcs_req now confirmed working
- Migrate config to yaml
- Updates to docs

### Changes since 0.3.7-1

- Print received payload to console
- Correctly append housecode to paho command + catch exceptions
- Several bugfixes + hotfixes for RCS status

### Changes since 0.3.7

- Hotfix for named pipe not existing


### Changes since 0.3.6-4

- Reworked rcs_mon.sh to pipe output of rcs_req into a json payload
- Initial test of x10mqtt rcs_stat MQTT message support
- Updates to docs


### Changes since 0.3.6-3

- Fix for heyu config dump
- Updates to docs


### Changes since 0.3.6-2

- Hotfix for typo in CM10A configuration enablement


### Changes since 0.3.6

- Dump heyu config to addon log at runtime.


### Changes since 0.3.5-3

- Add configuration flag to enable using older (ha!) CM10A computer interfaces


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
