# Dummy Module
from enum import Enum
from typing import Callable
import typing

from src.gpio import GPIO

class DummyStatus(Enum):
  DEACTIVATED = 0
  ACTIVATED = 1

class DummyType(Enum):
  SENSOR = 0
  MOTOR  = 1
  
class DummyGPIOType(Enum):
  ANALOG  = 0
  DIGITAL = 1
  ONEWIRE = 2

class DummyGPIOStatus(Enum):
  IN = 0
  OUT = 1

class Dummy:
  gpio: GPIO
  api: typing.List[object]
  class InputApi:
    def __init__(self, func : Callable, desc : str, name : str) -> None:
      self.callback = func
      self.desc = desc
      self.name = name
      
    def getDescription(self) -> str:
      return self.desc
    
    def getName(self) -> str:
      return self.name
    
    def __call__(self, name : str) -> bool:
      if name == self.name:
        self.callback()
        return True
      return False
  
  def __init__(self) -> None:
    """ Initializes the extension.
    """
    self.gpio = None
    # In this variable we define all the input API of the extension.
    self.api = [
      self.InputApi(self.input_exemple, "Example of how to use the input API.", "input_exemple")
    ]

  def manifest(self) -> object:
    """ Returns the manifest of the extension.

    Returns:
        object: The manifest of the extension.
    """    
    return {
      "name": "Dummy",
      "version": "1.0.0",
      "description": "Dummy sensor",
      "type": DummyType.SENSOR,
      "subtype": DummyGPIOType.ANALOG,
      "status": DummyStatus.DEACTIVATED,
      "uuid": "62b5c377-94f3-4fb9-a134-40b8696a4e37",
      "gpios": [0], # The GPIO order has to be the same as the mapping order
      "mapping": [
        DummyGPIOStatus.OUT
      ],
      "metadata" : {
        "address" : "random", # Address of the sensor in case of onewire
      }
    }
    
  def read(self) -> object:
    """ Reads the sensor and returns its value.

    Returns:
        object: The value of the sensor.
    """    
    return
  
  def read_raw(self) -> object:
    pass
    
  def background(self, callback: typing.Callable) -> None:
    """ Background code of the extension. Here the extension can grab some data and save it in database.
    """    
    pass
  
  def input_api(self) -> typing.List[object]:
    return self.api
  
  def register_gpio(self, gpio : GPIO) -> None:
    self.gpio = gpio
    
  def input_exemple(self) -> None:
    """ Example of how to use the input API.
    In this function we write what we want to the sensor/actuator.
    """
    pass