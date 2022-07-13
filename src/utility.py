
def removeEndOfLine(param : str) -> str:
  """ Remove <end of line> characters cross platform compatible 

  Args:
      param (str): the string

  Returns:
      str: the string without EOL
  """  
  return param.replace("\n", "").replace("\r", "")

