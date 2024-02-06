from flask import Blueprint, render_template
import vrp

views = Blueprint(__name__, "views")

@views.route("/")
def home():
    return render_template("index.html", cost = vrp.df['cost'][0], distance = vrp.df['distance'][0], duration = vrp.df['duration'][0])