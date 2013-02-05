#!/usr/bin/env python

import os
import unicodedata
from lcdproc.server import Server


class GeocacheDisplay:
  def __init__(self, scroll_speed=3):
    self.__lcd = Server()
    self.__lcd.start_session()
    self.__screen = self.__lcd.add_screen("cache")
    self.__screen.set_heartbeat("off")
    self.__screen.set_duration(10)
    self.__screen.set_priority("hidden")
# Scroller Widget parameters - SCREEN, REF, LEFT, TOP, RIGHT, BOTTOM, DIRECTION, SPEED, TEXT
# Scroll speed increases as the speed setting decreases.  1 is the fastest.
    self.__title_widget = self.__screen.add_scroller_widget("title",1,1,12,1,"h",scroll_speed,"")
    self.__code_widget = self.__screen.add_string_widget("code","",y=2)
    self.__distance_to_cache_widget = self.__screen.add_string_widget("dist","",y=2, x=9)
    self.__bearing_to_cache_widget = self.__screen.add_string_widget("btc","",y=2, x=14)
    self.__bearing_widget = self.__screen.add_string_widget("bearing","",y=1, x=14)

  def update(self, cache_name, code, bearing, bearing_to_cache, distance_to_cache, MEASUREMENT_STANDARD):
    self.__title_widget.set_text(cache_name.encode('ascii'))
    self.__code_widget.set_text(code.encode('ascii'))
    if MEASUREMENT_STANDARD == 'US':
      display_distance = (distance_to_cache / 1609.34)
      small_display_distance = (display_distance * 5280)
      units = 'mi'
      small_units = 'ft' 
      threshold = 1609.34
    elif MEASUREMENT_STANDARD == 'METRIC':
      display_distance = (distance_to_cache / 1000)
      small_display_distance = (distance_to_cache)
      units = 'km'
      small_units = 'm'
      threshold = 1000
    else:
      raise ValueError('MEASUREMENT_STANDARD must be "US" or "METRIC"')
    if (distance_to_cache > threshold):
      self.__distance_to_cache_widget.set_text(('%0.0f' % display_distance) + units)
    else:
      self.__distance_to_cache_widget.set_text(('%0.0f' % small_display_distance) + small_units)
    self.__bearing_widget.set_text(bearing)
    self.__bearing_to_cache_widget.set_text(bearing_to_cache)

  def hide(self):
    self.__screen.set_priority("hidden")

  def show(self, foreground):
    if foreground:
      self.__screen.set_priority("foreground")
    else:
      self.__screen.set_priority("info")

