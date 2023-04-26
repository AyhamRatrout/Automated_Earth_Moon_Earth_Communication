# Installation Steps
The following describe the steps needed to install each part of the required software.

## Python 3:
```
sudo apt install python3-distutils
```

## Pigpio Library:
```
wget https://github.com/joan2937/pigpio/archive/master.zip
unzip master.zip
cd pigpio-master
make
sudo make install
sudo pigpiod
sudo bash -c 'echo -e "@reboot root /usr/local/bin/pigpiod\n" > /etc/cron.d/1_pigpiod
```

## Nano Text Editor:
```
cd ~
git clone https://github.com/scopatz/nanorc.git ~/.nano
cat ~/.nano/nanorc >> ~/.nanorc
echo "set tabsize 4" >> ~/.nanorc
echo "set tabstospaces" >> ~/.nanorc
```

## PiTFT Touchscreen:
```
sudo apt install python3-pip
cd ~
sudo pip3 install --upgrade adafruit-python-shell click
sudo apt-get install -y git
git clone https://github.com/adafruit/Raspberry-Pi-Installer-Scripts.git
cd Raspberry-Pi-Installer-Scripts
sudo python3 adafruit-pitft.py --display=28c --rotation=180 --install-type=fbcp
sudo dpkg-reconfigure console-setup
```
* UTF-8
* Guess optimal character set
* Terminus
* 6x12 (framebuffer only).
* Then reboot machine

## Kivy for UI:
```
sudo apt-get update
sudo apt install python3-dev libmtdev1
sudo pip3 install https://connected-devices.s3.amazonaws.com/Kivy-2.1.0-cp37-cp37m-linux_armv7l.whl
sudo pip3 install kivy_examples pillow
```

## MQTT Communication Broker:
```
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients -y
```
## Python Paho:
```
sudo pip3 install paho-mqtt
```

## Supervisor:
```
sudo apt-get install supervisor
```
* Make sure to move all .conf files in the supervisor directory of this repository into /etc/supervisor/conf.d/

## Pyserial
```
sudo pip3 install pyserial
```
