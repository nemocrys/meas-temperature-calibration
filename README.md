[![DOI](https://zenodo.org/badge/672843245.svg)](https://doi.org/10.5281/zenodo.15214427)

# meas-temperature-calibration

Scripts to control a calibrator of temperature sensors.

## 1. About Us:

The project is developed and maintained by the [Model experiments group](https://www.ikz-berlin.de/en/research/materials-science/section-fundamental-description) at the Leibniz Institute for Crystal Growth (IKZ).

## 2. Introduction:

This project is used to calibrate thermocouples with the help of the "Isotech Jupiter 4852 Basic" temperature calibrator. The goal is to completely automate the calibration process with python scripts.

## 3. Operation manual:

__Isotech Jupiter 4852 Basic:__
https://isotech.co.uk/wp-content/uploads/2020/09/BASIC-SITE-Jupiter.pdf
in English

__Comunications Manual between Jupiter 4852 Basic and PC with Modbus__
https://www.eurotherm.com/?wpdmdl=27877
in English

## 4. jupiter4852.py:
jupiter4852.py allows comunication with the Jupiter 4852. Currently the current temperature can be read out and the setpoint can be read and written.

## 5. Hardware setup:
![Hardware Setup](./pictures/setup.png)
As the Computer a Raspberry Pi 400 was used. __The Jupiter 4852 must be connected to the comupter using the official adapter by Isotherm!__ A RS232 to USB adapter can be used to connect to the computer after the Isoterm adapter.

## 6. Software setup:
### 6.1 Jupiter:

__Comms Resolution "rES" musst be "XX.X °C" not "XX.XX °C" which is used per defult.__

__Modbus Address musst be "2" even if Cal Notepad apeaers to comunicate with "1".__

For comunication asure that defualt settings are used:
Baudrate: 9600
Parity:   None
bytesize: 8
stopbits: 1

### 6.2 Script:
![Plot](./pictures/plot.png)

_rezept.txt_ has to be configured to needs. a explanations can be found there.

_config.yml_ has to be configured to needs. An example can be found.

If everything is configuered Hauptprogramm.py can be started. If a seperate window opens with a graph that updates every 5s everythng works as intendet. The Script closes automaticly. If more then 8h pass the script will close automaticly even if the program is not finnished.

## 7. Output:
A folder will be created which holds the follwing files: _plot.png_ saves the plot. data.csv stores all data. measermentData.csv stores averaged data during measerments.

## Acknowledgements

[This project](https://nemocrys.github.io/) has received funding from the European Research Council (ERC) under the European Union's Horizon 2020 research and innovation programme (grant agreement No 851768).

<img src="https://github.com/nemocrys/test-cz-induction/blob/main/EU-ERC.png">
