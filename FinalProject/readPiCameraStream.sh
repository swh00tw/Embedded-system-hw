
rm -rf picamera

mkfifo picamera
nc -l 8080 -v > picamera