import logging
import threading
import typing

from extensions.dummy import Dummy, DummyGPIOType, DummyStatus, DummyType
import src.RPi.GPIO as GPIO
import src.gpio as cli_gpio
from src.storage import Storage
from enum import Enum
import uuid
import time
import os
import subprocess
import re

class GPIOExclude(Enum):
  GPIO4  = 7
  GPIO18 = 12
  GPIO22 = 15
  GPIO23 = 16
  GPIO24 = 18
  
LOOP_DELAY = 15 # We grab data every 15 seconds
ONEWIRE_READ = "/sys/bus/w1/devices/{address}/temperature"
ONEWIRE_READOLD = "/sys/bus/w1/devices/{address}/w1_slave"
ONEWIRE_DIRECTORY = "ls /sys/bus/w1/devices"

class GPIOModule:
  gpio: cli_gpio.GPIO
  def __init__(self, manifest : object, module : Dummy) -> None:
    self.name = manifest["name"]
    self.version = manifest["version"]
    self.description = manifest["description"]
    self.gpios = manifest["gpios"]
    self.gtype = manifest["subtype"]
    self.type = manifest["type"]
    self.gmap = manifest["mapping"]
    self.metadata = manifest["metadata"]
    self.background = module.background
    self.id = ""
    self.gpio = None
    self.module = module
  
  def getGPIOUsed(self) -> typing.List[int]:
    return self.gpios
  
  def getGPIOMapping(self) -> typing.List[tuple]:
    return list(zip(self.gpios, self.gmap))
  
  def isRegistered(self) -> bool:
    return self.id != ""
  
  def register(self, id : str, gpio: cli_gpio.GPIO) -> None:
    self.id = id
    self.gpio = gpio
    self.module.register_gpio(gpio)
    logging.info("GPIO: Module %s registered with id %s" % (self.name, self.id))
    
  def getOneWireAddress(self):
    return self.metadata["address"]
    
  def getGPIOType(self) -> DummyGPIOType:
    return self.gtype
  
class BaseGPIO:
  modules: typing.List[GPIOModule]
  
  def __init__(self) -> None:
    self.modules = list()
  
  def isRegistered(self, uuid: str) -> bool:
    for i in self.modules:
      if i.id == uuid:
        return True
    return False
  
  def getModule(self, uuid: str) -> GPIOModule or None:
    for i in self.modules:
      if i.id == uuid:
        return i
    return None

class DigitalGPIO(BaseGPIO):
  def register(self, module: GPIOModule, rcallback : typing.Callable, wcallback : typing.Callable) -> bool:
    mid = str(uuid.uuid4())
    gp = cli_gpio.GPIO(mid, wcallback, rcallback)
    module.register(mid, gp)
    self.modules.append(module)
    for gpio in module.getGPIOMapping():
      GPIO.setup(gpio[0], gpio[1])
    return True
  
  def unregister(self, uuid: str) -> bool:
    mod = self.getModule(uuid)
    if mod is None:
      return False
    for gpio in mod.getGPIOMapping():
      if gpio[1] == GPIO.OUT:
        GPIO.output(gpio[0], 0)
      else:
        GPIO.setup(gpio, GPIO.OUT)
    self.modules.remove(mod)
    return True
  
class AnalogGPIO(BaseGPIO):
  def register(self, module: GPIOModule) -> bool:
    pass
  
  def unregister(self, uuid: str) -> bool:
    pass

class OneWireGPIO(BaseGPIO):
  def register(self, module: GPIOModule, rcallback: typing.Callable, wcallback: typing.Callable) -> bool:
    if module.getOneWireAddress() not in os.listdir("/sys/bus/w1/devices"):
      logging.info("GPIO: OneWire address %s not found" % module.getOneWireAddress())
      return False
    mid = str(uuid.uuid4())
    gp = cli_gpio.GPIO(mid, wcallback, rcallback)
    module.register(mid, gp)
    self.modules.append(module)
    return True
  
  def unregister(self, uuid: str) -> bool:
    mod = self.getModule(uuid)
    if mod is None:
      return False
    self.modules.remove(mod)
    return True

