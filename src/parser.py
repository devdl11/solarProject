import uuid

configParserKeys = {
  "{uuid}" : uuid.uuid4(),
}

def configParser(param: str, sep: str) -> str:
  global configParserKeys
  keys = param.split(sep)
  final_keys = list()
  for k in keys:
    r = configParserKeys.get(k, None)
    if r is not None:
      final_keys.append(r())
    else:
      final_keys.append(k)
  return sep.join(final_keys)
