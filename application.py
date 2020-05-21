import os

from datetime import datetime
from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
# configuring session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configuring socketio
app.config["SECRET_KEY"] = 'my secret key'
socketio = SocketIO(app)

chatlist = []  # List to store chatroom names
usernames = []  # List to store current users
messagedict = {}  # Dictionary ot store user, his/her message and time


# First page to load if display name not provided
@app.route("/")
def index():
    # Check if the user was already present
    if "user_name" in session:

        # If user was in a chat before quiting take him to the previous chat
        if "chat_id" in session:
            if len(chatlist) >= session["chat_id"]:
                return redirect(url_for('chatroom', chat_id=session["chat_id"]))

        # If user is logged in take him to the list of chatrooms
        return redirect(url_for('chatroomlist'))
    return render_template("index.html")


# To logout from the site
@app.route("/logout", methods=["GET"])
def logout():

    # Removing username from username list and from session
    try:
        hell = session.pop("user_name")
    except KeyError:
        return render_template("error.html", error_message="Please identify yourself first")
    else:
        usernames.remove(hell)
    return redirect(url_for('index'))


# First page to load if display name provided and to view channel lists
@app.route("/chatrooms", methods=["GET", "POST"])
def chatroomlist():

    # Check if the username submitted from index is valid and if valid add it to username list and to session
    if request.method == "POST":
        user_name = request.form.get("user_name")
        if user_name in usernames:
            return render_template("error.html", error_message="Username already exists.")
        usernames.append(user_name)
        session["user_name"] = user_name
        usernames 

    # If user isn't logged it show and error page
    if request.method=="GET" and "user_name" not in session:
        return render_template("error.html", error_message="Please identify yourself first.")

    return render_template("chatlist.html", chatlist=chatlist, user_name=session["user_name"], usernames=usernames)


# Specific page for a chatroom
@app.route("/chatrooms/<int:chat_id>", methods=["GET", "POST"])
def chatroom(chat_id):

    # Check the validity of chatroom submitted by chatroomlist page
    if request.method == "POST":
        chatroom_name = request.form.get("chatroom_name")
        if chatroom_name in chatlist:
            return render_template("error.html", error_message="The chatroom already exists.")

        # Add chatroom to chatroom list and create an empty list on its name on messages dictionary
        chatlist.append(chatroom_name)
        messagedict[chatroom_name] = []

    # Check if user is logged in and if the requested chatroom exists
    if request.method == "GET":
        if "user_name" not in session:
            return render_template("error.html", error_message="Please identify yourself first.")
        if len(chatlist) < chat_id:
            return render_template("error.html", error_message="Chatroom Doesn't Exist."
                                                               " If you want the same chatroom, go back and create one")

    # Add id of current channel of user to his/her session
    session["chat_id"] = chat_id

    return render_template("chatroom.html", user_name=session["user_name"])


# Socket io to retrieve messages for a chat room
@socketio.on("submit message")
def message(data):
    selection = data["selection"]
    time = datetime.now().strftime("%Y-%m-%d %H:%M")  # Retrieving current datetime

    # Dictionary to save with messages
    response_dict = {"selection": selection, "time": time, "user_name": session["user_name"]}
    messagelist = messagedict[chatlist[session["chat_id"] - 1]]

    # When messages reaches 100 delete start deleting first ones
    if len(messagelist) == 100:
        del messagelist[0]

    # Add message to the messages of the current channel
    messagelist.append(response_dict)
    emit("cast message", {**response_dict, **{"chat_id": str(session["chat_id"])}}, broadcast=True)


# To instantly update channel
@socketio.on("submit channel")
def submit_channel(data):

    # Emit latest chat_id along with what came from a user to all users
    emit("cast channel", {"selection": data["selection"], "chat_id": len(chatlist) + 1}, broadcast=True)


# return messages of a chatroom through Ajax request along with chat_id of session
@app.route("/listmessages", methods=["POST"])
def listmessages():
    return jsonify({**{"message": messagedict[chatlist[session["chat_id"]-1]]}, **{"chat_id": session["chat_id"]}})


if __name__ == "__main__":
    app.run(debug=True)