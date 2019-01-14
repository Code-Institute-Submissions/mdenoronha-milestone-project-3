import os
import json
from flask import Flask, redirect, render_template, request, session, url_for, flash, Markup
from operator import itemgetter
import random
from datetime import datetime
import ctypes

app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "randomstring123")

# Have all variables needed in a class?
user_answers = []

def add_user_to_leaderboard(users):
    
    # convert data to list if not
    if type(users) is dict:
        users = [users]
        # Add user
        # Use Return here?
    for counter, user in enumerate(users):
        if (user["username"] == session["username"]):
            if user["score"] < session["score"]:
                user["score"] = session["score"]
            if user["total_time"] == None or user["total_time"] > session["total_time"]:
                user["total_time"] = session["total_time"]
        else:
            if counter == len(users) - 1:
                new_user = {}
                new_user["username"] = session["username"]
                new_user["score"] = session["score"]
                new_user["total_time"] = session["total_time"]
                users.append(new_user)

    # write list to file
    with open('data/users.json', 'w+') as overwrite:
        json.dump(users, overwrite)
    
    # Better way to do this than loading it again? 
    users = json.load(open('data/users.json'))
    
    return users
    
def render_leaderboard(users):
    
    users = sorted(users, key=lambda x: (-x['score'], x['total_time']))
    top_users = users[:25]
    
    
    for user in users:
        if user['total_time'] == None:
            user['total_time'] = 0
        user['total_time'] = turn_seconds_to_string(user["total_time"])
        user['username'] = user['username'].upper()
        
    return top_users
    
def turn_seconds_to_string(secs):
    # https://stackoverflow.com/questions/775049/how-do-i-convert-seconds-to-hours-minutes-and-seconds
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    secs_string = "%02d mins %02d secs" % (m, s)
    
    return secs_string

@app.route("/", methods=["POST", "GET"])
def index():
    
    users = json.load(open('data/users.json'))

    
    if request.method == "POST":
        if 'login' in request.form:
            for counter, user in enumerate(users):
                if user["username"].upper() == request.form["login"].upper():
                        session["username"] = request.form["login"] 
                else:
                    if counter == len(users) - 1:
                        flash("No User By That Name Exists", category='not-user')
        else:   
            for counter, user in enumerate(users):
                if user["username"].upper() == request.form["register"].upper():
                    # https://www.youtube.com/watch?v=DFCKWhoiHZ4
                    message = Markup("That username is taken, please try another.<br><strong>Already a Player? <span class=\"linked-text\" onclick=\"showLogin()\">Log in</span></strong>")
                    flash(message, category='user')
                    return render_template("index.html")
                else:
                    if counter == len(users) - 1:
                        session["username"] = request.form["register"] 
                        session["score"] = None
                        session["total_time"] = None
                        users = json.load(open('data/users.json'))
                        add_user_to_leaderboard(users)
        
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
    
    return render_template("qu_home.html", username = session["username"], current_qu_num = session["current_qu_num"])
    
@app.route('/questions/new-game')
def qu_new():
    
    session["current_qu_num"] = 1 
    session["score"] = 0
    session["answers"] = []
    session["total_time"] = 0
    session["random_questions"] = random.sample(range(10), 5)
    session["timer"] = 0
    session["visited_check"] = []
    session["answer_check"] = []
    session["answers"] = {}
    global answer_check
    answer_check = []
    return render_template("qu_new.html", username = session["username"])
    
@app.route('/questions/<qu_num>', methods=["GET","POST"])
def questions(qu_num):
    # If POST is repeated, can do this better?
    
    # Start at question 1 not question 0
    
    if request.method == "POST":
        # Mark questions as answered
        session["answer_check"].append(int(qu_num))
        
    if int(qu_num) not in session["visited_check"]:
        session["visited_check"].append(int(qu_num))
        session["start_time"] = datetime.now()
    
    random_questions = session["random_questions"]
    
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
        random_questions[int(qu_num)]
    except IndexError:
        return redirect(url_for("index"))
        
    if "current_qu_num" not in session or "score" not in session:
        return redirect(url_for("index"))
        
    
    """
    Redirect user if they try to access a different question
    """
    if int(qu_num) != int(session["current_qu_num"]):
        return redirect(url_for("index"))

    current_random_question = random_questions[int(qu_num)]
    
    if request.method == "POST":
        
        session["current_qu_num"] += 1
        stop_time = datetime.now()
        start_time = session["start_time"]
        print(stop_time - start_time)

        temp_answers = {}
        temp_answers["qu_num"] = current_random_question
        temp_answers["answer"] = request.form["answer"].upper()
        if session["total_time"] == None:
            session["total_time"] = 0
        session["total_time"] += (stop_time - start_time).total_seconds()
        
        # Does this work?
        # session["answers"].append(temp_answers)
        
        global user_answers
        # Add check to see if qu_num has an answer, if so don't append
        user_answers.append(temp_answers)
        
        
        session["answers"] = user_answers
        if request.form["answer"].upper() == riddles[current_random_question]["answer"].upper():
            # Run JS function using https://stackoverflow.com/questions/20753969/edit-js-file-from-python
            if session["score"] == None:
                session["score"] = 0
            session["score"] += 1
            
    question = riddles[current_random_question]
    
    if session["current_qu_num"] == 5:
        next_qu = "end"
    else:
        next_qu = session["current_qu_num"]
    
    return render_template("question.html", qu_num = qu_num, question = question, next_qu = next_qu, correct_answer = riddles[current_random_question]["answer"].upper())
    
@app.route('/questions/end')
def end():

    with open("data/riddles.json", "r") as json_data:
        riddles = json.load(json_data)

    if session["current_qu_num"] != 5:
        return redirect(url_for("index"))
        
    users = json.load(open('data/users.json'))
    add_user_to_leaderboard(users)
    top_users = render_leaderboard(users)
            
    total_time_str = turn_seconds_to_string(session["total_time"])
    
    return render_template("questions-end.html", top_users = top_users, total_time_str = total_time_str)  
    
@app.route("/leaderboard")
def leaderboard():
    
    users = json.load(open('data/users.json'))
    top_users = render_leaderboard(users)
    
    return render_template("leaderboard.html", top_users = top_users)
    
# Make debug false
app.run(host=os.getenv('IP', "0.0.0.0"), port=int(os.getenv('PORT', "8080")), debug=True)