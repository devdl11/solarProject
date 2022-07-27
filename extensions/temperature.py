from extensions.dummy import Dummy, DummyGPIOType, DummyStatus, DummyType, DummyGPIOStatus
import typing

class Temperature(Dummy):
  def __init__(self) -> None:
    super().__init__()
  
  def manifest(self) -> object:
    """ Returns the manifest of the extension.

    Returns:
        object: The manifest of the extension.
    """    
    return {
      "name": "Temperature",
      "version": "1.0.0",
      "description": "Temperature sensor 1",
      "type": DummyType.SENSOR,
      "subtype": DummyGPIOType.ONEWIRE,
      "status": DummyStatus.ACTIVATED,
      "uuid": "aae466ec-dcc2-4265-b675-c7323f335070",
      "gpios": [4], # The GPIO order has to be the same as the mapping order
      "mapping": [
        DummyGPIOStatus.IN
      ],
      "metadata" : {
        "address" : "28-00000736b83e", # Address of the sensor in case of onewire
      }
    }
    
  def read(self) -> str:
    data = self.read_raw()
    if int(data) == 0xFF:
      return "Error: No data"
    else:
      return "Temperature: " + str(data/1000.0) + "°C"
    
  def read_raw(self) -> float or int:
    result = self.gpio.read(0)
    if result is None:
      return 0xFF
    else:
      return float(result)
  
  def background(self, callback: typing.Callable) -> None:
    """ Background code of the extension. Here the extension can grab some data and save it in database.
    """
    data = self.read()
    raw = self.read_raw()
    callback(self.manifest()["uuid"], raw, data)
    