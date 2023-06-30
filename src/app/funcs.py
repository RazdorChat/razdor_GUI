# This file is for user/account related functions

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


def login_acc(username ,password, discrim):
    response = requests.post(f"{url}/user/{username}/{discrim}/authkey", json={
        "auth":password
    })
    json_res = json.loads(response.content.decode())
    if json_res["op"] == "Created.":
        return json_res["id"]
    else:
        return "Fail"
