import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
import secrets
import string
from email.message import EmailMessage
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from dotenv import load_dotenv

load_dotenv()
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key["api-key"] = os.getenv("BREVO_API_KEY")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
app = Flask(__name__)
app.secret_key = "learnflow_secret_key"


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        port=int(os.getenv("MYSQLPORT")),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE")
    )

# Study material for all topics
materials = {
    "osi-model": {
        "topic_id": "osi-model",
        "title": "OSI Model",
        "subject": "Computer Networks",
        "content": """
The OSI Model stands for Open Systems Interconnection Model.

It is a conceptual model that explains how data travels from one computer to another through a network.

The OSI Model has seven layers:

1. Physical Layer
2. Data Link Layer
3. Network Layer
4. Transport Layer
5. Session Layer
6. Presentation Layer
7. Application Layer

Each layer performs a specific task during communication.

The Physical Layer transfers raw bits through cables, radio signals, or other transmission media.

The Data Link Layer provides node-to-node data transfer and handles physical addressing.

The Network Layer is responsible for logical addressing and routing.

The Transport Layer provides reliable end-to-end communication.

The Session Layer manages communication sessions.

The Presentation Layer handles data formatting, encryption, and compression.

The Application Layer provides network services to applications used by the user.
"""
    },

    "dns": {
        "topic_id": "dns",
        "title": "DNS",
        "subject": "Computer Networks",
        "content": """
DNS stands for Domain Name System.

DNS converts human-readable domain names into IP addresses.

For example, when you enter:

www.google.com

your computer needs the IP address of Google's server.

DNS finds the corresponding IP address and helps the browser connect to the correct server.

DNS is often called the phonebook of the internet.

The basic DNS process is:

1. The user enters a domain name.
2. The browser asks a DNS resolver.
3. The resolver finds the IP address.
4. The IP address is returned to the browser.
5. The browser connects to the web server.
"""
    },

    "http": {
        "topic_id": "http",
        "title": "HTTP",
        "subject": "Computer Networks",
        "content": """
HTTP stands for HyperText Transfer Protocol.

HTTP is an application-layer protocol used for communication between a web browser and a web server.

When you open a website, the browser sends an HTTP request to the server.

The server processes the request and sends an HTTP response.

For example:

Browser:
GET /index.html

Server:
HTTP response containing the requested web page.

Common HTTP methods include:

GET:
Used to request data from a server.

POST:
Used to send data to a server.

PUT:
Used to update data.

DELETE:
Used to delete data.

HTTPS is the secure version of HTTP.
"""
    },

    "python-basics": {
        "topic_id": "python-basics",
        "title": "Python Basics",
        "subject": "Python",
        "content": """
Python is a high-level, interpreted, and general-purpose programming language.

Python is known for its simple and readable syntax.

Python is used in:

Web development
Artificial Intelligence
Machine Learning
Data Science
Automation
Software development

A simple Python program is:

print("Hello, World!")

Variables are used to store data.

Example:

name = "Arsalan"

age = 20

Python supports different data types:

int:
Stores whole numbers.

float:
Stores decimal numbers.

str:
Stores text.

bool:
Stores True or False values.

Python uses indentation to define blocks of code.
"""
    },

    "lists-tuples": {
        "topic_id": "lists-tuples",
        "title": "Lists and Tuples",
        "subject": "Python",
        "content": """
Lists and tuples are used to store multiple values in one variable.

A list is written using square brackets.

Example:

numbers = [10, 20, 30]

Lists are mutable. This means their values can be changed.

Example:

numbers[0] = 100

A tuple is written using parentheses.

Example:

colors = ("Red", "Green", "Blue")

Tuples are immutable. This means their values cannot be changed after creation.

List:

Mutable
Uses square brackets
Usually used when data may change

Tuple:

Immutable
Uses parentheses
Usually used when data should remain fixed
"""
    },

    "functions": {
        "topic_id": "functions",
        "title": "Functions",
        "subject": "Python",
        "content": """
A function is a reusable block of code that performs a specific task.

Functions help reduce repeated code.

A function is created using the def keyword.

Example:

def greet():

    print("Hello")

The function can be called using:

greet()

Functions can accept parameters.

Example:

def greet(name):

    print("Hello", name)

greet("Arsalan")

Functions can also return a value.

Example:

def add(a, b):

    return a + b

result = add(10, 20)

print(result)

The output will be:

30
"""
    }
}


