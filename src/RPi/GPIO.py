# This file is useful when programming. When the program starts, it will load the real RPi.GPIO module.

## We define some dummy functions to make the autocompletation work.


BOARD = 0
BCM   = 1
IN    = 0
OUT   = 1
RISING = 2


def cleanup():
  pass

def setmode(mode : int):
  pass

def setup(channel : int, mode : int):
  pass

def input(channel : int):
  return False

def output(channel : int, value : int):
  pass

def wait_for_edge(channel : int, edge : int):
  pass

def add_event_detect(channel : int, edge : int):
  pass

def event_detected(channel : int):
  return False
