# Here we start

## We setup some constants

CONFIG_PATH = "./config/current.json"
DEFAULT_CONFIG_PATH = "./config/default.json"

## Before doing anything, we load the configurations
import shutil
from src import config

from os import path
from shutil import move
from datetime import datetime
import os
import pytz

## Set our timezone
TIMEZONE = pytz.timezone("europe/bucharest")

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
  now = datetime.now(TIMEZONE)
  
  #If we didn't find the timestamp, we use the default naming
  if timestamp < 0:
    filename = myConfiguration.getArchiveNoTimestampFormat()
    filename = now.strftime(filename)
  else:
    filename = myConfiguration.getArchiveFormat()
    now = datetime.fromtimestamp(timestamp)
    filename = now.strftime(filename)

  filepath = path.join(myConfiguration.getArchiveLoggingPath(), filename)
  
  # We create the archive directory if it doesn't exist
  os.makedirs(path.dirname(filepath), exist_ok=True)
  
  move(previousLogFilePath, filepath)

# We create the logging directory if it doesn't exist
os.makedirs(path.dirname(previousLogFilePath), exist_ok=True)

now = datetime.now(TIMEZONE)

# We create or overwrite the default logfile and add the default header in it
header = myConfiguration.getArchiveFormattedHeader(int(now.timestamp()))
with open(previousLogFilePath, "w") as f:
  f.write(header)
  f.write("\r\n")

# Now we can setup the logging ! 

import logging

logging.basicConfig(
  filename=previousLogFilePath,
  datefmt=myConfiguration.getLoggingInFileDateFormat(),
  format=myConfiguration.getLoggingInFileFormat(),
  level=myConfiguration.getLoggingLevel(),
  style='{'
)

logging.info("Starting Solar System...")

# Now we can initialize the rest 

