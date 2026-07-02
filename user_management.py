import sqlite3 as sql
import time
import random
from main import bcrypt


#Create a function to insert a user into the database
def insertUser(username, password, DoB):
    #Connect to the database
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    #Insert the username, password and dob into a new entry into the datbaase
    #The input are seperate from the query, helping prevent SQL injections
    try:
        #Try and add the username and password into the database
        cur.execute(
            "INSERT INTO users (username,password,dateOfBirth) VALUES (?,?,?)",
            (username, password, DoB),
        )
    except:
        #If this error pops up, then except the error
        # Then rollback the previous commit and undo all changes, to ensure that the database is not locked down due to the error
        con.rollback()
        return False
    #Commit the change to the database
    con.commit()
    #Close the connection to the database
    con.close()
    


#Create a function to get users from the database
def retrieveUsers(username, password):
    #Connect to the database
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    #Fetch the entry in the database which matches the username
    #Works because usernames have to be unique
    #The input are seperate from the query, helping prevent SQL injections
    user = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    print(user)
    columns = ['id', 'username', 'password', 'dob']
    user_dict = dict(zip(columns, user))
    #If no entries found
    if not user_dict:
        #Close the connection and return False
        con.close()
        print("WHY DOES THIS WORK")
        return False
    else:
        # # If the user provided the right username, then check if the password is right
        # Hash the password provided and check if it matches the password in the database
        # Use flask bcrypt to hash the password for better security
        print("THIS WORKSKSKSKSSKSKSKSKSKSKKSKSSKKSKS")
        if bcrypt.check_password_hash(user_dict['password'], password):
            print("DOES THIS WORKSKSKKSKSKSK")
            # Plain text log of visitor count as requested by Unsecure PWA management
            with open("visitor_log.txt", "r") as file:
                number = int(file.read().strip())
                number += 1
            with open("visitor_log.txt", "w") as file:
                file.write(str(number))
            # Simulate response time of heavy app for testing purposes
            time.sleep(random.randint(80, 90) / 1000)
            return True
        else:
            return False

#Create a function to insert feedback provided by the user
def insertFeedback(feedback):
    #Connect to the database
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    #Insert feedback into a new entry in the feedback table
    #The input are seperate from the query, helping prevent SQL injections
    cur.execute("INSERT INTO feedback (feedback) VALUES (?)", (feedback,))
    #Commit the change to the database
    con.commit()
    #Close the connection to the database
    con.close()

#Create a function to list the feedback in the database
def listFeedback():
    #Connect to the database
    con = sql.connect("The_Unsecure_PWA-2026-main/database_files/database.db")
    cur = con.cursor()
    #From the database fetch all feedback
    data = cur.execute("SELECT * FROM feedback").fetchall()
    print(data)
    #Disconnect the connection to the database
    con.close()
    #Open the success_feedback.html page
    f = open("The_Unsecure_PWA-2026-main/templates/partials/success_feedback.html", "w")
    #For each row in the collected from database
    #Add to the html page
    for row in data:
        f.write("<p>\n")
        f.write(f"{row[1]}\n")
        f.write("</p>\n")
    f.close()
