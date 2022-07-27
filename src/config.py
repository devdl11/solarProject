import json
from src.utility import removeEndOfLine
from src.solarparser import configParser
from enum import Enum

## Some constants
### We need to set up these paths because docker is bonded to them
LOG_DIRECTORY = "logs/"
DATA_DIRECTORY = "data/"
###

class SolarLoggingLevel(Enum):
  DEBUG     = 0
  INFO      = 1
  WARNING   = 2
  ERROR     = 3
  CRITICAL  = 4
  

def translateSolarLoggingLevel(level: SolarLoggingLevel) -> int:
  if level == SolarLoggingLevel.DEBUG:
    return 10
  elif level == SolarLoggingLevel.NORMAL:
    return 20
  elif level == SolarLoggingLevel.WARNING:
    return 30
  elif level == SolarLoggingLevel.ERROR:
    return 40
  elif level == SolarLoggingLevel.CRITICAL:
    return 50

class Configuration:
  def __init__(self, default_config : str):
    # We pass a valid json string containing the default configuration
    config_obj = json.loads(default_config)
    
    self.default = config_obj
    self.load(default_config)
    
  def load(self, config: str):
    config = json.loads(config)
    self.logging = config["logging"]
    self.string = config["string"]
    self.database = config["database"]
    
  def getJoinSeparator(self) -> str:
    return self.string["joinSep"]
  
  def getKeySeparator(self) -> str:
    return self.string["keySep"]

  def getDoKeySpace(self) -> bool:
    return self.string["keySpace"]
    
  def getLoggingPath(self) -> str:
    return LOG_DIRECTORY + self.logging["path"]
  
  def getArchiveLoggingPath(self) -> str:
    return LOG_DIRECTORY + self.logging["archive"]["path"]
  
  def getArchiveFormat(self) -> str:
    return self.logging["archive"]["format"]
  
  def getLoggingInFileDateFormat(self) -> str:
    return self.logging["inFileDateFormat"]
  
  def getLoggingInFileFormat(self) -> str:
    return self.logging["inFileFormat"]
  
  def getArchiveTimestampKey(self) -> str:
    return self.logging["archive"]["key"]
   
  def getArchiveNoTimestampFormat(self) -> str:
    return configParser(self.logging["archive"]["noTimestampFormat"], self.getJoinSeparator())
  
  def getLoggingLevel(self) -> int:
    return translateSolarLoggingLevel(SolarLoggingLevel(self.logging["level"]))
  
  def getArchiveFormattedHeader(self, timestamp: int) -> str:
    # We suppose that the header template exist
    with open(self.logging["archive"]["header"]) as f:
      header = f.readlines()
    final = list()
    for l in header:
      if self.getArchiveTimestampKey() in l:
        line = self.getArchiveTimestampKey()
        if self.getDoKeySpace():
          line += f" {self.getKeySeparator()} "
        else:
          line += self.getKeySeparator()
        line += str(timestamp)
        final.append(line)
      else:
        final.append(removeEndOfLine(l))
    return "\r\n".join(final) + "\r\n"
   
  def getTimestampFromLogs(self, header_logs : str) -> int:
    """ This function extracts the timestamp from the log files using the configured header format

    Args:
        header_logs (str) : first 16 lines of the log file.
        
    Return:
        timestamp (int) : the timestamp found. If we cannot find the timestamp, it will return -1
    """
    header_logs = header_logs.replace(" ", "")
    check = header_logs.find(self.getArchiveTimestampKey() + self.getKeySeparator())
    if check < 0:
      return check
    start_at = check + len(self.getArchiveTimestampKey() + self.getKeySeparator())
    end_at = header_logs.find("\n", start_at)
    if check < 0:
      return check
    return int(removeEndOfLine(header_logs[start_at:end_at]))
  
  def getDatabaseFilePath(self):
    return DATA_DIRECTORY + self.database["path"]
