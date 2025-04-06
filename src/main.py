import shortuuid
import uvicorn
from quart import Quart, jsonify, redirect, render_template, request, session, url_for
from requests_oauthlib import OAuth2Session

import config
from db import DBHandler

app = Quart(__name__)
app.debug = True
app.config["SECRET_KEY"] = config.FLASK_SECRET_KEY

db_handler = DBHandler()


@app.before_serving
async def before_serving():
    # Initialize the DB handler before the app starts
    await db_handler.initialize()


def token_updater(token):
    session["oauth2_token"] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=config.OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=config.OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            "client_id": config.OAUTH2_CLIENT_ID,
            "client_secret": config.OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=config.TOKEN_URL,
        token_updater=token_updater,
    )


@app.before_request
def disable_route():
    if not config.PUBLIC_ALL:
        # Check if the request is for a route you want to disable
        if request.path in ["/all"]:
            return jsonify({"error": "Page not found"}), 404


@app.errorhandler(404)
async def page_not_found(e):
    return jsonify({"error": "Page not found"}), 404


@app.route("/")
async def home():
    if "oauth2_token" not in session:
        return redirect(url_for("login"))

    discord = make_session(token=session.get("oauth2_token"))
    user = discord.get(config.API_BASE_URL + "/users/@me").json()
    display_name = user.get("global_name")
    return await render_template("index.html", display_name=display_name)


@app.route("/login")
async def login():
    scope = request.args.get("scope", "identify")
    discord = make_session(scope=scope.split(" "))
    authorization_url, state = discord.authorization_url(config.AUTHORIZATION_BASE_URL)
    session["oauth2_state"] = state
    return redirect(authorization_url)


@app.route("/callback")
async def callback():
    if (await request.values).get("error"):
        return jsonify(error=(await request.values)["error"])

    # No need to await request.args
    if session.get("oauth2_state") != request.args.get("state"):
        return jsonify(error="State mismatch"), 400

    authorization_code = request.args.get("code")
    if not authorization_code:
        return jsonify(error="Missing authorization code"), 400

    discord = make_session(state=session.get("oauth2_state"))

    try:
        token = discord.fetch_token(
            config.TOKEN_URL,
            client_secret=config.OAUTH2_CLIENT_SECRET,
            code=authorization_code,
            include_client_id=True,
        )
    except Exception as e:
        return jsonify(error="Failed to fetch token", details=str(e))

    session["oauth2_token"] = token
    return redirect(url_for("home"))


@app.route("/all")
async def all_todo():
    todos = await db_handler.list_all()
    return jsonify(todos)


@app.route("/todos", methods=["GET"])
async def todos_route():
    if "oauth2_token" not in session:
        return redirect(url_for("login"))

    discord = make_session(token=session.get("oauth2_token"))
    user = discord.get(config.API_BASE_URL + "/users/@me").json()
    user_id = user.get("id")

    user_todos = await db_handler.list_todo(user_id)
    return jsonify(items=user_todos)


@app.route("/todo", methods=["POST"])
async def todo_route():
    if "oauth2_token" not in session:
        return redirect(url_for("login"))

    discord = make_session(token=session.get("oauth2_token"))
    user = discord.get(config.API_BASE_URL + "/users/@me").json()
    user_id = user.get("id")

    title = (await request.json).get("title")
    description = (await request.json).get("description")
    id = shortuuid.uuid()

    # Generate a random integer ID and use it directly
    success = await db_handler.add_todo(user_id, title, description, id)

    if success:
        user_todos = await db_handler.list_todo(user_id)
        return jsonify(items=user_todos), 201
    return jsonify(success=success), 400


@app.route("/delete", methods=["DELETE"])
async def delete_todo():
    if "oauth2_token" not in session:
        return redirect(url_for("login"))

    discord = make_session(token=session.get("oauth2_token"))
    user = discord.get(config.API_BASE_URL + "/users/@me").json()
    user_id = user.get("id")

    # Use a safe way to extract the ID
    id = (await request.json).get("id")
    if not id:
        return jsonify(success=False, message="ID not provided"), 400

    print(id)  # For debugging; you can remove it in production

    success = await db_handler.remove_todo(user_id, id)
    return jsonify(success=success), 200 if success else 400


startargs = {"host": config.HOST, "port": config.PORT, "reload": config.DEBUG}


if __name__ == "__main__":
    uvicorn.run("main:app", **startargs)
