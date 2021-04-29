from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
from mcstatus import MinecraftServer

from cloudipsp import Api, Checkout

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///server.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    on = db.Column(db.Boolean, default=True)
    info = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return self.title


@app.route("/")
def home():
    items = Item.query.order_by(Item.price).all()
    return render_template("home.html", data=items)


@app.route("/information")
def information():
    return render_template("information.html")


@app.route("/online")
def online():
    return render_template("online.html")


@app.route('/server-pinger')
def server_data():
    server_ip = "mc.hypixel.net"
    server = MinecraftServer.lookup("{}:25565".format(server_ip))

    players = server.status().players.online

    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return jsonify(ip=server_ip, time=time, value=players)


@app.route("/donate", methods=["POST", "GET"])
def donate():
    if request.method == "POST":
        title = request.form["title"]
        price = request.form["price"]
        info = request.form["info"]

        item = Item(title=title, price=price, info=info)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect("/")
        except:
            return "Ошибка. Проверьте правильность заполнения полей."
    else:
        return render_template("donate.html")


@app.route("/buy/<int:id>")
def buy(id):
    item = Item.query.get(id)

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "RUB",
        "amount": str(item.price) + "00"
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


if __name__ == "__main__":
    app.run()