class GPIOManager:
  thread: threading.Thread or None
  sensors: typing.List[GPIOModule]
  
  def __init__(self, dataLogger : Storage) -> None:
    logging.info("GPIOManager: Initializing...")
    self.logger = dataLogger
    self.loopRun = False
    self.thread = None
    self.sensors = list()
    ## GPIO Managers
    self.digitalgpio = DigitalGPIO()
    self.analoggpio = AnalogGPIO()
    self.onewiregpio = OneWireGPIO()
    ###
    logging.info("GPIOManager: Cleaning up...")
    GPIO.cleanup()
    logging.info("GPIOManager: Configuring GPIO...")
    GPIO.setmode(GPIO.BOARD)
    logging.info("GPIOManager: GPIO initialized !")
    logging.info("GPIOManager: Initialization done !")
    
  def __loop(self):
    while self.loopRun:
      for i in self.sensors:
        if i.isRegistered() and i.type == DummyType.SENSOR:
          try:
            i.background(self.logger.logSensorData)
          except:
            pass
      time.sleep(LOOP_DELAY)

  def addSensor(self, module : Dummy):
    # All sensors are children of Dummy class
    manifest = module.manifest()
    name = manifest["name"]
    logging.info("GPIOManager: Adding sensor %s..." % name)
    logging.info("GPIOManager: Sensor %s manifest:" % (name))
    logging.info(manifest)
    if manifest["status"] == DummyStatus.DEACTIVATED:
      logging.info("GPIOManager: Sensor %s is deactivated, skipping..." % name)
      return
    for i in manifest["gpios"]:
      if not self.isFree(i) and (manifest["subtype"] is not DummyGPIOType.ONEWIRE or len(manifest["gpios"]) > 1):
        logging.info("GPIOManager: Sensor %s cannot be loaded because GPIO %d is already used !" % (name, i))
        logging.info("GPIOManager: Giving up...")
        return
    gpiomod = GPIOModule(manifest, module)
    self.sensors.append(gpiomod)
    logging.info("GPIOManager: Registering sensor %s..." % name)
    if gpiomod.getGPIOType() == DummyGPIOType.DIGITAL:
      logging.info("GPIOManager: Sensor %s is a digital sensor..." % name)
      self.digitalgpio.register(gpiomod, self.digitalRead, self.digitalWrite)
    elif gpiomod.getGPIOType() == DummyGPIOType.ONEWIRE:
      logging.info("GPIOManager: Sensor %s is a one wire sensor..." % name)
      result = self.onewiregpio.register(gpiomod, self.oneWireRead, self.oneWireWrite)
      if not result:
        logging.info("GPIOManager: Sensor %s could not be registered, removing..." % name)
        self.sensors.remove(gpiomod)
        return
    logging.info("GPIOManager: Sensor %s added !" % name)
    
  def digitalRead(self, uuid : str, pin: int):
    if not self.digitalgpio.isRegistered(uuid):
      logging.info("GPIOManager: Sensor %s is not registered, skipping..." % uuid)
      return
    logging.info("GPIOManager: Sensor %s is reading GPIO %d..." % (uuid, pin))
    module = self.digitalgpio.getModule(uuid)
    gpios = module.getGPIOMapping()
    if gpios[pin][1] == GPIO.IN:
      return GPIO.input(gpios[pin][0])
    else:
      logging.info("GPIOManager: Sensor %s tried to read from output GPIO %d, skipping..." % (uuid, pin))
  
  def digitalWrite(self, uuid : str, pin: int, value: int):
    if not self.digitalgpio.isRegistered(uuid):
      logging.info("GPIOManager: Sensor %s is not registered, skipping..." % uuid)
      return
    logging.info("GPIOManager: Sensor %s is writing GPIO %d..." % (uuid, pin))
    module = self.digitalgpio.getModule(uuid)
    gpios = module.getGPIOMapping()
    if gpios[pin][1] == GPIO.OUT:
      GPIO.output(gpios[pin][0], value)
    else:
      logging.info("GPIOManager: Sensor %s tried to write to input GPIO %d, skipping..." % (uuid, pin))
      
  def oneWireRead(self, uuid : str, pin: int) -> object or None:
    if not self.onewiregpio.isRegistered(uuid):
      logging.info("GPIOManager: Sensor %s is not registered, skipping..." % uuid)
      return None
    module = self.onewiregpio.getModule(uuid)
    address = module.getOneWireAddress()
    logging.info("GPIOManager: Sensor %s is reading from OneWire address %s..." % (uuid, address))
    firstpath = ONEWIRE_READ.format(address=address)
    secondpath = ONEWIRE_READOLD.format(address=address)
    if os.path.isfile(ONEWIRE_READ):
      logging.info("GPIOManager: Sensor %s is using new OneWire API..." % uuid)
      command = f"cat {firstpath}"
      result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
      return result.stdout.decode("utf-8")
    elif os.path.isfile(ONEWIRE_READOLD.format(address=address)):
      # Using the function of this article : https://www.mkompf.com/weather/pionewiremini.html
      logging.info("GPIOManager: Sensor %s is using old OneWire API..." % uuid)
      value = None
      try:
        f = open(secondpath, "r")
        line = f.readline()
        if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
          line = f.readline()
          m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
          if m:
            value = str(float(m.group(2)))
        f.close()
      except (IOError) as e:
        logging.error("GPIOManager: Sensor %s could not read from OneWire address %s, skipping..." % (uuid, address))
      return value
    else:
      logging.info("GPIOManager: Sensor %s is not connected to a OneWire device, skipping..." % uuid)
      return None
    
  
  def oneWireWrite(self, uuid : str, pin: int, value: int):
    # TODO: Implement this
    pass

  def isFree(self, pin : int) -> bool:
    for i in self.sensors:
      if pin in i.getGPIOUsed():
        return False
      if pin in [i.value for i in list(GPIOExclude)]:
        return False
    return True

  def run_loop(self):
    logging.info("GPIOManager: Starting loop...")
    if self.thread is not None and self.thread.is_alive():
      logging.info("GPIOManager: Loop already running ! Killing it...")
      self.loopRun = False
      self.thread.join()
    logging.info("GPIOManager: Starting thread loop...")
    self.loopRun = True
    self.thread = threading.Thread(target=self.__loop, name="GPIOManager")
    self.thread.start()
    logging.info("GPIOManager: Loop started !")