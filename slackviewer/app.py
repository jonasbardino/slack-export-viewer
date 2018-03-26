import flask


app = flask.Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


@app.route("/channel/<name>/")
def channel_name(name):
    messages = flask._app_ctx_stack.channels[name]
    channels = list(flask._app_ctx_stack.channels.keys())
    groups = list(flask._app_ctx_stack.groups.keys())
    dm_users = list(flask._app_ctx_stack.dm_users)
    mpim_users = list(flask._app_ctx_stack.mpim_users)

    return flask.render_template("viewer.html", messages=messages,
                                 name=name.format(name=name),
                                 channels=sorted(channels),
                                 groups=sorted(groups),
                                 # NOTE: dm_users is a list of dicts so no sort!
                                 #dm_users=sorted(dm_users),
                                 dm_users=sorted(dm_users, key=lambda d: d["id"]),
                                 # NOTE: mpim_users is a list of dicts so no sort!
                                 #mpim_users=sorted(mpim_users)
                                 mpim_users=sorted(mpim_users, key=lambda d: d["name"]))


@app.route("/group/<name>/")
def group_name(name):
    messages = flask._app_ctx_stack.groups[name]
    channels = list(flask._app_ctx_stack.channels.keys())
    groups = list(flask._app_ctx_stack.groups.keys())
    dm_users = list(flask._app_ctx_stack.dm_users)
    mpim_users = list(flask._app_ctx_stack.mpim_users)

    return flask.render_template("viewer.html", messages=messages,
                                 name=name.format(name=name),
                                 channels=sorted(channels),
                                 groups=sorted(groups),
                                 # NOTE: dm_users is a list of dicts so no sort!
                                 #dm_users=sorted(dm_users),
                                 dm_users=sorted(dm_users, key=lambda d: d["id"]),
                                 # NOTE: mpim_users is a list of dicts so no sort!
                                 #mpim_users=sorted(mpim_users)
                                 mpim_users=sorted(mpim_users, key=lambda d: d["name"]))


@app.route("/dm/<id>/")
def dm_id(id):
    messages = flask._app_ctx_stack.dms[id]
    channels = list(flask._app_ctx_stack.channels.keys())
    groups = list(flask._app_ctx_stack.groups.keys())
    dm_users = list(flask._app_ctx_stack.dm_users)
    mpim_users = list(flask._app_ctx_stack.mpim_users)

    return flask.render_template("viewer.html", messages=messages,
                                 id=id.format(id=id),
                                 channels=sorted(channels),
                                 groups=sorted(groups),
                                 # NOTE: dm_users is a list of dicts so no sort!
                                 #dm_users=sorted(dm_users),
                                 dm_users=sorted(dm_users, key=lambda d: d["id"]),
                                 # NOTE: mpim_users is a list of dicts so no sort!
                                 #mpim_users=sorted(mpim_users)
                                 mpim_users=sorted(mpim_users, key=lambda d: d["name"]))


@app.route("/mpim/<name>/")
def mpim_name(name):
    messages = flask._app_ctx_stack.mpims[name]
    channels = list(flask._app_ctx_stack.channels.keys())
    groups = list(flask._app_ctx_stack.groups.keys())
    dm_users = list(flask._app_ctx_stack.dm_users)
    mpim_users = list(flask._app_ctx_stack.mpim_users)

    return flask.render_template("viewer.html", messages=messages,
                                 name=name.format(name=name),
                                 channels=sorted(channels),
                                 groups=sorted(groups),
                                 # NOTE: dm_users is a list of dicts so no sort!
                                 #dm_users=sorted(dm_users),
                                 dm_users=sorted(dm_users, key=lambda d: d["id"]),
                                 # NOTE: mpim_users is a list of dicts so no sort!
                                 #mpim_users=sorted(mpim_users)
                                 mpim_users=sorted(mpim_users, key=lambda d: d["name"]))


@app.route("/")
def index():
    channels = list(flask._app_ctx_stack.channels.keys())
    if "general" in channels:
        return channel_name("general")
    else:
        return channel_name(channels[0])
