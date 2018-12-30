import os
import json
from flask import Flask, redirect, render_template, request, session, url_for
from operator import itemgetter

app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "randomstring123")

user_answers = []

def add_user_to_leaderboard(users):
    
    # convert data to list if not
    if type(users) is dict:
        users = [users]
        # Add user
    for counter, user in enumerate(users):
        if (user["username"] == session["username"]):
            if user["score"] < int(session["score"]):
                user["score"] = int(session["score"])
        else:
            if counter == len(users) - 1:
                new_user = {}
                new_user["username"] = session["username"]
                new_user["score"] = int(session["score"])
                users.append(new_user)
                

    # write list to file
    with open('data/users.json', 'w+') as overwrite:
        json.dump(users, overwrite)
    
    # Better way to do this than loading it again? 
    users = json.load(open('data/users.json'))
    
    return users

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
        
    with open("data/riddles.json", "r") as json_data:
        riddles = json.load(json_data)
    
    username = session["username"]
    return render_template("qu_home.html", riddles_length = len(riddles), username = username, current_qu_num = session["current_qu_num"])
    
@app.route('/questions/new-game')
def qu_new():
    
    session["current_qu_num"] = 0
    session["score"] = 0
    
    return render_template("qu_new.html")
    
    
@app.route('/questions/<qu_num>', methods=["GET","POST"])
def questions(qu_num):
    
    session["qu_num"] = []
    
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
        
    if "current_qu_num" not in session or "score" not in session:
        return redirect(url_for("index"))
        
    
    """
    Take user to the question they're currently on
    """
    
    if "answer" not in session["qu_num"] and int(qu_num) != int(session["current_qu_num"]):
        return redirect(url_for("questions", qu_num = session["current_qu_num"]))

     
    if request.method == "POST":
        session["current_qu_num"] += 1
        
        temp_answers = {}
        temp_answers["qu_num"] = qu_num
        temp_answers["answer"] = request.form["answer"].upper()
        global user_answers
        user_answers.append(temp_answers)
        
        session["answers"] = user_answers
        if request.form["answer"].upper() == riddles[qu_num]["answer"].upper():
            # Run JS function using https://stackoverflow.com/questions/20753969/edit-js-file-from-python
            session["score"] += 1
            
    question = riddles[qu_num]
    
    if session["current_qu_num"] == len(riddles) - 1:
        next_qu = "end"
    else:
        next_qu = session["current_qu_num"]
    
    return render_template("question.html", qu_num = qu_num, question = question, next_qu = next_qu)
    
@app.route('/questions/end')
def end():
    
    with open("data/riddles.json", "r") as json_data:
        riddles = json.load(json_data)

    if session["current_qu_num"] != len(riddles) - 1:
        return redirect(url_for("index"))
        
    users = json.load(open('data/users.json'))
    add_user_to_leaderboard(users)
    
    users = sorted(users, key=itemgetter("score"), reverse=True) 
        
    return render_template("questions-end.html", users = users)    
    

app.run(host=os.getenv('IP', "0.0.0.0"), port=int(os.getenv('PORT', "8080")), debug=True)