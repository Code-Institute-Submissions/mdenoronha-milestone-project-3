import os
import json
from flask import Flask, redirect, render_template, request, session, url_for, flash
from operator import itemgetter
import random
from datetime import datetime
import ctypes

app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "randomstring123")

# Reset all game attributes to reset Riddle Game
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

"""
Once game is complete, user's score and total time is added to leaderboard
This function also adds a new user to user.json when they first register
"""
def add_user_to_leaderboard(users):
    # convert data to list if not
    if type(users) is dict:
        users = [users]
    # Checks if user's score & total time is better than their previous attempt
    for counter, user in enumerate(users):
        if user["username"] == session["username"]:
            # if user["score"] < session["score"]:
            #     user["score"] = session["score"]
            #     user["total_time"] = session["total_time"]
            # elif user["score"] == session["score"]:
            #     if user["total_time"] > session["total_time"] or user["total_time"] == None:
            #         user["total_time"] = session["total_time"]
            break
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
    users = json.load(open('data/users.json'))
    
    return users
    
# Interates through user.json to create leaderboard 
def render_leaderboard(users):
    
    users = [i for i in users if not i['score'] == None]
    # Sorts users by score and total time, selecting the top 25
    users = sorted(users, key=lambda x: (-x['score'], x['total_time']))
    top_users = users[:25]

    for user in top_users:
        if user['total_time'] == None:
            user['total_time'] = 0
        user['total_time'] = turn_seconds_to_string(user["total_time"])
        user['username'] = user['username'].upper()
        
    return top_users

# Turns total time to a string of minutes and seconds
def turn_seconds_to_string(secs):
    # https://stackoverflow.com/questions/775049/how-do-i-convert-seconds-to-hours-minutes-and-seconds
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    secs_string = "%02dm %02ds" % (m, s)
    
    return secs_string

# Method that adds answer to empty dict
def add_answer(current_random_question, submitted_answer):
    temp_answers = {}
    temp_answers["random_qu_num"] = current_random_question
    temp_answers["answer"] = submitted_answer
    
    return temp_answers

"""
Homepage where users can register and login
"""
@app.route("/", methods=["POST", "GET"])
def index():
    # Loads all users from user.json
    users = json.load(open('data/users.json'))
    
    """
    If user has entered a name into the login form, it is checked to see if a user 
    by that name exists. If not, an error message is displayed.
    """
    if request.method == "POST":
        if 'login' in request.form:
            for counter, user in enumerate(users):
                if user["username"].upper() == request.form["login"].upper():
                        # If user exists, username is attached to session and user can play game
                        session["username"] = request.form["login"].upper()
                        break
                else:
                    if counter == len(users) - 1:
                        flash("No User By That Name Exists", category='not-user')
        # If user has entered a name into the register form, it is checked to ensure
        # no user by that name already exists
        else:   
            for counter, user in enumerate(users):
                # If username is already taken, an error message is displayed
                if user["username"].upper() == request.form["register"].upper():
                    messages = ["That username is taken, please try another.",
                                "Is This You? ",
                                "Log in"]
                                
                    for message in messages:
                        flash(message, category='user')

                    return render_template("index.html")
                # If not, user is created, given basic game attributes and added to user.json
                else:
                    if counter == len(users) - 1:
                        session["username"] = request.form["register"].upper() 
                        session["score"] = None
                        session["total_time"] = None
                        users = json.load(open('data/users.json'))
                        add_user_to_leaderboard(users)
    # If user has logged in or registered, they are redirected to Questions Home
    if "username" in session:
        return redirect(url_for("qu_home"))
    
    title = "Riddles Game - Join Up"
    return render_template("index.html", title = title)
"""
Questions home which allows users to create a new game, continue a game or see the leaderboard
"""
@app.route('/questions/home')
def qu_home():
    # If user has not started a game, current_qu_num is set to None
    if "current_qu_num" not in session:
        session["current_qu_num"] = None
        
    # If user has not logged in or registered, they are redirected to Home
    if "username" not in session:
        return redirect(url_for("index"))
        
    with open("data/riddles.json", "r") as json_data:
        riddles = json.load(json_data)
        
    
    title = "Riddles Game - Questions Home"
    return render_template("qu_home.html", username = session["username"], current_qu_num = session["current_qu_num"], title = title)

"""
A new game page which explains what will happen during the game. Essential game attributes
to start the game are set
"""
@app.route('/questions/new-game')
def qu_new():
    
    # Starts user at question 1
    session["current_qu_num"] = 1
    # Resets game attributes to remove previous game progress
    reset_game_attributes()
    
    title = "Riddles Game - New Game"
    
    return render_template("qu_new.html", username = session["username"], title = title)
 
