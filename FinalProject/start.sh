rm -rf picamera1 picamera2
nc -l 8080 -v > picamera1 &
nc -l 8081 -v > picamera2 & 
python3 run_model_example.py
serverip=$(ipipconfig getifaddr en0)
ssh -l pi 192.168.50.243 "raspivid -n -w 320 -h 240 -o - -t 0 -b 2000000 | nc ${server} 8080"
#rpiIP1=$1
#rpiIP2=$2
#ssh -l pi $1 "raspivid -n -w 320 -h 240 -o - -t 0 -b 2000000 | nc ${server} 8080"
#ssh -l pi $2 "raspivid -n -w 320 -h 240 -o - -t 0 -b 2000000 | nc ${server} 8080"