import logging
import threading
import RPi.GPIO as GPIO

class GPIOManager:
  thread: threading.Thread or None
  
  def __init__(self) -> None:
    logging.info("GPIOManager: Initializing...")
    self.loopRun = False
    self.thread = None
    logging.info("GPIOManager: Cleaning up...")
    

  def __loop(self):
    pass

  def run_loop(self):
    logging.info("GPIOManager: Starting loop...")
    if self.thread is not None and self.thread.is_alive():
      logging.info("GPIOManager: Loop already running ! Killing it...")
      self.loopRun = False
      self.thread.join()
    logging.info("GPIOManager: Starting loop thread...")
    self.loopRun = True
    self.thread = threading.Thread(target=self.__loop, name="GPIOManager")
    self.thread.start()
    logging.info("GPIOManager: Loop started !")