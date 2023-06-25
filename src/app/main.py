from sanic import *
from sanic.response import text
from sanic_jinja2 import SanicJinja2
from jinja2 import FileSystemLoader

import webview
import sys
import multiprocessing
import requests, json, os
from gevent.pywsgi import WSGIServer
from funcs import *

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
    user_id = user_config["user_id"]
    user_auth = user_config["user_auth"]

@app.route('/')
async def landing(request):
    if not os.path.exists("../data/userdata.json"):
        return redirect("/account")
    else:
        return redirect("/app")

@app.route(f"/app")
async def homepage(request):
    return jinja.render("home.html", request)

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

    status = create_acc(usern, passw)
    if status["op"] == "Created.":
        authkey = requests.post(f"{url}/user/{status['id']}/authkey", json={
            "auth":passw
        })
        usrauthkey = json.loads(authkey.content.decode())
        
        userdata = {
            "username": usern,
            "password": passw,
            "user_id": status["id"],
            "user_auth": usrauthkey["authentication"]
        }
        json.dump(userdata, open("../data/userdata.json", "w"), indent=4)
        return jinja.render("created.html", request, id=status["id"], username=usern)
    else:
        return text("invalid")

    

def start_webview():
    webview.create_window(f"Razdor Client v{VER}", "http://localhost:80")
    webview.start()

def start_server():
    app.run(host='0.0.0.0', port=80, access_log=False, workers=2) # NOTE: TURN DEBUG ON FOR ERRORS
    
    # NOTE: i had to use raw sanic, this should be fine and is actually the preferred way to run sanic.
    #http_server = WSGIServer(("localhost", 80), app) # you might need to switch to Uvicorn for this
    #http_server.serve_forever()
    #app.run(port=80)

# Load templates
app.static("/template", template_dir, name='Template')

if __name__ == '__main__':
    multiprocessing.Process(target=start_webview).start()
    start_server()
    sys.exit(0)
