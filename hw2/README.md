# Step 1

Open mbed_app.json, modify config.hostname.value to IP your server runs on, then modify target_overrides.\*.nsapi.default-wifi-ssid and target_overrides.\*.nsapi.default-wifi-password to wifi your board connect.

# Step 2

Modify main.cpp line 49. Set port number your host listening.

# Step 3

Run server.
```
python3 server.py
```
and run main.cpp in mbed studio.
