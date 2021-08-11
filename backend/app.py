import os
from flask import Flask
from backend.__init__ import api
from backend.models.orm import db

app = Flask(__name__, static_url_path="/static")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "SQLALCHEMY_DATABASE_URI", r"sqlite:///E:\IIIT\Election_Portal\election-portal\backend\tmp\test.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
api.init_app(app)
db.init_app(app)
db.create_all(app=app)

if __name__ == "__main__":
    app.run(debug=True, port = 5000)