# Quiz questions for all topics
quiz_questions = {
    "osi-model": [
        {
            "question": "What does OSI stand for?",
            "options": [
                "Open System Interconnection",
                "Online System Interface",
                "Open Software Internet",
                "Operating System Interface"
            ],
            "answer": "Open System Interconnection"
        },
        {
            "question": "How many layers are present in the OSI model?",
            "options": ["5", "6", "7", "8"],
            "answer": "7"
        },
        {
            "question": "Which is the lowest layer of the OSI model?",
            "options": [
                "Application Layer",
                "Network Layer",
                "Physical Layer",
                "Transport Layer"
            ],
            "answer": "Physical Layer"
        },
        {
            "question": "Which layer is responsible for routing?",
            "options": [
                "Data Link Layer",
                "Network Layer",
                "Session Layer",
                "Presentation Layer"
            ],
            "answer": "Network Layer"
        },
        {
            "question": "Which layer provides end-to-end communication?",
            "options": [
                "Physical Layer",
                "Transport Layer",
                "Network Layer",
                "Application Layer"
            ],
            "answer": "Transport Layer"
        }
    ],

    "dns": [
        {
            "question": "What does DNS stand for?",
            "options": [
                "Domain Name System",
                "Data Network Service",
                "Digital Name Server",
                "Domain Network Security"
            ],
            "answer": "Domain Name System"
        },
        {
            "question": "What is the main function of DNS?",
            "options": [
                "Encrypt data",
                "Convert domain names into IP addresses",
                "Create websites",
                "Transfer files"
            ],
            "answer": "Convert domain names into IP addresses"
        },
        {
            "question": "DNS is often called the ______ of the internet.",
            "options": ["Engine", "Phonebook", "Browser", "Cable"],
            "answer": "Phonebook"
        },
        {
            "question": "Which of the following is a domain name?",
            "options": [
                "192.168.1.1",
                "www.google.com",
                "255.255.255.0",
                "8080"
            ],
            "answer": "www.google.com"
        },
        {
            "question": "What does a DNS resolver return?",
            "options": [
                "A password",
                "An IP address",
                "A web page",
                "A file"
            ],
            "answer": "An IP address"
        }
    ],

    "http": [
        {
            "question": "What does HTTP stand for?",
            "options": [
                "HyperText Transfer Protocol",
                "HighText Transfer Program",
                "Hyper Transfer Text Process",
                "Host Transfer Protocol"
            ],
            "answer": "HyperText Transfer Protocol"
        },
        {
            "question": "HTTP works mainly between a ______ and a server.",
            "options": [
                "Keyboard",
                "Web browser",
                "Printer",
                "Database"
            ],
            "answer": "Web browser"
        },
        {
            "question": "Which HTTP method is commonly used to request data?",
            "options": ["POST", "GET", "DELETE", "PUT"],
            "answer": "GET"
        },
        {
            "question": "Which HTTP method is commonly used to send data?",
            "options": ["GET", "POST", "TRACE", "HEAD"],
            "answer": "POST"
        },
        {
            "question": "What is HTTPS?",
            "options": [
                "An old version of HTTP",
                "The secure version of HTTP",
                "A database",
                "A programming language"
            ],
            "answer": "The secure version of HTTP"
        }
    ],

    "python-basics": [
        {
            "question": "Python is a ______ programming language.",
            "options": [
                "Low-level",
                "High-level",
                "Machine-level",
                "Assembly-only"
            ],
            "answer": "High-level"
        },
        {
            "question": "Which function is used to display output in Python?",
            "options": ["show()", "display()", "print()", "output()"],
            "answer": "print()"
        },
        {
            "question": "Which symbol is used to assign a value to a variable?",
            "options": ["==", "=", "!=", ">"],
            "answer": "="
        },
        {
            "question": "Which data type stores text in Python?",
            "options": ["int", "float", "str", "bool"],
            "answer": "str"
        },
        {
            "question": "Which value is a Boolean value in Python?",
            "options": ["10", "Hello", "True", "3.5"],
            "answer": "True"
        }
    ],

    "lists-tuples": [
        {
            "question": "Which brackets are used to create a list?",
            "options": ["()", "[]", "{}", "<>"],
            "answer": "[]"
        },
        {
            "question": "Which brackets are commonly used to create a tuple?",
            "options": ["[]", "{}", "()", "<>"],
            "answer": "()"
        },
        {
            "question": "A list is ______.",
            "options": [
                "Immutable",
                "Mutable",
                "Always empty",
                "A function"
            ],
            "answer": "Mutable"
        },
        {
            "question": "A tuple is ______.",
            "options": [
                "Mutable",
                "Immutable",
                "A loop",
                "A condition"
            ],
            "answer": "Immutable"
        },
        {
            "question": "Which collection can be changed after creation?",
            "options": [
                "Tuple",
                "List",
                "String only",
                "Integer"
            ],
            "answer": "List"
        }
    ],

    "functions": [
        {
            "question": "Which keyword is used to define a function in Python?",
            "options": ["function", "define", "def", "func"],
            "answer": "def"
        },
        {
            "question": "What is a function?",
            "options": [
                "A reusable block of code",
                "A database",
                "A browser",
                "An operating system"
            ],
            "answer": "A reusable block of code"
        },
        {
            "question": "Which keyword is used to send a value back from a function?",
            "options": ["print", "send", "return", "output"],
            "answer": "return"
        },
        {
            "question": "What is used to call a function named greet?",
            "options": [
                "call greet",
                "greet()",
                "def greet",
                "function greet"
            ],
            "answer": "greet()"
        },
        {
            "question": "What are values passed to a function called?",
            "options": ["Arguments", "Layers", "Classes", "Files"],
            "answer": "Arguments"
        }
    ]
}


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["user_name"] = user["full_name"]
            session["user_email"] = user["email"]

            return redirect(url_for("dashboard"))

        session["reset_email"] = email

        return render_template(
            "login.html",
            show_forgot_password=True,
            entered_email=email
        )

    return render_template(
        "login.html",
        show_forgot_password=False
    )


