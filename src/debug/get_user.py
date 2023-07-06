# get username and discrim from user id

import requests, json, sys

config = json.load(open("../app/config.json", "r"))
VER = config["VER"]
url = config["URL"]

id = sys.argv[1]
    
response = requests.get(f"{url}/user/{id}")
json_res = json.loads(response.content.decode())

print(json_res)