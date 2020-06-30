#!/bin/bash

clear
echo '###################'
echo 'UPDATING OS'
echo '###################'
apt-get update
apt-get -y upgrade

# setup wifi
clear
echo '###################'
echo 'SETTING UP WIFI'
echo '###################'
git clone https://github.com/joshdboss/RaspiWifi /home/pi/raspiwifi-setup/
python3 /home/pi/raspiwifi-setup/initial_setup.py

# setup the interfaces
clear
echo '###################'
echo 'SETTING UP INTERFACES'
echo '###################'
raspi-config nonint do_camera 0
raspi-config nonint do_i2c 1
raspi-config nonint do_wifi_country DE

# setup the RTC
clear
echo '###################'
echo 'SETTING UP REAL-TIME CLOCK'
echo '###################'
apt-get install python-smbus i2c-tools #not necessary, but helpful for diagnosis
if grep -xq 'dtoverlay=i2c-rtc,ds1307' /boot/config.txt ; then
  true
else
	echo 'dtoverlay=i2c-rtc,ds1307' >> /boot/config.txt
fi  
cp ./static_files/hwclock-set /lib/udev/

# setup the IMU
clear
echo '###################'
echo 'SETTING UP IMU'
echo '###################'
apt-get -y install libi2c-dev libeigen3-dev libboost-program-options-dev moreutils
git clone https://github.com/DavidEGrayson/minimu9-ahrs /home/pi/minimu9-ahrs-setup/
make -C /home/pi/minimu9-ahrs-setup/
make install -C /home/pi/minimu9-ahrs-setup/
cp ./static_files/.minimu9-ahrs /home/pi/

# setup the SCRIPTS
clear
echo '###################'
echo 'SETTING UP SCRIPTS'
echo '###################'
cp ./scripts/ /usr/lib/swiffer-monitor/
cp ./static_files/swiffer-monitor-bootstrapper /etc/cron.d/
mkdir /home/pi/Logging/
mkdir /home/pi/Logging/Unsent
mkdir /home/pi/Logging/Sent
mkdir /home/pi/Logging/UnprocessedIMU
mkdir /home/pi/Logging/UnprocessedVideo


# reboot
clear
echo '###################'
echo 'FINISHING UP'
echo '###################'
echo -n "Reboot required for changes to take effect. Reboot? (y/n) > "
	read response
	if [ "$response" == "y" ]; then
	    reboot
	fi
