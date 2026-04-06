from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
import threading

app = Flask(__name__)
CORS(app)

# 🔁 Doctors Data
def get_doctors_data():
    return [
        {"name": "Dr. Arjun", "specialty": "Cardiology", "hospital": "Apollo Hospital", "slots": ["10","11","14"]},
        {"name": "Dr. Kavya", "specialty": "Cardiology", "hospital": "Fortis Hospital", "slots": ["12","15"]},
        {"name": "Dr. Rahul", "specialty": "Neurology", "hospital": "AIIMS", "slots": ["10","13"]},
        {"name": "Dr. Sneha", "specialty": "Orthopedic", "hospital": "Manipal Hospital", "slots": ["11","16"]},
        {"name": "Dr. Meena", "specialty": "General Medicine", "hospital": "Care Hospital", "slots": ["9","10","15"]},
        {"name": "Dr. Ramesh", "specialty": "Dermatology", "hospital": "Apollo Hospital", "slots": ["14","15"]}
    ]

# 🧠 Disease → Specialty
def get_specialty(disease):
    mapping = {
        "Hypertension": "Cardiology",
        "Heart Attack": "Cardiology",
        "Stroke": "Neurology",
        "Migraine": "Neurology",
        "Arthritis": "Orthopedic",
        "Back Pain": "Orthopedic",
        "Skin Allergy": "Dermatology",
        "Acne": "Dermatology",
        "Depression": "Psychiatry",
        "Anxiety": "Psychiatry",
        "Diabetes": "General Medicine",
        "Fever": "General Medicine"
    }
    return mapping.get(disease, "General Medicine")

# 🔍 Get Doctors
@app.route("/get_doctors", methods=["POST"])
def get_doctors():
    doctors = get_doctors_data()
    disease = request.json.get("disease", "")
    specialty = get_specialty(disease)

    result = [doc for doc in doctors if doc["specialty"] == specialty]
    return jsonify(result)

# 📧 SEND EMAIL (BACKGROUND)
def send_email(patient, email, doctor, hospital, date, time):
    try:
        print("📧 Trying to send email...")

        sender_email = "smart.hospital.booking@gmail.com"
        app_password = "pvfjxefiostedobg"

        msg = MIMEText(f"""
Dear {patient},

Warm Greetings from Smart Hospital Network.

Your appointment has been successfully confirmed.

-----------------------------------------
Doctor   : {doctor}
Hospital : {hospital}
Date     : {date}
Time     : {time}:00
-----------------------------------------

Kindly arrive 10-15 minutes early.

Stay safe & take care.

Regards,  
Smart Hospital Team
""")

        msg["Subject"] = "Appointment Confirmation"
        msg["From"] = sender_email
        msg["To"] = email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()

        print("✅ Email sent successfully")

    except Exception as e:
        print("❌ EMAIL ERROR:", e)

# 📅 BOOK APPOINTMENT
@app.route("/book", methods=["POST"])
def book():
    data = request.json

    patient = data.get("patient")
    email = data.get("email")
    doctor = data.get("doctor")
    hospital = data.get("hospital")
    date = data.get("date")
    time = str(data.get("time")).strip()

    if not patient or not email:
        return jsonify({"reply": "⚠ Please enter all details properly"})

    doctors = get_doctors_data()

    for doc in doctors:
        if doc["name"] == doctor and time in doc["slots"]:

            # 🚀 send email in background
            threading.Thread(
                target=send_email,
                args=(patient, email, doctor, hospital, date, time)
            ).start()

            return jsonify({
                "reply": f"""🙏 Thank you {patient}!

✅ Appointment Confirmed  
👨‍⚕️ {doctor}  
🏥 {hospital}  
📅 {date}  
⏰ {time}:00  

📧 Confirmation sent to your email  

🛡️ Stay safe & take care!"""
            })

    return jsonify({"reply": "❌ Selected slot not available"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)