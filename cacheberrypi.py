#!/usr/bin/env python

import os
import string
import time
import lib.gislib as gislib
from lib.ledhandler import LedHandler, LED_ON, LED_OFF
from lib.gpshandler import GpsHandler
from lib.geocachefinder import GeocacheFinder
from lib.geocachedisplay import GeocacheDisplay
from lib.geocacheloader import GeocacheLoader
from lib.tracklogexporter import TracklogExporter
from lib.dashboard import Dashboard
import lib.databaseinit
from pyspatialite import dbapi2 as spatialite
from calendar import timegm
import ConfigParser

config = ConfigParser.RawConfigParser({'MEASUREMENT_STANDARD': 'US', 'TIME_ZONE': 'US/Central'})
config.read('cacheberrypi.cfg')

MEASUREMENT_STANDARD = config.get('Settings', 'MEASUREMENT_STANDARD')
timezone = config.get('Settings', 'TIME_ZONE')
SCROLL_SPEED = config.get('Settings', 'DISPLAY_SCROLL_SPEED')
GEOCACHE_SOURCE = config.get('Advanced', 'GEOCACHE_SOURCE')
TRACKLOG_TARGET = config.get('Advanced', 'TRACKLOG_TARGET')
TRACKLOG_EXPORT_TARGET = config.get('Advanced', 'TRACKLOG_EXPORT_TARGET')
DATABASE_FILENAME = config.get('Advanced', 'DATABASE_FILENAME')
LED_PINS = map(int,(config.get('Advanced', 'LED_PINS')).split(','))
LED_SEARCH_STATUS = 2
LED_CLOSE = 1


os.environ['TZ'] = timezone
time.tzset()

def mainloop(led, gps, finder, geocache_display, dashboard):
  while 1:
    # grab current state from GPS and update finder location
    gps_state = gps.state()
    finder.update_position(gps_state['p'])
    finder.update_speed(gps_state['s'])
    finder.update_bearing(gps_state['b'])

    if MEASUREMENT_STANDARD == 'US':
        speed = (gps_state['s'] * 2.23694)
        units = 'mph'
    elif units == 'METRIC':
        speed = (gps_state['s'] * 3.6)
        units = 'kph'
    else:
        raise ValueError('MEASUREMENT_STANDARD must be "US" or "METRIC"')

    try:
      clock = localtime(time.strptime(gps_state['t'], '%Y-%m-%dT%H:%M:%S.000Z'))
    except:
      clock = None

    dashboard.update(
        clock,
        speed, 
        gislib.humanizeBearing(gps_state['b']),
        units)

    # grab current closest cache 
    closest = finder.closest()

    if closest:
      distance = gislib.getDistance(gps_state['p'], closest['position']) * 1000
      geocache_display.update(
          closest["description"],
          closest["code"],
          gislib.humanizeBearing(gps_state['b']) if gps_state['s'] > 2 else '',
          gislib.humanizeBearing(gislib.calculateBearing(gps_state['p'], closest['position'])),
          distance,
          MEASUREMENT_STANDARD
          )

      geocache_display.show(distance < 1000)  #if within 1km show in foreground (on top)

      # blink close light if we are not moving and within 100m or if we are moving and
      # our ETA is within 45 seconds.
      if (gps_state['s'] < 10 and distance < 100) or \
        (gps_state['s'] >= 10 and (float(distance)/gps_state['s']) < 45):
        led.toggle(LED_CLOSE)
      else:
        led.set(LED_CLOSE, LED_ON)

    else:
      geocache_display.hide()

    time.sleep(.5)

def localtime(gmttime):
    unixtime = timegm(gmttime)
    clock = time.localtime(unixtime)
  
if __name__=='__main__':

  if not os.path.exists(DATABASE_FILENAME):
    lib.databaseinit.create(DATABASE_FILENAME)

  led = LedHandler(LED_PINS)

  gps = GpsHandler(TRACKLOG_TARGET)
  gps.start()

  tracklogexport = TracklogExporter(TRACKLOG_TARGET, TRACKLOG_EXPORT_TARGET)
  tracklogexport.start()

  finder = GeocacheFinder(DATABASE_FILENAME, lambda: led.toggle(LED_SEARCH_STATUS))
  finder.start()

  geocache_display = GeocacheDisplay(SCROLL_SPEED)

  loader = GeocacheLoader(DATABASE_FILENAME, GEOCACHE_SOURCE, 
      lambda: finder.pause(),
      lambda: finder.unpause())
  loader.start()

  dashboard = Dashboard()

  mainloop(led, gps, finder, geocache_display, dashboard)
