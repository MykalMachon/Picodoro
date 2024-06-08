# stdlib
import network 
import socket 
import time
import math
import random
import json

# pimoroni 
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_P4

# connect to WIFI 
import config

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.WIFI_SSID, config.WIFI_PASS)

alarm_set = True
alarm_original_seconds = 20
alarm_remaining_seconds = alarm_original_seconds

network_info = wlan.ifconfig()
print('network info:', network_info)

# set up buttons
button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

# set up display
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, rotate=0, pen_type=PEN_P4)
display.set_backlight(1)

DISP_W, DISP_H = display.get_bounds()

# PENS
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)

# display some text
display.set_font("bitmap16")
display.set_thickness(2)

def clear(update=True):
    display.set_pen(BLACK)
    display.clear()

def get_settings():
  with open("db.json", "r") as f:
    settings = json.load(f)
  return settings

def set_settings(settings):
  with open("db.json", "w") as f:
    json.dump(settings, f)

def create_http_dict(pieces):
  if pieces[0] == b'POST':
    return {
      "method": pieces[0],
      "path": pieces[1],
      "version": pieces[2],
      "body": parse_POST_body(pieces[-1])
    }
  else:
    return {
      "method": pieces[0],
      "path": pieces[1],
      "version": pieces[2],
    }

def draw_screen(state):
  clear(update=False)
  display.set_pen(WHITE)

  if wlan.isconnected():
    display.text(f"got wifi", 8, 8, scale=2)
  else:
    display.text("no wifi", 8, 8, scale=2)

  if state.get('title') == "no_alarms":
    scale_factor = 3 
    na_width = display.measure_text("no alarms set", scale=scale_factor)
    remaining_width = DISP_W - na_width
    remaining_height = DISP_H - ((16 * scale_factor) / 2) 
    display.text("no alarms set", math.floor(remaining_width / 2), math.floor(remaining_height / 2), scale=scale_factor)

  if state.get('title') == "alarm_set":
    # get string for remaining time
    scale_factor = 6
    seconds = math.floor(alarm_remaining_seconds) % 60
    minutes = math.floor(alarm_remaining_seconds / 60)
    time_str = f"{minutes:02}:{seconds:02}"

    # draw line at bottom of screen that corresponds to remaining time
    percentage_complete = alarm_remaining_seconds / alarm_original_seconds 
    percentage_remaining = 1 - percentage_complete 
    dist_to_end = math.floor(DISP_W * percentage_remaining)

    display.line(dist_to_end, DISP_H - 5, DISP_W, DISP_H - 5, 5)

    # draw time string in middle of screen
    time_width = display.measure_text(time_str, scale=scale_factor)
    remaining_width = DISP_W - time_width
    remaining_height = DISP_H - ((16 * scale_factor) / 2) 
    display.text(time_str, math.floor(remaining_width / 2), math.floor(remaining_height / 2), scale=scale_factor)
  
  if state.get('title') == "alarm_completed":
    scale_factor = 6
    na_width = display.measure_text("DONE", scale=scale_factor)
    remaining_width = DISP_W - na_width
    remaining_height = DISP_H - ((16 * scale_factor) / 2) 
    display.text("DONE", math.floor(remaining_width / 2), math.floor(remaining_height / 2), scale=scale_factor)


last_datetime = None

while True:
  current_datetime = time.time()
  if last_datetime is None:
    last_datetime = current_datetime
  
  remaining_time = current_datetime - last_datetime
  last_datetime = current_datetime
  alarm_remaining_seconds -= remaining_time

  # print(alarm_remaining_seconds)

  if alarm_set and alarm_remaining_seconds > 0:    
    draw_screen({
      "title": "alarm_set"
    })
  
  if alarm_set and alarm_remaining_seconds <= 0:
    draw_screen({
      "title": "alarm_completed"
    })
  
  if not alarm_set:
    draw_screen({
      "title": "no_alarms"
    })

  display.update()
  time.sleep(0.1)

