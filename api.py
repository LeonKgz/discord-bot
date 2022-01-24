tmport requests
import json
import sys

url = f"https://getbible.net/json?passage=Romans%204:1,%2010,%2015&version=synodal"

response = requests.get(url)

try: #try parsing to dict
  dataform = str(response.text).strip("'<>() ").replace('\'', '\"')
#  print(dataform[:-2])
  dataform = dataform[:-2]
  struct = json.loads(dataform)
  print(struct)
except:
  #print(repr(response.text))
  print(sys.exc_info())
