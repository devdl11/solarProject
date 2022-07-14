# Dummy Sensor
from enum import Enum
from typing import Callable

class DummyStatus(Enum):
  DEACTIVATED = 0
  ACTIVATED = 1

class DummyType(Enum):
  SENSOR = 0
  MOTOR  = 1

class DummySensorType(Enum):
  ANALOG  = 0
  DIGITAL = 1


class Dummy:
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
    self.gpio = None

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
      "subtype": DummySensorType.ANALOG,
      "status": DummyStatus.DEACTIVATED,
    }
    
  def read(self) -> object:
    """ Reads the sensor and returns its value.

    Returns:
        object: The value of the sensor.
    """    
    return
    
  def background(self) -> None:
    """ Background code of the extension. Here the extension can grab some data and save it in database.
    """    
    pass
  
  def input_api(self) -> object:
    pass