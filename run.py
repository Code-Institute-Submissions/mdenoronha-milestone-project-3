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
    
    if "current_qu_num" not in session:
        session["current_qu_num"] = 0
    
    if "username" not in session:
        return redirect(url_for("index"))
    
    username = session["username"]
    return render_template("qu_home.html", username = username, current_qu_num = session["current_qu_num"])
    
@app.route('/questions/new-game')
def qu_new():
    
    session["current_qu_num"] = 0
    session["score"] = 0
    
    return render_template("qu_new.html")
    
    
@app.route('/questions/<qu_num>', methods=["GET","POST"])
def questions(qu_num):
    
    if "current_qu_num" not in session or "score" not in session:
        return redirect(url_for("index"))
    
    with open("data/riddles.json", "r") as json_data:
        riddles = json.load(json_data)
    """
    Test if url slug is a question number, if not redirect user to the questions 
    homepage
    """
    try:
        qu_num = int(qu_num)
    except ValueError:
        return redirect(url_for("index"))
        
    try:
        riddles[qu_num]
    except IndexError:
        return redirect(url_for("index"))
     
    if request.method == "POST":
        session["current_qu_num"] += 1
        if request.form["answer"] == riddles[qu_num]["answer"]:
            # Run JS function using https://stackoverflow.com/questions/20753969/edit-js-file-from-python
            session["score"] += 1
            
    question = riddles[qu_num]
    
    if session["current_qu_num"] == len(riddles) - 1:
        next_qu = "end"
    else:
        next_qu = session["current_qu_num"]
    
    return render_template("question.html", question = question, next_qu = next_qu)
    
@app.route('/questions/end')
def end():
    
    with open("data/riddles.json", "r") as json_data:
        riddles = json.load(json_data)
    
    if session["current_qu_num"] != len(riddles) - 1:
        return redirect(url_for("index"))
    
    return render_template("questions-end.html", score = session["score"])    
    
        
    

app.run(host=os.getenv('IP', "0.0.0.0"), port=int(os.getenv('PORT', "8080")), debug=True)