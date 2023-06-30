# Main server handler

from sanic import *
from sanic.response import text
from sanic.response import json as jsonify # rename sanic json response as jsonify to avoid conflicts
from sanic_jinja2 import SanicJinja2
from jinja2 import FileSystemLoader

import webview
import sys
import multiprocessing
import requests, json, os
from gevent.pywsgi import WSGIServer
from funcs import *
from api import *

app = Sanic(__name__)
# Load static files.
app.static("static", os.path.abspath('../static'))

template_dir = "../template"
# Create jinja object
jinja = SanicJinja2(app, pkg_name="main", loader=FileSystemLoader(searchpath=template_dir))

config = json.load(open("vars.json", "r"))
VER = config["VER"]
url = config["URL"]

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
    return jinja.render("app.html", request)

@app.route("/friends")
async def friendspage(request):
    return jinja.render("friends.html", request)
    
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
    app.run(host='0.0.0.0', port=80, access_log=False, workers=2) # NOTE: TURN DEBUG ON FOR ERRORS
    
    #http_server = WSGIServer(("localhost", 80), app) # you might need to switch to Uvicorn for this
    #http_server.serve_forever()
    #app.run(port=80)

# Load templates
app.static("/template", template_dir, name='Template')

if __name__ == '__main__':
    multiprocessing.Process(target=start_webview).start()
    start_server()
    sys.exit(0)
