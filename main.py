from flask import Flask, render_template, redirect, request, session
from flask_cors import CORS
import user_management as dbHandler
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, TextAreaField
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, urljoin
import html


load_dotenv()


#Function to help check is a url is safe
def is_safe_url(target):
    #Gets the base url of the PWA
    host_url = urlparse(request.host_url)
    #Joins the host url and the target url
    redirect_url = urlparse(urljoin(request.host_url, target))
    #Checks if the url uses http or https and then if the base url is the same
    return redirect_url.scheme in ("http", "https") and host_url.netloc == redirect_url.netloc

class SignIn_Form(FlaskForm):
    username = StringField("Username")
    password = PasswordField("Password")
    dob = DateField("Date of Birth")
    submit = SubmitField("Submit")

class LogIn_Form(FlaskForm):
    username = StringField("Username")
    password = PasswordField("Password")
    dob = DateField("Date of Birth")
    submit = SubmitField("Submit")    

class Feedback_Form(FlaskForm):
    feedback = TextAreaField("Enter your feedback here: ")
    submit = SubmitField("Submit")

#Create class which helped minimise chances of CSRF attacks
csrf = CSRFProtect()

#Initiate Flask app
app = Flask(__name__)
#Initiate the CSRF protection class
csrf.init_app(app)
# Enable CORS to allow cross-origin requests (needed for CSRF demo in Codespaces)
CORS(app)
#Create the Bcrypt class which will help hash passwords to store in the database
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")


#Initiate the class which will help restrict login attempts to stop brute force attacks 
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    #Set the limit, only 200 attempts per day and only 50 per hours
    default_limits=["200 per day", "50 per hour"]
)

##Create the sucess page for the PWA, the get request will retrieve the data(add comment data) and the post request will send through the review details
@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def addFeedback():
    form = Feedback_Form()
    #if the request method if get and a url parameter is passed
    target = request.args.get("url")    
    if request.method == "GET" and target:
        if is_safe_url(target):
            return redirect(target)
        return "Invalid redirect URL", 400
    #If the form was a valid submission then
    if form.validate_on_submit():  
        #Then let the feedback equal to the input from the form
        feedback = form.feedback.data
        safe_input = html.escape(feedback)
        #Use the dbHandler class function insertFeedback with a feedback parameter
        dbHandler.insertFeedback(safe_input)
        #Use the dbHandler class to list the Feedback from where it's stored   
        feedback_list = dbHandler.listFeedback()
        #Return the html page sucess, with the parameterers True and "Back"
        return render_template("success.html", state=True, value="Back", form=form, feedback=feedback_list)
    else:
        #If the POST method was not used, just use the dbHandle function listFeedback
        feedback_list = dbHandler.listFeedback()
        #Return the html page success
        return render_template("success.html", state=True, value="Back", form=form, feedback=feedback_list)

#Create the signup page for the PWA, using the GET, POST, PUT, PATCH, DELETE methods
@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    form = SignIn_Form()
    #if the request method if get and a url parameter is passed
    if request.method == "GET" and request.args.get("url"):
        #store the url parameter in the target variable
        target = request.args.get("url")
        #If the target is a safe url then redirect to target url
        if target and is_safe_url(target):
            return redirect(target)
        #Otherwise return invalid redirect url and an error
        elif target:
            return "Invalid redirect URL", 400
    #If the form was a valid submission
    if form.validate_on_submit():  
            #Get the username entered in the form
            username = form.username.data
            #Get the password entered in the form
            password = form.password.data
            #Using the bcrypt function generate a hash for the password
            hashed_password = bcrypt.generate_password_hash(password=password)
            #Get the DoB entered in the form
            DoB = form.dob.data
            #Use the insertUser function from the dbHandler, giving the username, password and dob parametred
            dbHandler.insertUser(username, hashed_password, DoB)
            #Return the index.html page
            return render_template("index.html", form=form)
    else:
        #If the post request wasn't used then return the signup.html page
        return render_template("signup.html", form=form)

#Create the index html page and use the methods, GET, PUT, POST, PATCH and DELETE
@app.route("/index.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@app.route("/", methods=["POST", "GET"])
#Add a decorater tag, using the limiter class to restrict the number of login attempts
@limiter.limit("5 per minute", override_defaults=True)
def home():
    form = LogIn_Form()
    #If the method used is the GET method and something was entered in the url parametered
    if request.method == "GET" and request.args.get("url"):
        #Let the url variable be the url which was inputted into the parameter
        url = request.args.get("url", "")
        #Redirect to the url that was inputted
        return redirect(url, code=302)
    #If the GET method is used by the url is not entered as a parameter
    elif request.method == "GET":
        #Get the msg from the msg parameter
        msg = request.args.get("msg", "")
        #Return the index.html page
        return render_template("index.html", msg=msg, form=form)
    #If the request is a POST request
    elif form.validate_on_submit():  
            #Get the username entered in the form
            username = form.username.data
            #Get the password entered in the form
            password = form.password.data   
            #let the isLoggedIn variable be equal to the output of the retreieveUser function from the dbHandler, which has the username and password as parameters
            isLoggedIn = dbHandler.retrieveUsers(username, password)
            #If isLoggedIn is true
            if isLoggedIn: 
                #Use the dbHandler listFeedback function
                feedback_list = dbHandler.listFeedback()
                #Return the success.html page, with the parameters username and the state of the isLoggedIn variable
                form_feedback = Feedback_Form()
                return render_template("success.html", value=username, state=isLoggedIn, form=form_feedback, feedback=feedback_list)
            else:
                #If isLoggedIn is false then return the index.html 
                return render_template("index.html", form=form)
    else:
        return render_template("index.html", form=form)


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=False, host="0.0.0.0", port=5000)
