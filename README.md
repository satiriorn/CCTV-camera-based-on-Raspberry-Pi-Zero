# CCTV camera based on raspberry pi zero

The project consists of the following elements:
- Raspberry Pi Zero v1.3;
- OTG USB for connect usb wifi if built-in, it is not needed;
- 5Mp RPi Camera (E) for Raspberry Pi from Waveshare;
- PIR SR501;

Scheme of connecting elements:

<img src="https://github.com/satiriorn/CCTV-camera-based-on-Raspberry-Pi-Zero/blob/Satiriorn/image/Scheme_connected_elements.jpg" alt="Scheme of connecting elements"/>

Camera startup process:
-Install on sd card Raspbian: https://www.raspberrypi.com/software/
-Enter ssid and password for connecting to WiFi;
-Unlock VNC server or connect to raspberry via SSH;
-Clone this repository;
-add os.getenv("CHAT_ID")- chat_id of your chat and os.getenv("TOKEN") - token of your bot.
-Launching the camera via command - python RaspberryIPCameraBot.py

View of the camera in the printed case:
<img src="https://github.com/satiriorn/CCTV-camera-based-on-Raspberry-Pi-Zero/blob/Satiriorn/image/result.jpg" alt="Result"/>

Test camera in telegram:
<img src="https://github.com/satiriorn/CCTV-camera-based-on-Raspberry-Pi-Zero/blob/Satiriorn/image/test.jpg" alt="Result"/>