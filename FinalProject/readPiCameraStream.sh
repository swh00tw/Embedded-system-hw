if [ -p picamera ]
then 
    rm picamera
fi
mkfifo picamera
nc -l 8080 -v > picamera