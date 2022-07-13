# Here we start

## We setup some constants

CONFIG_PATH = "./config/current.json"
DEFAULT_CONFIG_PATH = "./config/default.json"

## Before doing anything, we load the configurations
from src import config

from os import path
from shutil import move

# We suppose that the default configuration file exist no matter what. Otherwise, python will print a nice error ;-)
with open(DEFAULT_CONFIG_PATH, "r") as f:
  defaultConfigurations = f.read()
  
myConfiguration = config.Configuration(default_config=defaultConfigurations)

# If the custom configuration file doesn't exist, we create it with the defaults values, else we load it
if not path.isfile(CONFIG_PATH):
  with open(CONFIG_PATH, "w") as f:
    f.write(defaultConfigurations)
else:
  with open(CONFIG_PATH, "r") as f:
    myConfiguration.load(f.read())

## Now we setup the logging system
previousLogFilePath = myConfiguration.getLoggingPath()

# If there is a previous log file, we need to copy it into the archive directory to not overwrite it with the new logs
if path.isfile(previousLogFilePath):
  with open(previousLogFilePath, "r") as f:
    # Iterate through the file's lines until we get 10 lines
    header = "".join([next(f) for i in range(10)])
    timestamp = myConfiguration.getTimestampFromLogs(header)
    
    