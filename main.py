from flask import Flask, request, render_template, redirect, url_for
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import csv
import os
import smtplib

app = Flask(__name__)
app.config["FILE_UPLOADS"] = "temp"

email = None
password = None
csv_file = None
message = None
subject = None
server = None  # Initialize the SMTP server


@app.route("/", methods=["GET", "POST"])
def sendersmail():
    global email, password, csv_file, message, subject, server
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        subject = request.form.get("subject")
        message = request.form.get("message")

        if "file" in request.files:
            upload_file = request.files["file"]
            file_path = os.path.join(
                os.getcwd(), app.config["FILE_UPLOADS"], upload_file.filename
            )
            upload_file.save(file_path)
            csv_file = file_path
            return redirect("/htp")
        else:
            # Handle the case where the "filename" key is not present in request.files
            return "No file uploaded. Please select a file and try again."

    return render_template("index.html")


@app.route("/htp")
def sendingmails():
    print(request.method)
    global email, password, csv_file, message, subject, server
    msg = MIMEMultipart("alternative")
    msg["subject"] = subject
    msg["from"] = email

    part1 = MIMEText(message, "text")
    part2 = MIMEText(message, "html")

    msg.attach(part1)
    msg.attach(part2)
    # print(server)
    # if server is None:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    try:
        server.login(email, password)
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {str(e)}")
        return redirect(url_for("login_error"))

    try:
        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for eemail in reader:
                server.sendmail(email, eemail, msg.as_string())
        return render_template("index2.html")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return redirect("/")


@app.route("/login_error")
def login_error():
    return "Email login failed. Please check your email and password."


if __name__ == "__main__":
    app.run(debug=True)
