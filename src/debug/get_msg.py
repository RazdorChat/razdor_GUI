import json, requests, sys

user_data = json.load(open("../data/userdata.json"))

config = json.load(open("../app/config.json", "r"))
VER = config["VER"]
url = config["URL"] # https://razdor.chat/api

msgs_to_get_from = sys.argv[1] # get messages from this channel/dm
response = requests.post(f"{url}/user/{user_data['user_id']}/authkey", json={
    "auth": user_data["password"]
})
authkey = json.loads(response.content.decode())["authentication"]

gotten_msgs = requests.get(f"{url}/message/user/{msgs_to_get_from}/messages", json={
    "auth": authkey,
    "requester": user_data["user_id"]
})

print(gotten_msgs.content.decode())