"""
Question pages where users enter their answers to displayed riddles
"""
@app.route('/questions/<qu_num>', methods=["GET","POST"])
def questions(qu_num):
    
    """
    A number of checks to ensure a user is not able to navigate to a questions page
    out of sequence of the game steps. Doing so would result in an error as essential 
    game attributes would not be set. If this occurs, the user is redirected to an 
    appropriate page.
    """
    
    # Checks to see if user has visited a qu_num that is an integer, if not redirects user to home
    try:
        qu_num = int(qu_num)
    except ValueError:
        return redirect(url_for("index"))
    
    # Checks to see if riddles have been generated necessary for game to play, if not redirects user to home
    try: 
        session["random_questions"]
    except KeyError:
        return redirect(url_for("index"))
    
    random_questions = session["random_questions"]
    
    # Checks to see if qu_num is within the random questions list, if not redirects user to home
    try:
        random_questions[int(qu_num) - 1]
    except IndexError:
        return redirect(url_for("index"))
    
    # Checks to see if essential game attributes have been set, if not redirects user to home
    if "current_qu_num" not in session or "score" not in session:
        return redirect(url_for("index"))
    
    # Checks to see if user is on the correct question number, if not redirects user to home
    if int(qu_num) != int(session["current_qu_num"]):
        return redirect(url_for("index"))

    
    # If the user has not visited this question before, the question number is added to visited questions
    if int(qu_num) not in session["visited_check"]:
        session["visited_check"].append(int(qu_num))
        # Starts a timer from a user's first visit of this question
        session["start_time"] = datetime.now()

    # If user answers the question, marks specific question as answered
    if request.method == "POST":
        session["answer_check"].append(int(qu_num))
        
    with open("data/riddles.json", "r") as json_data:
        riddles = json.load(json_data)
    
    # Attributes necessary to display on question.html
    current_random_question = random_questions[int(qu_num) - 1]
    correct = None
    correct_answer = None
    
    # User answers the riddle
    if request.method == "POST":
        
        # User is marked as currently on the next riddle
        session["current_qu_num"] += 1
        
        """
        The time is recorded when the user answered. This minus the time the question
        was started equates to how long it took the user to answer the question. This 
        is added to session[total_time] which records how long the user took to answer
        all riddles
        """
        stop_time = datetime.now()
        start_time = session["start_time"]
        if session["total_time"] == None:
            session["total_time"] = 0
        session["total_time"] += (stop_time - start_time).total_seconds()
        
        # The users answer is added to session
        session["answers"].append(add_answer(current_random_question, request.form["answer"].upper()))
        
        # Iterates all possible answers for the riddle, adding 1 to the users score if one of them is correct
        if not isinstance(riddles[current_random_question - 1]["answer"], list):
            if request.form["answer"].upper() == riddles[current_random_question - 1]["answer"].upper():
                if session["score"] == None:
                    session["score"] = 0
                session["score"] += 1
                print("correct")
        else:
            for answer in riddles[current_random_question - 1]["answer"]:
                if request.form["answer"].upper() == answer.upper():
                    if session["score"] == None:
                        session["score"] = 0
                    session["score"] += 1
                    print("correct")
                
        """
        Updates correct_answer attribute which lets question.html display a correct
        or incorrect message depending on the user's answer
        """
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
    
    # The current question the user is answering (for question.html)
    question = riddles[current_random_question - 1]
    
    """
    The next question button is updated to new current question the user is on. 
    If the user was already on the last question, the button takes user to Question End
    """
    
    if session["current_qu_num"] == 6:
        next_qu = "end"
    else:
        next_qu = session["current_qu_num"]
        
    
    title = "Riddles Game - Question %d" % (qu_num)
    
    return render_template("question.html", qu_num = qu_num, question = question, next_qu = next_qu, correct = correct, correct_answer = correct_answer, title = title)

"""
A leaderboard page users are directed to after completing the riddles game
"""

@app.route('/questions/end')
def end():
    # If the user has not yet completed the game, they are redirected to home
    if session["current_qu_num"] != 6:
        return redirect(url_for("index"))
     
    """
    Loads all entries from users.json, adds the user that's playing (if their
    score is better than their last attempt) and displayed the top sorted users 
    """
    
    users = json.load(open('data/users.json'))
    add_user_to_leaderboard(users)
    top_users = render_leaderboard(users)
    
    # Displays total time taken in a readable format
    total_time_str = turn_seconds_to_string(session["total_time"])
    
    title = "Riddles Game - End"
    
    return render_template("questions-end.html", top_users = top_users, total_time_str = total_time_str, title = title)  

"""
A page which rests all game attributes and logs out the user, redirecting them to home
"""
@app.route("/logout")
def logout():
    
    try:
        del session["username"]
    except KeyError:
        return redirect(url_for("index"))
        
    session["current_qu_num"] = None
    reset_game_attributes()
    return redirect(url_for("index"))
    
"""
Displays the leaderboard, the top 25 sorted users from user.json
"""
@app.route("/leaderboard")
def leaderboard():
    
    # Loads all users and displays top 25 sorted by score and total time
    users = json.load(open('data/users.json'))
    top_users = render_leaderboard(users)
    
    title = "Riddles Game - Leaderboard"
    
    return render_template("leaderboard.html", top_users = top_users, title = title)
    
# Make debug false
# If name for test_riddle
if __name__ == "__main__":
     app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=False)
    # app.run(host=os.getenv('IP', "0.0.0.0"), port=int(os.getenv('PORT', "8080")), debug=True)