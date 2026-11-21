
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import os
import pickle
import random
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "change-this-secret-key-before-deployment"
)

# Admin Login Details
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "SVSU@123"

ENQUIRIES_FILE = "enquiries.json"
FEEDBACK_FILE = "feedback.json"


# JSON File Functions
def read_json_file(filename, default):
    if not os.path.exists(filename):
        return default

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, type(default)) else default

    except (json.JSONDecodeError, OSError):
        return default


def write_json_file(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# Admin Protection
def admin_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))

        return function(*args, **kwargs)

    return decorated_function


# College Information
college_data = {
    "courses": "SVSU offers undergraduate, postgraduate, diploma and Ph.D. programmes. Check https://svsu.ac.in/programmName.php for the published programme list.",

    "bca": "SVSU's published 2026-27 programme list includes BCA / BCA (AI & ML / Data Science). Please check the official brochure for eligibility and availability.",

    "mca": "Please check the current SVSU programme list and admission brochure to confirm whether MCA is offered for the session you are asking about.",

    "bba": "SVSU's published programme list includes BBA (Hons./Hons. with Research). Check the official brochure for details.",

    "mba": "SVSU's published programme list includes MBA for Working Professionals at Gurugram Campus.",

    "btech": "SVSU offers multiple B.Tech programmes. Check the official brochure for eligibility and details.",

    "admission": "For admission information, visit https://admission.svsu.ac.in and read the latest programme brochure.",

    "fees": "Fees are programme-specific. Please check the latest official SVSU brochure or contact admissions@svsu.ac.in.",

    "eligibility": "Eligibility is programme-specific. Please check the latest official SVSU brochure.",

    "timing": "Please contact the university office to confirm current office and class timings.",

    "contact": "SVSU Helpline: 1800 1800 147 | Email: info@svsu.ac.in | Admissions: admissions@svsu.ac.in | Main Campus: Village Dudhola, Palwal, Haryana."
}


# Detailed Portal Information
PORTAL_INFO = {
    "courses": {
        "title": "Course Information",
        "intro": "Programmes published by SVSU for Academic Session 2026-27.",
        "groups": [
            {
                "name": "UG Programmes",
                "items": [
                    "B.Tech. Computer Engineering",
                    "B.Tech. Computer Science & Engineering (AI & ML)",
                    "B.Tech. Cyber Security",
                    "B.Tech. Electrical Engineering",
                    "B.Tech. Electronics Engineering",
                    "B.Tech. Mechanical & Smart Manufacturing",
                    "B.Sc. Clinical Psychology",
                    "BBA (Hons./Hons. with Research)",
                    "BCA / BCA (AI & ML / Data Science)"
                ]
            },
            {
                "name": "PG Programmes",
                "items": [
                    "MBA (for Working Professionals)",
                    "M.Sc. Clinical Psychology",
                    "L.L.M.",
                    "M.A. English",
                    "Master of Medical Laboratory Science"
                ]
            },
            {
                "name": "Diploma Programmes",
                "items": [
                    "Diploma in Civil Engineering",
                    "Diploma in Mechanical Engineering",
                    "Diploma in Electrical Engineering",
                    "Diploma in Computer Science & Engineering",
                    "Diploma in Pharmacy",
                    "Diploma in Industrial Electronics"
                ]
            },
            {
                "name": "Other Programmes",
                "items": [
                    "Ph.D. programmes under various streams"
                ]
            }
        ],
        "note": "Course availability, campus, eligibility and duration can vary. Confirm details using the latest official brochure.",
        "links": [
            {
                "label": "Official Programme List",
                "url": "https://svsu.ac.in/programmName.php"
            },
            {
                "label": "Official Website",
                "url": "https://svsu.ac.in/"
            }
        ]
    },

    "admission": {
        "title": "Admission Help",
        "intro": "Admission information for Academic Session 2026-27.",
        "steps": [
            "Open the official SVSU admission website.",
            "Select your preferred programme.",
            "Read the latest admission brochure.",
            "Check eligibility, documents and fees.",
            "Follow the application instructions.",
            "Check official notices for merit lists and counselling updates."
        ],
        "note": "Eligibility, fees and admission dates are programme-specific. Always confirm from the latest official notice.",
        "links": [
            {
                "label": "SVSU Admission Portal",
                "url": "https://admission.svsu.ac.in"
            },
            {
                "label": "SVSU Website",
                "url": "https://svsu.ac.in/"
            },
            {
                "label": "HSTES Counselling",
                "url": "https://www.hstes.org.in/"
            }
        ],
        "email": "admissions@svsu.ac.in",
        "phone": "18001800147"
    },

    "contact": {
        "title": "Contact Support",
        "intro": "Contact information published by Shri Vishwakarma Skill University.",
        "phone": "18001800147",
        "phone_display": "1800 1800 147",
        "other_phones": [
            "+91-124-2746800",
            "9306095464",
            "9253364547",
            "9253224547",
            "9253394547"
        ],
        "email": "info@svsu.ac.in",
        "admission_email": "admissions@svsu.ac.in",
        "address": "Village Dudhola, District Palwal, Haryana, India",
        "transit_address": "Plot No. 147, Sector 44, Gurugram, Haryana, India",
        "links": [
            {
                "label": "Official Contact Page",
                "url": "https://svsu.ac.in/contact-us.php"
            },
            {
                "label": "Official Website",
                "url": "https://svsu.ac.in/"
            }
        ],
        "note": "Confirm office hours and department contact details on the official website."
    }
}


# Load Machine Learning Model
try:
    with open("chatbot_model.pkl", "rb") as file:
        ml_model = pickle.load(file)

    print("Machine Learning model loaded successfully!")

