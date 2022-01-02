rm -rf picamera
if [ -p picamera ]
then 
    rm -rf picamera
fi
mkfifo picamera
nc -l 8081 -v > picamera
