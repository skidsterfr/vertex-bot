"""
Render's free web-service tier needs something listening on an HTTP port,
and will spin the service down after ~15 minutes without a request.
This tiny Flask server gives it something to respond with, and gives
UptimeRobot (or similar) something to ping to keep Vertex awake.
"""
from flask import Flask
from threading import Thread

app = Flask("")


@app.route("/")
def home():
    return "Vertex is alive."


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()
