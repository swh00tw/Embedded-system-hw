# Usage

```
# open a terminal
./readPiCameraStream.sh

# chmod +x ./readPiCameraStream.sh when first time execute
```

sometimes, you have to type:

```
rm -rf picamera
```

before using this script

Then,

```
# open another terminal
python3 run_model_example.py
```

And use Rpi terminal type:

```
raspivid -n -w 320 -h 240 -o - -t 0 -b 2000000 | nc <your_IP> 8080
```
