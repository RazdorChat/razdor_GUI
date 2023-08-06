# File for the ClientAPI used for communication between Sanic and JS 

import requests, json

config = json.load(open("config.json", "r"))
VER = config["VER"]
url = config["URL"]

def get_user_relations(id : int, authkey : str):
    response = requests.post(f"{url}/user/{id}/relationships", json={
        "auth": authkey
    })
    json_res = json.loads(response.content.decode())
    return json_res

def send_req(authkey : str, id : int, friend_id : int):
    response = requests.post(f"{url}/user/{friend_id}/add", json={
        "auth": authkey,
        "requester": id
    })
    
    json_res = json.loads(response.content.decode())
    if json_res["op"] == "Sent.":
        return json_res["op"]
    elif json_res["op"] == "void":
        return "no_user" # returns if that user the person wants to friend doesnt exist
    else:
        return "ERR" # for all other errors

def accept_req(authkey : str, id : int, friend_id : int):
    response = requests.post(f"{url}/user/accept", json={
        "auth" : authkey,
        "requester" : friend_id,
        "parent" : id
    })    
    json_res = json.loads(response.content.decode())
    return json_res

def get_username(id : int):
    response = requests.get(f"{url}/user/{id}")
    json_res = json.loads(response.content.decode())
    return json_res

def get_dm_msgs(id : int, friends_id : int, authkey : str):
    response = requests.get(f"{url}/message/user/{friends_id}/messages", json={
        "auth": authkey,
        "requester": id
    })
    json_res = json.loads(response.content.decode())
    print(json_res)
    return json_res

