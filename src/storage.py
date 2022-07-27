from pickle import FALSE
import sqlite3
import logging
import os

class Storage:
  TABLES = {
    "SensorsLogs" : "CREATE TABLE {name} (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, sensor_id VARCHAR(64), raw REAL, value VARCHAR);",
  }
    
  def __init__(self, databasePath : str) -> None:
    logging.info("Storage: Initializing...")
    if not os.path.exists(databasePath):
      logging.info("Storage: Database file does not exist, creating it...")
      os.makedirs(os.path.dirname(databasePath))
    
    self.is_manipulating = False
    self.connection = sqlite3.connect(databasePath, check_same_thread=False)
    logging.info("Storage: Database connected !")
    logging.info("Storage: Running bootstrap...")
    self.__bootstrap()
    logging.info("Storage: Bootstrap done !")
    logging.info("Storage: Initialized !")
    
  def __doTableExist(self, name : str) -> bool:
    cursor = self.connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return len(cursor.fetchall()) > 0 
    
  def __bootstrap(self):
    cursor = self.connection.cursor()
    for i in self.TABLES.keys():
      if not self.__doTableExist(i):
        # create the table
        cursor.execute(self.TABLES[i].format(name=i))
        self.connection.commit()
        logging.debug("Storage: Table {name} created !".format(name=i))
        
  def waitUntilFree(self):
    while self.is_manipulating:
      pass
        
  def logSensorData(self, sensorId : str, raw : float, value : str) -> None:
    self.waitUntilFree()
    self.is_manipulating = True
    cursor = self.connection.cursor()
    logging.debug("Storage: Logging sensor %s data..." % sensorId)
    cursor.execute("INSERT INTO SensorsLogs (timestamp, sensor_id, raw, value) VALUES (strftime('%s', 'now'), ?, ?, ?)", (sensorId, raw, value))
    self.connection.commit()
    logging.debug("Storage: Sensor data logged !")
    self.is_manipulating = False