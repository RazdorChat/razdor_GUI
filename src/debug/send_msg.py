import json, requests, sys

user_data = json.load(open("../data/userdata.json"))

config = json.load(open("../app/config.json", "r"))
VER = config["VER"]
url = config["URL"]

sendto = sys.argv[1] # send to this user id
content = sys.argv[2] # message content

response = requests.post(f"{url}/user/{user_data['user_id']}/authkey", json={
    "auth": user_data["password"]
})
authkey = json.loads(response.content.decode())["authentication"]

message_to_send = requests.post(f"{url}/message/user/{sendto}/create", json={
    "auth": authkey,
    "requester": user_data["user_id"],
    "content": content
})

print(message_to_send.content.decode())
