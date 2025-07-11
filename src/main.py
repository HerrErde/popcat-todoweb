import shortuuid
import asyncio
import uvicorn
from quart import Quart, jsonify, redirect, render_template, request, session, url_for
from requests_oauthlib import OAuth2Session

import config
from db import DBHandler

app = Quart(__name__)
app.debug = config.DEBUG
app.config["SECRET_KEY"] = config.FLASK_SECRET_KEY

db_handler = DBHandler()


@app.before_serving
async def before_serving():
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
        auto_refresh_url="https://discordapp.com/api/oauth2/token",
        token_updater=token_updater,
    )


@app.errorhandler(404)
async def page_not_found(e):
    return jsonify({"error": "Page not found"}), 404


@app.route("/")
async def home():
    if "oauth2_token" not in session:
        return redirect(url_for("login"))

    discord = make_session(token=session.get("oauth2_token"))
    user = discord.get("https://discordapp.com/api/users/@me").json()
    display_name = user.get("global_name")
    user_id = user.get("id")
    return await render_template(
        "index.html", display_name=display_name, user_id=user_id
    )


@app.route("/login")
async def login():
    scope = request.args.get("scope", "identify")
    discord = make_session(scope=scope.split(" "))
    authorization_url, state = discord.authorization_url(
        "https://discordapp.com/api/oauth2/authorize"
    )
    session["oauth2_state"] = state
    return redirect(authorization_url)


@app.route("/callback")
async def callback():
    if (await request.values).get("error"):
        return jsonify(error=(await request.values)["error"])

    if session.get("oauth2_state") != request.args.get("state"):
        return jsonify(error="State mismatch"), 400

    authorization_code = request.args.get("code")
    if not authorization_code:
        return jsonify(error="Missing authorization code"), 400

    discord = make_session(state=session.get("oauth2_state"))

    try:
        token = discord.fetch_token(
            "https://discordapp.com/api/oauth2/token",
            client_secret=config.OAUTH2_CLIENT_SECRET,
            code=authorization_code,
            include_client_id=True,
        )
    except Exception as e:
        return jsonify(error="Failed to fetch token", details=str(e))

    session["oauth2_token"] = token
    return redirect(url_for("home"))


@app.route("/all", methods=["GET"])
async def all_todos():
    user_id_param = request.args.get("id")

    if config.PUBLIC_ALL and not user_id_param:
        all_todos = await db_handler.list_all()
        return jsonify(items=all_todos)

    if "oauth2_token" not in session:
        return jsonify(error=True, status=401), 401

    discord = make_session(token=session["oauth2_token"])
    user = await asyncio.to_thread(
        lambda: discord.get("https://discordapp.com/api/users/@me").json()
    )
    user_id = str(user.get("id"))

    if not user_id_param or str(user_id_param) != user_id:
        return jsonify(error=True, status=401), 401

    user_todos = await db_handler.list_todo(user_id)
    return jsonify(items=user_todos)


@app.route("/save", methods=["POST"])
async def save_todo():
    if "oauth2_token" not in session:
        return redirect(url_for("login"))

    data = await request.get_json()
    title = data.get("title")
    description = data.get("description")
    user_id_param = data.get("user_id")

    if not title or not description:
        return jsonify(error=False, status=400)

    discord = make_session(token=session["oauth2_token"])
    user = await asyncio.to_thread(
        lambda: discord.get("https://discordapp.com/api/users/@me").json()
    )
    user_id = str(user.get("id"))

    if not user_id_param or str(user_id_param) != user_id:
        return jsonify(error=True, status=401), 401

    id = shortuuid.uuid()
    success = await db_handler.add_todo(user_id, title, description, id)

    if success:
        user_todos = await db_handler.list_todo(user_id)
        return jsonify(items=user_todos), 201
    return jsonify(error=False), 400


@app.route("/delete", methods=["DELETE"])
async def delete_todo():
    if "oauth2_token" not in session:
        return redirect(url_for("login"))

    discord = make_session(token=session["oauth2_token"])
    user = await asyncio.to_thread(
        lambda: discord.get("https://discordapp.com/api/users/@me").json()
    )
    user_id = str(user.get("id"))

    if not user_id_param or str(user_id_param) != user_id:
        return jsonify(error=True, status=401), 401

    data = await request.get_json()
    id = data.get("id")

    if not id:
        return jsonify(error=False, message="ID not provided"), 400

    success = await db_handler.remove_todo(user_id, id)
    return jsonify(error=success), 200 if success else 400


startargs = {"host": config.HOST, "port": config.PORT, "reload": config.DEBUG}


if __name__ == "__main__":
    uvicorn.run("main:app", **startargs)
