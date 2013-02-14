Cacheberry-Pi
=============

Cacheberry Pi is a geocaching assistant built upon the Raspberry Pi platform.

It's intended to be a permanent fixture in the car and alert you of nearby caches (when stopped) or along your route (when driving).  The intent is not to replace your handheld GPSr but to complement it. 

See an overview [Video on YouTube](http://youtu.be/bwD6K2EeeV8) or view the [project homepage](http://jclement.ca/cacheberry-pi/).

The information that follows is for the Cacheberry Pi as built by [Steve Whitcher](steve@whitcher.org).  The hardware in this version is somewhat different from the original, including a serial connected GPS and a different i2c backpack on the LCD.  The code has also been modified to localize the time, speed, and distances displayed on the LCD. 

# Features #
* Smart Search: depending on speed and direction of travel
* Ability to maintain a database of 20k+ geocaches
* Easy syncing of cache lists with GSAK via thumb drive
* Automatic tracklog recording and syncing with thumb drive
* Easy customization of settings in the 'cacheberrypi.cfg' file.

# Hardware #
* [RaspberryPi B](http://www.newark.com/jsp/search/productdetail.jsp?id=43W5302&Ntt=43W5302&)
* [Arduino IIC / I2C Serial 2.6" LCD 1602 Module Display](http://amzn.to/U7Trus)
* [Adafruit Ultimate GPS breakout](http://www.adafruit.com/products/746) - Likely almost any other NMEA GPS will suffice
* [4GB AmazonBasics Class 10 SD Card](http://amzn.to/WW2j4V)
* 12V USB Charger + MicroUSB cable

# Software Requirements #
* Python 2.7
* [GPsd](http://www.catb.org/gpsd/) - Available through APT
* [PySpatialite](http://code.google.com/p/pyspatialite/) - Available through APT
* [LCDProc] (http://www.lcdproc.org/) - Available through APT (required custom display driver)                                                      
* [RPi.GPIO] (http://pypi.python.org/pypi/RPi.GPIO) 
* [AutoFS] (http://www.autofs.org/) - Available through APT


***                                     
# Setup Instructions #


## Prerequisites ##

### Install required packages from APT###

~~~
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install autofs lcdproc python-pyspatialite sqlite3 gpsd vim-nox gpsd-clients screen python-dev i2c-tools python-smbus git
~~~

###Install RPi.GPIO and LCDProc python libraries###

~~~
$ cd /usr/src
$ sudo wget http://pypi.python.org/packages/source/R/RPi.GPIO/RPi.GPIO-0.4.1a.tar.gz#md5=9acdb66290350aaa74b99de859ded153
$ sudo tar -xvf RPi.GPIO-0.4.1a.tar.gz
$ cd RPi.GPIO-0.4.1a/
$ sudo python setup.py install
~~~

~~~
$ cd /usr/src
$ sudo wget http://pypi.python.org/packages/source/l/lcdproc/lcdproc-0.03.tar.gz#md5=177328fd30c973151b5e75f9c1b992c7
$ sudo tar -xzf lcdproc-0.03.tar.gz
$ cd lcdproc-0.03/
$ sudo python setup.py install
~~~

## Download CacheberryPi Software ##

###Clone the CacheberryPi repository to your "pi" user's home folder###

~~~
$ cd ~
$ git clone https://github.com/Aurock/Cacheberry-Pi.git
~~~

## Configuration ##

###Install the ifup script so we can see network configuration on the LCD###

~~~
$ cd ~/Cacheberry-Pi/util
$ sudo cp ifup-lcdproc /etc/network/if-up.d
$ sudo chmod 755 /etc/network/if-up.d/ifup-lcdproc
~~~

###Install lcdproc configuration files and LCD driver###

~~~
$ cd ~/Cacheberry-Pi/misc
$ sudo cp LCDd.conf /etc
$ sudo cp hd44780-i2c/hd44780.so /usr/lib/lcdproc/
~~~

###Setup udev to make GPS devices world write/readable###

~~~
$ cd ~/Cacheberry-Pi/misc
$ sudo cp 70-persistent-net.rules  /etc/udev/rules.d/
~~~

###Edit 2 files to enable i2c###

*In /etc/modprobe.d/raspi-blacklist.conf Add a # before the line "blacklist i2c-bcm2708".
*Add the following 2 lines in /etc/modules
~~~
i2c-dev
i2c-bcm2708
~~~

###Run the gpsd reconfiguration wizard###
~~~
$ sudo dpkg-reconfigure
~~~
Accept the default choices in the wizard except for the 'device the GPS receiver is connected to.'  Change that setting to "/dev/ttyAMA0"

###Set CacheberryPi to run on startup###
Edit /etc/rc.local to add the following before "exit 0"

~~~
nohup /home/pi/Cacheberry-Pi/start &
~~~

###Configure autofs for update functionality###

~~~
$ cd ~/Cacheberry-Pi/misc
$ cp auto.removable /etc
$ cp auto.master /etc
~~~

###Change host name###
Edit /etc/hosts and /etc/hostname, replacing "raspberrypi" with "cacheberrypi".

## GSAK Export Settings ##
When displaying a cache, the top line of the display will show the cache description, and the bottom line will show the Waypoint Name.  These can be configured when exporting the cache data from GSAK.  Customize the data exported using [GSAK's "Special Tags"](http://gsak.net/help/hs10300.html#scustom). 

For example, the waypoint name and cache description could be set as follows: 

* Waypoint Name = "%Caches_FavPoints (%Dif/%Ter)"
* Cache Description Format = "%Name by %By"

