#!/bin/bash
clear
echo '###################'
echo 'UPDATING OS'
echo '###################'
apt-get update
apt-get -y upgrade

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
echo -n "Do you want to setup the IMU? Only select 'no' if it has already been done. (y/n) > "
read response
if [ "$response" == "y" ]; then
	apt-get -y install libi2c-dev libeigen3-dev libboost-program-options-dev moreutils
	git clone https://github.com/DavidEGrayson/minimu9-ahrs /home/pi/minimu9-ahrs-setup/
	make -C /home/pi/minimu9-ahrs-setup/
	make install -C /home/pi/minimu9-ahrs-setup/
	cp ./static_files/.minimu9-ahrs /home/pi/
fi

# setup the SCRIPTS
clear
echo '###################'
echo 'SETTING UP SCRIPTS'
echo '###################'
cp -r ./scripts/ /usr/lib/swiffer-monitor/
cp ./static_files/swiffer-monitor-bootstrapper /etc/cron.d/
chmod +x /etc/cron.d/swiffer-monitor-bootstrapper
mkdir -m777 /home/pi/Logging/
mkdir -m777 /home/pi/Logging/MonitorLog
mkdir -m777 /home/pi/Logging/Unsent
mkdir -m777 /home/pi/Logging/Sent
mkdir -m777 /home/pi/Logging/UnprocessedIMU
mkdir -m777 /home/pi/Logging/UnprocessedVideo

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
