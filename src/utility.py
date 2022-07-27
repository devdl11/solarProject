
def removeEndOfLine(param : str) -> str:
  """ Remove <end of line> characters cross platform compatible 

  Args:
      param (str): the string

  Returns:
      str: the string without EOL
  """  
  return param.replace("\n", "").replace("\r", "")

def digitalWriteParser(value: int):
    return 0 if value == 0 else 1
