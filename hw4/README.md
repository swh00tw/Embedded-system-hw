# Embedded system HW4

## Usage

1. open mbed studio, and import program from https://os.mbed.com/teams/mbed-os-examples/code/mbed-os-example-ble-Button/
2. use hw4/source to replace original source folder in example project.
3. compile and run.
4. use terminal to run ble_scan_connect.py on RPI. (sudo python3 ble_scan_connect.py)
5. when click button of STM node, RPI (GATT client) will receive student_id one char at a time.
