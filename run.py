import os
import json
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "randomstring123")

@app.route("/", methods=["POST", "GET"])
def index():
    
    if request.method == "POST":
        session["username"] = request.form["username"]
        
    if "username" in session:
        return redirect(url_for("qu_home"))
    
    
    return render_template("index.html")
    
    
@app.route('/questions/home')
def qu_home():
    
    if "score" not in session:
        current_qu_num = 0
    
    if "username" not in session:
        return redirect(url_for("index"))
    
    username = session["username"]
    return render_template("qu_home.html", username = username, current_qu_num = current_qu_num)

app.run(host=os.getenv('IP', "0.0.0.0"), port=int(os.getenv('PORT', "8080")), debug=True)