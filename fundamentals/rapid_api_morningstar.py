from utils import my_constants as mconst
import requests
import json

# url = f"{mconst.RAPID_API_URL}/convenient/fundamentals/quarterly/as-reported"

url = f"{mconst.RAPID_API_URL}/convenient/keyratios"

querystring = {"Mic":"XNSE","Ticker":"INFY"}

headers = {
    'x-rapidapi-host': "morningstar1.p.rapidapi.com",
    'x-rapidapi-key': "ab87ed58b2msh78f8c53185c415bp161652jsnff19e78ce6eb",
    'accept': "string"
    }

response = requests.request("GET", url, headers=headers, params=querystring)
json_res = json.loads(response.text)
with open("keyratios.json", "w") as files:
    files.write(json.dumps(json_res, indent=4, sort_keys=True))

print(response.text)