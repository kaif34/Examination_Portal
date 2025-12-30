from flask import Blueprint, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

exam_notify_bp = Blueprint('exam_notify_bp', __name__)

def send_email(to_email, subject, body):
    # Replace with your actual email details
    sender_email = "your-email@gmail.com"
    sender_password = "your-app-password"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")

@exam_notify_bp.route('/api/send_exam_notification', methods=['POST'])
def send_exam_notification():
    from app import mysql  # Use your MySQL object from db_config/init_mysql
    data = request.get_json()
    exam_id = data.get("exam_id")

    try:
        cur = mysql.connection.cursor()
        # Get exam info
        cur.execute("SELECT Exam_Title, Start_DateTime FROM Entrance_Exam WHERE Exam_ID = %s", (exam_id,))
        exam = cur.fetchone()
        if not exam:
            return jsonify({"error": "Exam not found"}), 404

        exam_title, start_time = exam

        # Get all applicants' emails
        cur.execute("SELECT Email, Full_Name FROM applicants")
        students = cur.fetchall()

        for email, name in students:
            body = f"Dear {name},\n\nYour exam '{exam_title}' is scheduled on {start_time}.\n\nGood luck!"
            send_email(email, f"Exam Notification - {exam_title}", body)

        return jsonify({"message": "Notifications sent to all applicants."})
    except Exception as e:
        print(e)
        return jsonify({"error": "Something went wrong."}), 500
