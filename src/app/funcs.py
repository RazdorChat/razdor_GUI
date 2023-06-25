# This file is for API related functions

import requests, json

config = json.load(open("vars.json", "r"))
VER = config["VER"]
url = config["URL"]

def create_acc(username, password):
    response = requests.post(f"{url}/user/create", json={
        "password" :password,
        "username": username
    })
    json_res = json.loads(response.content.decode())
    return json_res