except Exception as error:
    print("Model Loading Error:", error)
    ml_model = None


# Load Intent Responses
try:
    with open("intents.json", "r", encoding="utf-8") as file:
        intents_data = json.load(file)

except Exception as error:
    print("Intent Loading Error:", error)
    intents_data = {"intents": []}


# Machine Learning Response
def get_ml_response(message):

    if ml_model is None:
        return None

    prediction = ml_model.predict([message])[0]

    probabilities = ml_model.predict_proba([message])[0]
    confidence = max(probabilities)

    print("User Question:", message)
    print("Predicted Intent:", prediction)
    print("Confidence:", confidence)

    if confidence < 0.35:
        return None

    for intent in intents_data.get("intents", []):

        if intent.get("tag") == prediction:
            responses = intent.get("responses", [])

            if responses:
                return random.choice(responses)

    return None


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Sidebar Information API
@app.route("/api/portal/<section>", methods=["GET"])
def portal_section(section):

    if section not in PORTAL_INFO:
        return jsonify({
            "success": False,
            "message": "Section not found."
        }), 404

    return jsonify({
        "success": True,
        "data": PORTAL_INFO[section]
    })


# Chat Route
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}

    user_message = str(
        data.get("message", "")
    ).strip()

    if not user_message:
        return jsonify({
            "response": "Please enter your question."
        }), 400

    answer = None

    # First use Machine Learning
    try:
        answer = get_ml_response(user_message.lower())

    except Exception as error:
        print("ML Prediction Error:", error)

    # Keyword-based fallback
    message_lower = user_message.lower()

    if answer is None:

        if "bca" in message_lower:
            answer = college_data["bca"]

        elif "mca" in message_lower:
            answer = college_data["mca"]

        elif "bba" in message_lower:
            answer = college_data["bba"]

        elif "mba" in message_lower:
            answer = college_data["mba"]

        elif "btech" in message_lower or "b.tech" in message_lower:
            answer = college_data["btech"]

        elif "course" in message_lower or "programme" in message_lower:
            answer = college_data["courses"]

        elif "admission" in message_lower or "apply" in message_lower:
            answer = college_data["admission"]

        elif "fee" in message_lower:
            answer = college_data["fees"]

        elif "eligibility" in message_lower or "eligible" in message_lower:
            answer = college_data["eligibility"]

        elif "timing" in message_lower or "office time" in message_lower:
            answer = college_data["timing"]

        elif any(word in message_lower for word in [
            "contact", "phone", "email", "address"
        ]):
            answer = college_data["contact"]

        else:
            answer = (
                "Sorry, I could not understand your question. "
                "Please ask about courses, admission, fees, "
                "eligibility or contact."
            )

    # Save Student Enquiry
    enquiries = read_json_file(ENQUIRIES_FILE, [])

    enquiries.append({
        "question": user_message,
        "answer": answer,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "answered": not answer.startswith(
            "Sorry, I could not understand"
        )
    })

    try:
        write_json_file(ENQUIRIES_FILE, enquiries)

    except OSError as error:
        print("Enquiry Save Error:", error)

    return jsonify({
        "response": answer
    })


# Feedback System
@app.route("/feedback", methods=["POST"])
def feedback():

    data = request.get_json(silent=True) or {}

    feedback_value = data.get("feedback", "")

    if feedback_value not in ["Yes", "No"]:
        return jsonify({
            "success": False,
            "message": "Invalid feedback"
        }), 400

    feedback_data = read_json_file(FEEDBACK_FILE, [])

    feedback_data.append({
        "feedback": feedback_value,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    try:
        write_json_file(FEEDBACK_FILE, feedback_data)

    except OSError as error:
        print("Feedback Save Error:", error)

        return jsonify({
            "success": False,
            "message": "Could not save feedback."
        }), 500

    return jsonify({
        "success": True,
        "message": "Feedback saved successfully"
    })


# ---------------- ADMIN PANEL ----------------

# Admin Login
@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    error_message = ""

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):
            session.clear()
            session["is_admin"] = True
            session["admin_username"] = username

            return redirect(url_for("admin_dashboard"))

        error_message = "Invalid username or password. Please try again."

    return render_template(
        "admin_login.html",
        error=error_message
    )


# Admin Dashboard
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    enquiries = read_json_file(ENQUIRIES_FILE, [])
    feedback_data = read_json_file(FEEDBACK_FILE, [])

    total_enquiries = len(enquiries)

    unanswered_count = sum(
        1 for item in enquiries
        if not item.get("answered", True)
    )

    yes_count = sum(
        1 for item in feedback_data
        if item.get("feedback") == "Yes"
    )

    no_count = sum(
        1 for item in feedback_data
        if item.get("feedback") == "No"
    )

    # Count popular questions
    question_counts = {}

    for item in enquiries:

        question = item.get("question", "").strip()

        if question:
            question_counts[question] = (
                question_counts.get(question, 0) + 1
            )

    popular_questions = sorted(
        question_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )[:5]

    return render_template(
        "admin_dashboard.html",
        total_enquiries=total_enquiries,
        unanswered_count=unanswered_count,
        total_feedback=len(feedback_data),
        yes_count=yes_count,
        no_count=no_count,
        popular_questions=popular_questions,
        recent_enquiries=list(reversed(enquiries[-20:])),
        recent_feedback=list(reversed(feedback_data[-20:]))
    )


# Admin Logout
@app.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():

    session.clear()

    return redirect(url_for("admin_login"))


# Run Flask Application
if __name__ == "__main__":

    print("Chatbot is starting...")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
