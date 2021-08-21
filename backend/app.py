import os
from flask import Flask, request, redirect, render_template
from backend import api
from backend.models.orm import db
from backend.models.models import User
from backend.middlewares import auth
from cas import CASClient

app = Flask(__name__, static_url_path="/static")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "sqlite:////tmp/test.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "top_secret_key")
api.init_app(app)
db.init_app(app)
db.create_all(app=app)

cas_client = CASClient(
    version=3,
    service_url='http://localhost:5000/login',
    server_url='https://login.iiit.ac.in/cas/'
)

@app.route("/login")
def login():
    next = request.args.get("next")
    ticket = request.args.get("ticket")

    if not ticket:
        cas_login_url = cas_client.get_login_url()
        app.logger.debug('CAS Login URL: %s', cas_login_url)
        return redirect(cas_login_url)

    email, attributes, pgtiou = cas_client.verify_ticket(ticket)
    if not email:
        return redirect("/login")
    else:
        user = User.query.filter_by(email=email).first()
        if not user:
            # query ldap and create db entry
            ...
        
        auth_token = auth.encode_auth_token(email)
        return render_template("redirect.html",token=auth_token)


    

if __name__ == "__main__":
    app.run(debug=True, port = 5000)