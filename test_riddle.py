import os
from riddle import app, turn_seconds_to_string
import unittest
import random
import flask
from flask import url_for
from datetime import datetime
import time
    
def setup_user(sess):
    # Sets sessions to recreate a user about to start game
    sess['score'] = 0
    sess['answers'] = []
    sess['total_time'] = 0
    sess['random_questions'] = random.sample(range(10), 5) 
    sess['visited_check'] = []
    sess['answer_check'] = []
    sess['answers'] = []
    sess['start_time'] = None
    sess["current_qu_num"] = 1

class RiddleTests(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True 

    def tearDown(self):
        pass 
    
    """
    Test pages respond with 200 when the correct variables are set
    """
    # Index
    def test_index_200_response(self):
        with app.test_client() as client:
            # Test the request in this context block.
            result = client.get("/")
            self.assertEqual(result.status_code, 200) 
   
    # Questions home 
    def test_questions_home_200_response(self):
        with app.test_client() as client:
                with client.session_transaction() as sess:
                    setup_user(sess)
                    sess["username"] = "TESTINGNAME"
        # Test the request in this context block.
        result = client.get("/questions/home")
        self.assertEqual(result.status_code, 200) 
    
    # Questions new game 
    def test_questions_new_game_200_response(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                    sess["username"] = "TESTINGNAME"
            # Test the request in this context block.
            result = client.get("/questions/new-game")
            self.assertEqual(result.status_code, 200) 
    
    # Question 1
    def test_question_200_response(self):
        with app.test_client() as client:
                with client.session_transaction() as sess:
                    setup_user(sess)
        # Test the request in this context block.
        result = client.get("/questions/1")
        self.assertEqual(result.status_code, 200)
        
    # Questions 1+
    def test_question_1_plus_200_response(self):
        with app.test_client() as client:
                with client.session_transaction() as sess:
                    setup_user(sess)
                    sess["current_qu_num"] = 2
        # Test the request in this context block.
        result = client.get("/questions/2")
        self.assertEqual(result.status_code, 200)
    
    # Questions end
    def test_question_end_200_response(self):
        with app.test_client() as client:
                with client.session_transaction() as sess:
                    setup_user(sess)
                    sess["username"] = "TESTINGNAME"
                    sess["current_qu_num"] = 6
        # Test the request in this context block.
        result = client.get("/questions/end")
        self.assertEqual(result.status_code, 200) 
        
    # Leaderboard
    def test_leaderboard_200_response(self):
        result = self.app.get("/leaderboard")
        self.assertEqual(result.status_code, 200) 
                
    """
    Test - When user starts the game and then posts an answer, the time taken to do so is added to 'total_time' in user's session
    """
    def test_question_timer(self):
        with app.test_client() as client:
                with client.session_transaction() as sess:
                    # Modify the session in this context block.
                    setup_user(sess)

                client.get("/questions/1")
                # Saves time page loads for testing
                testing_start_time = datetime.now()
                # Waits 1-4 seconds
                time.sleep(random.randint(1,4))
                # Submits POST request (simulate answering question)
                client.post("/questions/1")
                # Saves time POST request is made
                test_end_time = datetime.now()
                # Equates time between start and end
                testing_total_time = (test_end_time - testing_start_time).total_seconds()
                """
                Checks simulated testing total time equals total time saved to session in app
                Check is within 1 second to account for any differences when datetime.now() is run
                """
                self.assertAlmostEqual(testing_total_time, flask.session["total_time"], None, None, 1)

    # Test - User has no 'username' in session redirected to homepage
    def test_questions_home_redirect(self):
        with app.test_request_context():
            with app.test_client() as client:
                    with client.session_transaction() as sess:
                        setup_user(sess)
            result = client.get("/questions/home")
            self.assertEqual(result.status_code, 302) 
            self.assertEqual(result.location, url_for('index', _external=True))

    # Test - qu_num is not an integer, user is redirected to index
    def test_questions_redirect_not_integer(self):
        with app.test_request_context():
                with app.test_client() as client:
                        with client.session_transaction() as sess:
                            setup_user(sess)
                result = client.get("/questions/not_integer")
                self.assertEqual(result.status_code, 302) 
                self.assertEqual(result.location, url_for('index', _external=True))
    
    # Test - qu_num is not the current question user is on, user is redirected to index
    def test_questions_redirect_not_current_qu(self):
        with app.test_request_context():
                with app.test_client() as client:
                        with client.session_transaction() as sess:
                            setup_user(sess)
                            sess["current_qu_num"] = 2
                result = client.get("/questions/1")
                self.assertEqual(result.status_code, 302) 
                self.assertEqual(result.location, url_for('index', _external=True))

    # Test - redirect if qu_num is not within random_questions length
    def test_questions_redirect_qunum_not_within_length(self):
        with app.test_request_context():
                with app.test_client() as client:
                        with client.session_transaction() as sess:
                            setup_user(sess)
                result = client.get("/questions/9")
                self.assertEqual(result.status_code, 302) 
                self.assertEqual(result.location, url_for('index', _external=True))
                
    # Test - Redirect if current_qu_num or score not in session
    def test_questions_redirect_qunum_not_in_session(self):
        with app.test_request_context():
                with app.test_client() as client:
                        with client.session_transaction() as sess:
                            setup_user(sess)
                            sess.pop("current_qu_num")
                result = client.get("/questions/1")
                self.assertEqual(result.status_code, 302) 
                self.assertEqual(result.location, url_for('index', _external=True))
        
        with app.test_request_context():
                with app.test_client() as client:
                        with client.session_transaction() as sess:        
                            setup_user(sess)
                            sess.pop("score")
                result = client.get("/questions/1")
                self.assertEqual(result.status_code, 302) 
                self.assertEqual(result.location, url_for('index', _external=True))
                
    # Test - if qu_num not in visited_check, it is added on visiting relevant question number
    def test_questions_qunum_added_to_visitedcheck(self):
        with app.test_request_context():
                with app.test_client() as client:
                        with client.session_transaction() as sess:
                            setup_user(sess)
                        response = client.get("/questions/1")
                        self.assertEqual(flask.session['visited_check'],[1])
                        
    # Test - user is redirected from questions/end if they haven't completed all the questions
    def test_questions_redirect_not_completed_quix(self):
        with app.test_request_context():
                with app.test_client() as client:
                        with client.session_transaction() as sess:
                            setup_user(sess)
                result = client.get("/questions/end")
                self.assertEqual(result.status_code, 302) 
                self.assertEqual(result.location, url_for('index', _external=True))
                            
    def test_home(self):
        result = self.app.get('/') 
        # assert the status code of the response
        self.assertEqual(result.status_code, 200) 

 
if __name__ == "__main__":
    unittest.main()