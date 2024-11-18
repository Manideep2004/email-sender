from flask import Flask
from redis import Redis

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "data"
app.config["SECRET_KEY"] = "some-secure-secret"

app.redis = Redis(host="localhost", port=6379, decode_responses=True)

from app import routes
