import os
from flask import Flask, render_template, request, session, redirect, url_for,jsonify, send_from_directory
from datetime import datetime
from dotenv import load_dotenv
import time
import json
import csv

load_dotenv()

app = Flask(__name__, static_url_path='/uploads')

app.secret_key = "LMNUrAcLmU"

valid_extensions = ["json"]

@app.route("/",methods=["GET", "POST"])
def get_winner():
    if 'loggedin' in session:
        if request.method == "POST":
            try:
                result = request.form.get("result")
                votesFile = request.files['votesFile']
                if not is_valid_file_extension(votesFile.filename, valid_extensions):
                    return "Invalid votes file format!"            
                today_date = datetime.now().strftime("%Y-%m-%d")
                filename = f"{today_date}_votes.json"
                file_path = os.path.join("uploads", filename) 
                votesFile.save(file_path)
                with open(file_path) as f:
                    votes = json.load(f)
                    def match_pattern(choices):
                        return choices == result
                    correctVotes = [vote for vote in votes if match_pattern(vote['Choices'])]
                    correctVotes.sort(key=lambda x: datetime.strptime(x['Date']['date'], '%Y-%m-%d %H:%M:%S.%f'))

                    # Extract field names from the first JSON object
                    fieldnames = correctVotes[0].keys()
                    csv_filename = f"{today_date}_result.csv"
                    csv_file_path  = os.path.join("uploads","output", csv_filename) 

                    # Write JSON data to CSV file
                    with open(csv_file_path, 'w', newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        
                        # Write header
                        writer.writeheader()
                        
                        # Write rows
                        for row in correctVotes:
                            writer.writerow(row)
                return str(csv_filename)
            except Exception as e:
                return str(e)
        return render_template("getWinner.html",userName = session.get('name'))
    else:
        return redirect(url_for('login'))     

@app.route("/download-result/<string:filename>")
def downloadResult(filename):
    try:
        if 'loggedin' in session:
            return send_from_directory(os.path.join('uploads','output'), filename, as_attachment=True)
        else:
            return redirect(url_for('login'))
    except Exception as e:
        return str(e)
    


@app.route("/login", methods=['GET','POST'])
def login():    
    username = os.getenv("USER_NAME")
    password = os.getenv("PASSWORD")
    if request.method == 'POST':
        username = request.form.get("username")
        password  = request.form.get("password")
        if username == os.getenv("USER_NAME") and password == os.getenv("PASSWORD"):
            session['loggedin'] = True
            session['name'] = username
            return redirect(url_for("get_winner"))
        else:
            return render_template("login.html",error="Invalid Credentials!")
        
    return render_template("login.html")
        
@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('name', None)
    # Redirect to index page
    return redirect(url_for('login'))

def is_valid_file_extension(filename, valid_extensions):
    # Get the file extension
    file_extension = filename.split(".")[-1].lower()

    # Check if the file extension is in the list of valid extensions
    if file_extension in valid_extensions:
        return True
    else:
        return False


if __name__ == "__main__":
    app.run(debug=True)