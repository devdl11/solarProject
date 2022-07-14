from typing import Callable

class GPIO:
  def __init__(self, uuid : str, writer : Callable) -> None:
    self.uuid = uuid
    self.writer = writer
    
  def write(self, value : int) -> None:
    self.writer(self.uuid, value)