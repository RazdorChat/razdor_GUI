import json, requests, sys

user_data = json.load(open("../data/userdata.json"))

config = json.load(open("../app/config.json", "r"))
VER = config["VER"]
url = config["URL"]

response = requests.post(f"{url}/user/{user_data['user_id']}/authkey", json={
    "auth": user_data["password"]
})
authkey = json.loads(response.content.decode())["authentication"]

print("authkey",":",authkey)