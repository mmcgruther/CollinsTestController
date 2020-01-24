# Collins Test Controller
Automated control of scientific equipment over TCP/IP network with a Raspberry Pi.
### Installation
Install Raspbian on Raspberry Pi.
Required packages: python3, pyvisa, pyvisa-py, pyqt5
```sh
$ sudo apt-get update
$ sudo apt-get install pyvisa
$ sudo pip3 install pyvisa-py
$ sudo apt-get install python3-pyqt5
$ sudo apt-get install qt5-default pyqt5-dev pyqt5-dev-tools
```
### Equipment Configuration
Populate equipment.json
### Operation
Run main.py
```sh
python3 main.py
```
Establish equipment connections, then execute test
