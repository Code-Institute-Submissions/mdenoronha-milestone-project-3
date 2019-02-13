import os
import json
from flask import Flask, redirect, render_template, request, session, url_for, flash
from operator import itemgetter
import random
from datetime import datetime
import ctypes

app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "randomstring123")

    # Put into func, get rid of class
def reset_game_attributes():
    session['score'] = 0
    session['answers'] = []
    session['total_time'] = 0
    session['random_questions'] = random.sample(range(10), 5) 
    session['visited_check'] = []
    session['answer_check'] = []
    session['answers'] = []
    session['start_time'] = None
        
    return


def add_user_to_leaderboard(users):
    
    # convert data to list if not
    if type(users) is dict:
        users = [users]
        # Add user
        # Use Return here?
        # Fix issue with double entries
    for counter, user in enumerate(users):
        if (session["username"] == user["username"]):
            if user["score"] < session["score"]:
                user["score"] = session["score"]
                user["total_time"] = session["total_time"]
            elif user["score"] == session["score"]:
                if user["total_time"] > session["total_time"] or user["total_time"] == None:
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
    
    users = [i for i in users if not i['score'] == None]
    
    users = sorted(users, key=lambda x: (-x['score'], x['total_time']))
    top_users = users[:25]

    for user in top_users:
        if user['total_time'] == None:
            user['total_time'] = 0
        user['total_time'] = turn_seconds_to_string(user["total_time"])
        user['username'] = user['username'].upper()
        
    return top_users
# time module instead of this function
def turn_seconds_to_string(secs):
    # https://stackoverflow.com/questions/775049/how-do-i-convert-seconds-to-hours-minutes-and-seconds
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    secs_string = "%02dm %02ds" % (m, s)
    
    return secs_string
    
def add_answer(current_random_question, submitted_answer):
    temp_answers = {}
    temp_answers["random_qu_num"] = current_random_question
    temp_answers["answer"] = submitted_answer
    
    return temp_answers

@app.route("/", methods=["POST", "GET"])
def index():
    
    users = json.load(open('data/users.json'))
    
    if request.method == "POST":
        if 'login' in request.form:
            for counter, user in enumerate(users):
                if user["username"].upper() == request.form["login"].upper():
                        session["username"] = request.form["login"].upper()
                        break
                else:
                    if counter == len(users) - 1:
                        flash("No User By That Name Exists", category='not-user')
        else:   
            for counter, user in enumerate(users):
                if user["username"].upper() == request.form["register"].upper():
                    # https://www.youtube.com/watch?v=DFCKWhoiHZ4
                    # Change this into a list of strings, and input into html (remove HTML from message)
                    messages = ["That username is taken, please try another.",
                                "Is This You? ",
                                "Log in"]
                                
                    for message in messages:
                        flash(message, category='user')

                    return render_template("index.html")
                else:
                    if counter == len(users) - 1:
                        session["username"] = request.form["register"].upper() 
                        session["score"] = None
                        session["total_time"] = None
                        users = json.load(open('data/users.json'))
                        add_user_to_leaderboard(users)
        
    if "username" in session:
        return redirect(url_for("qu_home"))
    
    title = "Riddles Game - Join Up"
    return render_template("index.html", title = title)
    
@app.route('/questions/home')
def qu_home():
    if "current_qu_num" not in session:
        session["current_qu_num"] = None
    
    if "username" not in session:
        return redirect(url_for("index"))
        
    with open("data/riddles.json", "r") as json_data:
        riddles = json.load(json_data)
        
    
    title = "Riddles Game - Questions Home"
    return render_template("qu_home.html", username = session["username"], current_qu_num = session["current_qu_num"], title = title)
    
@app.route('/questions/new-game')
def qu_new():

    session["current_qu_num"] = 1
    reset_game_attributes()
    
    title = "Riddles Game - New Game"
    
    return render_template("qu_new.html", username = session["username"], title = title)
    