import socket
import traceback

socket.setdefaulttimeout(10)
@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    email = session.get("reset_email")

    if not email:
        flash("Please enter your email and password first.")
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (email,)
    )

    user = cursor.fetchone()

    if not user:
        cursor.close()
        connection.close()

        flash("This email is not registered.")
        return redirect(url_for("login"))

    # Generate random password
    characters = (
        string.ascii_letters
        + string.digits
        + "@#$%"
    )

    new_password = "".join(
        secrets.choice(characters)
        for _ in range(10)
    )

    hashed_password = generate_password_hash(new_password)

    # Update password
    cursor.execute(
        """
        UPDATE users
        SET password = %s
        WHERE email = %s
        """,
        (hashed_password, email)
    )

    connection.commit()

    cursor.close()
    connection.close()

    # Send email using Brevo
    try:
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        sender = {
            "name": "LearnFlow",
            "email": os.getenv("EMAIL_ADDRESS")
        }

        to = [
            {
                "email": email,
                "name": user["full_name"]
            }
        ]

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender,
            to=to,
            subject="LearnFlow - New Password",
            text_content=f"""Hello {user["full_name"]},

Your LearnFlow password has been reset.

Your new password is:

{new_password}

Please log in using this new password.

Regards,
LearnFlow
"""
        )

        response = api_instance.send_transac_email(
            send_smtp_email
        )

        print("Brevo Response:", response)

        session.pop("reset_email", None)

        flash(
            "A new password has been sent to your email.",
            "success"
        )

    except ApiException as e:
        print("Brevo API Error:", e)

        flash(
            "The password was changed, but the email could not be sent.",
            "error"
        )

    except Exception as e:
        print("Error:", e)

        flash(
            "Something went wrong while sending the email.",
            "error"
        )

    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users
                (
                    full_name,
                    email,
                    password
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    full_name,
                    email,
                    hashed_password
                )
            )

            connection.commit()

            flash(
                "Registration successful. Please log in."
            )

            return redirect(url_for("login"))

        except mysql.connector.IntegrityError:
            flash(
                "This email is already registered."
            )

            return redirect(url_for("register"))

        finally:
            cursor.close()
            connection.close()

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        user_name=session["user_name"],
        user_email=session["user_email"]
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/logout-on-back", methods=["POST"])
def logout_on_back():
    session.clear()
    return "", 204


