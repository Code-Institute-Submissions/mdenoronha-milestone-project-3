Riddles Game 
=============
A milestone project displaying capabilities in HMTL, CSS, Javascript, Python and the Flask framework.
The project is a riddle game where the user is shown a random selection of 5 riddles that they have to answer correctly.
The game makes use of a leaderboard, where users are sorted into those with the higher scores and those who answered the fastest.

UX
---------------
The main intended user is someone interested in riddles and wishes to play a game based on guessing riddles.
* Given the competitive nature of the game (with the addition of a leaderboard), the app's intended user is someone who is competitive and wishes to compete against other players
* Correct answers are supplied at the end of each riddle, whether the answer is correct or not. Helping to satisfy non-competitive players who only wish to attempt to answer a series of fun riddles.
* The app is geared towards users who wish to play the game on mobile or desktop; the site is fully responsive - catering to both user types

Wireframes can be found [here](https://github.com/mdenoronha/milestone-project-3/tree/master/wireframes)

The following alterations were made after the mock-up phase:
* Text positioning on leaderboard
* Icons used on navigation bar and game options

Features
---------------
### Existing Features ###
*Creating a user*
* Users are able to enter a name on the register form on the homepage to save a username, this username is saved to users.json (with limitations, explained in more detail later on)
* Other users are not able to register the same username, giving a unique account for users to make use of
* Usernames are saved to a user's session, allowing them leave the site and return logged in (within limitations of session cookie)
* Users are able to log out of their account by clicking the log out icon
* Users are able to log in to their account by clicking the log in button and entering their username (no password is required)

*Functionality of the game*
* Random riddles are shown to users by starting a new game (up to 5)
* An answer form is displayed allowing users to make a guess of the answer
* Correct guesses add one to a saved score attribute assigned to the user's session, the user is made aware they guessed correctly/incorrectly
* Correct answers are shown to the user, irrespective of their answer
* The time taken to answer the question is recorded and added to a total_time attribute assigned to the user's session
* As the time taken to answer the question only starts on first view of the riddle, users are not able to gain extra time to answer the question by leaving the site.
* On leaving the site, users are able to continue their game by selecting the Continue Game option
* Variations of answers are taken into account. User's guesses are compared to a range of possible answers to allow for any inconsistencies (e.g. 'television', 'a television', 'a television set')
* Users are able to quit the game and delete their progress at any time by logging out
* When 5 random riddles are answered, users are directed to a leaderboard where the top 25 users are displayed (in order of score and total time taken to answer riddles)
* Users score and total time is added to user.json (as long as it is better than their previous attempt) (with limitations, explained in more detail later on)
* If users score and total time is in the top 25, their username is displayed in the leaderboard
* User's score and total time are shown once the game is completed
* The game can be started again (at any point) by selecting New Game option

*Other features*
* At any time, users can select Instructions from the navigation menu to see an explanation of the game
* At any time, users can see the leaderboard. This can be done by selecting leaderboard from the navigation menu or the Leaderboard option when a game is not being played

### Features Left to Implement ###
* Due Heroku's ephemeral filesystem, while the necessary logic is in place to add users to user.json and to update their scores after each game, this update does not persist permanently. A further update would be to find an alternative option to update the json file.
* The app makes no use of secure user authentication. This means that users are able to log into any account using only the username. A feature to implement would be to add secure authentication with passwords.
* Users are only able to guess an answer to a riddle once, a possible update would be to allow users multiple guessing before the riddle was marked as incorrect.

Technologies Used
---------------
* Python was used extensively in the creation of the app
* A number of modules were used within the app:
    * Flask framework necessary for building web application
    * random module in order to choose 5 random riddles
    * datetime module to assist in the recording of user's game time
    * json module for interaction with json files
* As only a basic amount of Javascript was required, no Javascript frameworks or libraries were used. The small amount of Javascript required also didn't necessitate a separate file, with Javascript written within script tags within the relevant HTML files.
* unittest was used to build the testing framework

Functionality
---------------
* At the homepage, users are encouraged to add a username in the register form
    * If this username hasn't been entered before, it is added to users.json using the add_user_to_leaderboard() method
    * If the username has been entered before, flash provides a message navigating users to the log in form
* As the user enters a username into the log in form:
    * If the username is present in users.json, the username is assigned to the user's session and on refreshing they are redirected to Questions Home
    * If the username is not present in users.json, flash provides a message informing the user that the username is not recognised
* On Questions Home, the user is assigned a current_qu_num attribute to their session
* On selecting New Game option, the user is directed to qu_new()
* On Questions New, the current_qu_num attribute is updated to the user's current question number (1) and all essential game attributes are reset to their starting values using reset_game_attributes() method
* On continuing the user is directed to /questions/1, as this corresponds with their current_qu_num they are not redirected away from this page
* As the user has not visited this question before, the question number is added to visited_questions attribute in the user's session
* datetime.now() is used to record the current time when the question was first seen. This will not re-run if the user visits the page again as the question number is present in visited_questions
* The question the user is currently on increases by, saved in the current_qu_num attribute
* When the user answers the riddle and makes a POST request, the time is recorded and the difference between the start and end time is added to the total-time attribute on the user's session
* All possible answers (present in riddles.json) are iterated over, if the user's input matches one their score (saved to their session) is incremented by one
* correct is updated with whether they were correct or not, this is used by question.html to display the appropriate message
* The next question link is updated to take the user to their current_qu_num. If current_qu_num is 6, the game is over and the user is directed to Questions End
* If the user leaves at any point before the game is over, the Leaderboard option on Questions Home changes to a Continue Game option - taking the user to their current_qu_num or Questions End
* At Questions End, users.json is loaded and the user is added to the file (if their score and total_time is better than their last attempt)
* render_leaderboard() is run which sorts all users by score, and then by total time. The top 25 are then selected and assigned to top_users
* The relevant HTML file displays top_users as a table

Testing
---------------
Python testing document can be found [here](https://github.com/mdenoronha/milestone-project-3/blob/master/test_riddle.py)
The file is run by using 'python3 test_riddle.py' command

### Testing through test_riddle.py ###
Test  | Status
------------- | -------------
Testing 200 Responses |
Visiting Homepage returns a 200 response when the appropriate attributes are met | Successful
Visiting Questions Home returns a 200 response when the appropriate attributes are met | Successful
Visiting Questions New Game returns a 200 response when the appropriate attributes are met | Successful
Visiting Question 1 returns a 200 response when the appropriate attributes are met | Successful
Visiting Question 1+ returns a 200 response when the appropriate attributes are met | Successful
Visiting Question End returns a 200 response when the appropriate attributes are met | Successful
Visiting Leaderboard returns a 200 response when the appropriate attributes are met | Successful
Other Tests |
When user starts the game and then posts an answer, the time taken to do so is added to total_time in user's session | Successful
If user has no username attribute in session they are redirected to Homepage | Successful
If qu_num is not an integer, user is redirected to Homepage | Successful
If qu_num is not the same as the current question the user is on, user is redirected to Homepage | Successful
If qu_num is not within the length of random_questions, user is redirected to homepage | Successful
If current_qu_num or score not in session, user is redirected to homepage | Successful
If qu_num not in visited_check, it is added on visiting relevant question number | Successful
User is redirected from Questions End if they haven't completed all the questions | Successful


### Manual Testing ###
Test  | Status
------------- | -------------
Basic Tests |
Selecting instructions icon in navigation displays instructions modal | Successful
Selecting leaderboard icon in navigation takes user to Leaderboard | Successful
If the user has username attribute in session and has logged in, the log out icon is displayed | Successful
If the user has no username attribute in session and has not logged in, the log in icon is displayed | Successful
Selecting log in icon in navigation on the homepage displays login modal | Successful
Selecting log in icon in navigation on any other page takes the user to the homepage and displays login modal | Successful
Selecting log out icon in navigation displays log out modal | Successful
If no game is currently being played, the Leaderboard option is displayed | Successful
If a game is currently being played, the Leaderboard option is displayed | Successful
User Tests |
Entering a username on the register form that is already in users.json displays an error message | Successful
Entering a username on the log in form that is not in users.json displays an error message | Successful
Entering a new username on the register form adds the user to user.json | Failed
Due to Heroku ephemeral filesystem the update to the file does not exist permanently |
Entering a new username on the register form takes the user to Questions Home and saves the username to session | Successful
Entering a username already in users.json on the login form takes the user to Questions Home and saves the username to session | Successful
Confirming log out on the log out modal takes the user to the homepage and removes username from session | Successful
Login and register inputs are required fields | Successful
Game functionality |
By visiting Questions New, reset_game_attributes() is run and main game attributes are reset | Successful
By visiting Questions New, a random list of 5 questions are generated | Successful
Questions/1 displays the first riddle in the random_questions list | Successful
Inputting any of the correct answers (as seen in riddles.json) displays the correct answer modal | Successful
Inputting any of the correct answers (as seen in riddles.json) adds one to the score attribute | Successful
Inputting a wrong answer displays the incorrect answer modal | Successful
The correct and incorrect answer modals display one of the correct answers (as seen in riddles.json) | Successful
The next question button takes the user to question number one more than their currently on (up to 5) | Successful
On leaving Questions, the Continue Game option takes users to the current question they are on | Successful
Answer inputs are required fields | Successful
If the user has completed all 5 questions, the next question button takes users to Questions End | Successful
On Questions End, the user's score is displayed correctly | Successful
On Questions End, the user's total time is displayed correctly | Successful
The table features the user (if their score and total time is within the top 25) | Successful
The table features the top 25 users by score and then by total time | Successful

Deployment
---------------
Project has been deployed to Heroku and is accessible [here](https://riddles-game.herokuapp.com/).
The process for deployment was as follows: 
* Create a new app in Heroku
* Link Github repository to Heroku with automatic deploys turned on
* Create requirements.txt file
* Create Procfile 
* Update app's PORT and IP to correspond with Heroku

Credits
---------------
* Assistance from [here](http://atodorov.org/blog/2013/01/28/remove-query-string-with-javascript-and-html5/) for removing URL parameters necessary for login modal
* Assistance on favicon implementation with Flask from [here](https://webmasters.stackexchange.com/questions/25876/how-do-i-deploy-a-favicon-on-heroku)
* [favicon-generator.org](https://www.favicon-generator.org/) used to create favicon
* Riddles provided by [riddles.fyi](https://riddles.fyi) and [riddles.com](https://www.riddles.com)