@app.route('/questions/<qu_num>', methods=["GET","POST"])
def questions(qu_num):
    
    # If POST is repeated, can do this better?
    """
    Test if url slug is a question number, if not redirect user to the questions 
    homepage
    """
    try:
        qu_num = int(qu_num)
    except ValueError:
        return redirect(url_for("index"))
        
    try: 
        session["random_questions"]
    except KeyError:
        return redirect(url_for("index"))
    
    random_questions = session["random_questions"]
    
    try:
        random_questions[int(qu_num) - 1]
    except IndexError:
        return redirect(url_for("index"))
        
    if "current_qu_num" not in session or "score" not in session:
        return redirect(url_for("index"))
        
    
    # Start at question 1 not question 0
    
    if request.method == "POST":
        # Mark questions as answered
        session["answer_check"].append(int(qu_num))
        
    if int(qu_num) not in session["visited_check"]:
        session["visited_check"].append(int(qu_num))
        session["start_time"] = datetime.now()

    
    with open("data/riddles.json", "r") as json_data:
        riddles = json.load(json_data)
        
    
    
    """
    Redirect user if they try to access a different question
    """
    if int(qu_num) != int(session["current_qu_num"]):
        return redirect(url_for("index"))

    current_random_question = random_questions[int(qu_num) - 1]
    
    correct = None
    correct_answer = None

    if request.method == "POST":
        
        session["current_qu_num"] += 1
        stop_time = datetime.now()
        start_time = session["start_time"]
        
        if session["total_time"] == None:
            session["total_time"] = 0
        session["total_time"] += (stop_time - start_time).total_seconds()
        
        session["answers"].append(add_answer(current_random_question, request.form["answer"].upper()))
        
        for answer in riddles[current_random_question - 1]["answer"]:
            if request.form["answer"].upper() == answer.upper():
                # Run JS function using https://stackoverflow.com/questions/20753969/edit-js-file-from-python
                if session["score"] == None:
                    session["score"] = 0
                session["score"] += 1
                
        answers = riddles[current_random_question - 1]["answer"]
        if not isinstance(answers, list):
            if request.form["answer"].upper() == answers.upper():
                correct = True
                correct_answer = answers
            else:
                correct = False
                correct_answer = answers
        else:
            for counter, answer in enumerate(answers):
                if request.form["answer"].upper() == answer.upper():
                    correct = True
                    correct_answer = answer
                    break
                else:
                    if counter == len(riddles[current_random_question - 1]["answer"]) - 1:
                       correct = False
                       correct_answer = answer
            
    question = riddles[current_random_question - 1]
    
    if session["current_qu_num"] == 6:
        next_qu = "end"
    else:
        next_qu = session["current_qu_num"]
        
    
    title = "Riddles Game - Question %d" % (qu_num)
    
    return render_template("question.html", qu_num = qu_num, question = question, next_qu = next_qu, correct = correct, correct_answer = correct_answer, title = title)
    
@app.route('/questions/end')
def end():

    if session["current_qu_num"] != 6:
        return redirect(url_for("index"))
        
    users = json.load(open('data/users.json'))
    add_user_to_leaderboard(users)
    top_users = render_leaderboard(users)
            
    total_time_str = turn_seconds_to_string(session["total_time"])
    
    title = "Riddles Game - End"
    
    return render_template("questions-end.html", top_users = top_users, total_time_str = total_time_str, title = title)  


@app.route("/logout")
def logout():
    
    try:
        del session["username"]
    except KeyError:
        return redirect(url_for("index"))
        
    session["current_qu_num"] = None
    reset_game_attributes()
    return redirect(url_for("index"))
    
           
@app.route("/leaderboard")
def leaderboard():
    
    users = json.load(open('data/users.json'))
    top_users = render_leaderboard(users)
    
    title = "Riddles Game - Leaderboard"
    
    return render_template("leaderboard.html", top_users = top_users, title = title)
    
# Make debug false
# If name for test_riddle
if __name__ == "__main__":
    app.run(host=os.getenv('IP', "0.0.0.0"), port=int(os.getenv('PORT', "8080")), debug=True)