@app.route("/delete-account", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM users
        WHERE user_id = %s
        """,
        (user_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    session.clear()

    flash(
        "Your account has been deleted successfully."
    )

    return redirect(url_for("login"))


@app.route("/study/<topic>")
def study_material(topic):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if topic not in materials:
        return "Topic not found", 404

    return render_template(
        "study_material.html",
        material=materials[topic]
    )


@app.route("/quiz/<topic>")
def quiz(topic):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if topic not in quiz_questions:
        return "Quiz not found", 404

    return render_template(
        "quiz.html",
        topic=topic,
        questions=quiz_questions[topic]
    )


@app.route("/submit-quiz/<topic>", methods=["POST"])
def submit_quiz(topic):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if topic not in quiz_questions:
        return "Quiz not found", 404

    questions = quiz_questions[topic]

    score = 0
    results = []

    for index, question in enumerate(questions):
        selected_answer = request.form.get(
            f"question_{index}"
        )

        correct_answer = question["answer"]

        is_correct = (
            selected_answer == correct_answer
        )

        if is_correct:
            score += 1

        results.append({
            "question": question["question"],
            "selected_answer": selected_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })

    total_questions = len(questions)

    percentage = (
        score / total_questions
    ) * 100

    if percentage >= 80:
        performance_level = "Excellent"

        recommendation = (
            "You have a strong understanding of this topic. "
            "You can move to the next topic and continue learning."
        )

        recommendation_type = "excellent"

    elif percentage >= 60:
        performance_level = "Good"

        recommendation = (
            "You understand most of the topic, but you should "
            "review the incorrect answers and practice again."
        )

        recommendation_type = "good"

    elif percentage >= 40:
        performance_level = "Needs Improvement"

        recommendation = (
            "Your understanding is developing, but some concepts "
            "need more attention. Review the study material and "
            "retry the quiz."
        )

        recommendation_type = "improvement"

    else:
        performance_level = "Needs Revision"

        recommendation = (
            "You should revise the complete topic carefully. "
            "Understand the basic concepts and then retry the quiz."
        )

        recommendation_type = "revision"

    user_id = session["user_id"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO quiz_reports
        (
            user_id,
            topic,
            score,
            total_questions,
            percentage,
            performance_level,
            recommendation
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            user_id,
            topic,
            score,
            total_questions,
            percentage,
            performance_level,
            recommendation
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return render_template(
        "quiz_result.html",
        score=score,
        total=total_questions,
        percentage=percentage,
        results=results,
        topic=topic,
        performance_level=performance_level,
        recommendation=recommendation,
        recommendation_type=recommendation_type
    )


@app.route("/my-progress")
def my_progress():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            report_id,
            topic,
            score,
            total_questions,
            percentage,
            performance_level,
            recommendation,
            attempted_at
        FROM quiz_reports
        WHERE user_id = %s
        ORDER BY attempted_at DESC
        """,
        (user_id,)
    )

    reports = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "progress.html",
        reports=reports
    )


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        new_password = request.form["new_password"]

        hashed_password = generate_password_hash(
            new_password
        )

        user_id = session["user_id"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE user_id = %s
            """,
            (
                hashed_password,
                user_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        flash(
            "Your password has been reset successfully."
        )

        return redirect(
            url_for("reset_password")
        )

    return render_template(
        "reset_password.html"
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )