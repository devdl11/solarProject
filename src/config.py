import json

class Configuration:
  def __init__(self, default_config : str):
    # We pass a valid json string containing the default configuration
    config_obj = json.loads(default_config)
    
    self.default = config_obj
    self.load(config_obj)
    
  def load(self, config: str):
    self.logging = config["logging"]
    self.string = config["string"]
    
  def getJoinSeparator(self) -> str:
    return self.string["joinSep"]
  
  def getKeySeparator(self) -> str:
    return self.string["keySep"]
  
  def getDoKeySpace(self) -> bool:
    return self.string["keySpace"]
    
  def getLoggingPath(self) -> str:
    return self.logging["path"]
  
  def getArchiveLoggingPath(self) -> str:
    return self.logging["archive"]["path"]
  
  def getArchiveFormat(self) -> str:
    return self.logging["archive"]["format"]
   
  def getTimestampFromLogs(self, header_logs : str) -> int:
    """ This function extracts the timestamp from the log files using the configured header format

    Args:
        header_logs (str) : first 16 lines of the log file.
        
    Return:
        timestamp (int) : the timestamp found. If we cannot find the timestamp, it will return -1
    """
    check = header_logs.find()
    pass