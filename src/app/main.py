# Main server handler

from sanic import *
from sanic.response import text
from sanic.response import json as jsonify # rename sanic json response as jsonify to avoid conflicts
from sanic_jinja2 import SanicJinja2
from jinja2 import FileSystemLoader
from datetime import datetime


import webview
import sys
import multiprocessing
import requests, json, os
from gevent.pywsgi import WSGIServer
from funcs import *
from api import *

import ctypes


app = Sanic(__name__)
# Load static files.
app.static("static", os.path.abspath('../static'))

template_dir = "../template"
# Create jinja object
jinja = SanicJinja2(app, pkg_name="main", loader=FileSystemLoader(searchpath=template_dir))

config = json.load(open("config.json", "r"))
VER = config["VER"]
url = config["URL"]
boost = config["Boost"]
if boost == "True":
    boost = ctypes.CDLL("../boost/api.dll")
    get_username_boost = boost.get_username
    
elif boost == "False":
    print("Boost is disabled!")
    
else:
    print("Invalid Boost option in config.json!")
    exit(0)

if os.path.exists("../data/userdata.json"):
    user_config = json.load(open("../data/userdata.json", "r"))
    username = user_config["username"]
    password = user_config["password"]
    user_discrim = user_config["user_discrim"]
    userid = user_config["user_id"]

    response = requests.post(f"{url}/user/{username}/{user_discrim}/authkey", json={
        "auth": password
    })
    json_res = json.loads(response.content.decode())

    user_auth = json_res["authentication"]

@app.route('/')
async def landing(request):
    if not os.path.exists("../data/userdata.json"):
        return redirect("/account")
    else:
        return redirect("/app")

# This is the main url for msging and viewing
@app.route("/app")
async def homepage(request):
    relations_list = get_user_relations(userid, user_auth)
    friends_list = []
    friends_id_list = []
    
    for friend_req_id, status in relations_list["op"].items():
        relations_user_names = get_username(friend_req_id)
        if status != "pending":
            friends_list.append(f"{relations_user_names['name']}#{relations_user_names['discrim']}")
            friends_id_list.append(friend_req_id)
            
    return jinja.render("app.html", request, friends = friends_list, friends_id = friends_id_list)

@app.route("/app/user/<id>")
async def message_viewer(request, id):
    friend_username = get_username(id)
    relations_list = get_user_relations(userid, user_auth)
    friends_list = []
    friends_id_list = []
    
    for friend_req_id, status in relations_list["op"].items():
        relations_user_names = get_username(friend_req_id)
        if status != "pending":
            friends_list.append(f"{relations_user_names['name']}#{relations_user_names['discrim']}")
            friends_id_list.append(friend_req_id)   
    
    dm_msgs = get_dm_msgs(userid, id, user_auth)
    try:
        msgs = reversed(dm_msgs['msgs'])
        for i in dm_msgs["msgs"]:
            if boost == "True":
                msg_username = get_username_boost(i["author"])
            else:
                msg_username = get_username(i["author"])
    except:
        msgs = ""
    try:
        return jinja.render("user_msg.html", request, friend_username = friend_username, friends = friends_list, friends_id = friends_id_list, mass_dm_msgs = msgs, datetime = datetime, msg_username = msg_username)
    except UnboundLocalError:
        return html("Something went wrong while fetching messages if this persists please contact a Client Dev<br/> <a href='/app'>Home</a>")

@app.route("/app/user/friends")
async def friendspage(request):
    relations_list = get_user_relations(userid, user_auth)
    pending_friends_list = []
    pending_friends_id_list = []
    
    friends_list = []
    friends_id_list = []
    
    for friend_req_id, status in relations_list["op"].items():
        relations_user_names = get_username(friend_req_id)
        
        if status == "friend":
            friends_list.append(f"{relations_user_names['name']}#{relations_user_names['discrim']}")
            friends_id_list.append(friend_req_id)
            
        elif bool(friends_list) == 0:
            friends_list == ["None"]
            
        if status == "pending":
            pending_friends_list.append(f"{relations_user_names['name']}#{relations_user_names['discrim']}")
            pending_friends_id_list.append(friend_req_id)      
            
        elif bool(pending_friends_list) == 0:
            pending_friends_list == ["None"]
            
    return jinja.render("friends.html", request, full_friends = friends_list, full_friends_id = friends_id_list, pending_friends = pending_friends_list, pending_friends_id = pending_friends_id_list)

@app.route("/app/user/friends/<id>")
async def accept_friend_request(request, id):
    if boost == "True":
        friend_username = get_username_boost(id)
    else:
        friend_username = get_username(id)
    relations_list = get_user_relations(userid, user_auth)
    friends_list = []
    friends_id_list = []
    
    for friend_req_id, status in relations_list["op"].items():
        relations_user_names = get_username(friend_req_id)
        if status != "pending":
            friends_list.append(f"{relations_user_names['name']}#{relations_user_names['discrim']}")
            friends_id_list.append(friend_req_id)
            
    return jinja.render("friend_req_accept.html", request, friend_req_username = friend_username, friends = friends_list, friends_id = friends_id_list)

@app.route("/app/user/friends/<id>/accept")
async def accept_friend_req(request, id):
    friend_username = get_username(id)
    status = accept_req(user_auth, userid, id)
    return redirect(f"/app/user/{id}")

######## MSGing and stuff #########

@app.route("/get_relations")
async def relations(request):
    usr_relations = get_user_relations(userid, user_auth)
    return jsonify(usr_relations)

@app.route("/account")
async def account(request):
    return  jinja.render("account.html", request)

@app.route("/signup")
async def account_signup(request):
    return jinja.render("signup.html", request)

@app.route("/signup_account")
async def account_create(request):
    usern = request.args.get("username")
    passw = request.args.get("password")

    user_create = create_acc(usern, passw)
    if user_create["op"] == "Created.":
        user_display_details = get_username(user_create["id"])
        userdata = {
            "username": usern,
            "password": passw,
            "user_discrim": user_display_details["discrim"],
            "user_id": user_create["id"]
        }
        json.dump(userdata, open("../data/userdata.json", "w"), indent=4)
        return jinja.render("signedup.html", request, id=user_create["id"], username=usern, discrim=user_display_details["discrim"])
    else:
        return text("invalid")
    
@app.route("/login")
async def account_login(request):
    return jinja.render("login.html", request)

@app.route("/login_account")
async def account_login_to(request):
    usern = request.args.get("username")
    passw = request.args.get("password")
    discrim = request.args.get("discrim")

    user_create = login_acc(usern, passw, discrim)
    # Check if the creds are valid
    if user_create != "Fail":
        userdata = {
            "username": usern,
            "password": passw,
            "user_discrim": discrim,
            "user_id": user_create
        }
        json.dump(userdata, open("../data/userdata.json", "w"), indent=4)
        return jinja.render("loggedin.html", request, username=usern, discrim=discrim)
    else:
        return text("invaild please try again!")


def start_webview():
    webview.create_window(f"Razdor Client v{VER}", "http://localhost:80")
    webview.start()

def start_server():
    app.run(host='0.0.0.0', port=80, access_log=False, debug=False, workers=1) # NOTE: TURN DEBUG ON FOR ERRORS
    
    #http_server = WSGIServer(("localhost", 80), app) # you might need to switch to Uvicorn for this
    #http_server.serve_forever()
    #app.run(port=80)

# Load templates
app.static("/template", template_dir, name='Template')

if __name__ == '__main__':
    multiprocessing.Process(target=start_webview).start()
    start_server()
    sys.exit(0)
