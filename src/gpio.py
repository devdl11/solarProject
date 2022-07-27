from typing import Callable

class GPIO:
  def __init__(self, uuid : str, writer : Callable, reader: Callable) -> None:
    self.uuid = uuid
    self.writer = writer
    self.reader = reader
    
  def write(self, value : int, index : int) -> None:
    self.writer(self.uuid, value, index)
    
  def read(self, index : int) -> int:
    return self.reader(self.uuid, index)