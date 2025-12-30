from flask import Blueprint, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import MySQLdb.cursors

def create_send_email_routes(mysql):
    send_email_bp = Blueprint('send_email', __name__)

    @send_email_bp.route('/api/send_exam_emails', methods=['POST'])
    def send_exam_emails():
        data = request.get_json()
        exam = data.get("exam", {})
        applicants = data.get("applicants", [])

        try:
            sender_email = "examinationportal2025@gmail.com"
            sender_password = "zwdp rwro piku dwib"
            subject = f"Exam Assignment: {exam['Exam_Name']}"

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            for applicant in applicants:
                email = applicant.get("Email")

                # Fetch full applicant data from DB by email
                cursor.execute("SELECT Full_Name, Email, Password FROM applicants WHERE Email = %s", (email,))
                db_applicant = cursor.fetchone()

                if not db_applicant:
                    print(f"⚠️ Applicant with email {email} not found.")
                    continue

                full_name = db_applicant['Full_Name']
                receiver_email = db_applicant['Email']
                password = db_applicant['Password']

                body = f"""Dear {full_name},

You have been assigned the following exam:

Exam ID: {exam['Exam_Id']}
Exam Name: {exam['Exam_Name']}
Date: {exam['Exam_Date']}
Time: {exam['Exam_Time']}

Your login credentials:
Email: {receiver_email}
Password: {password}

Good luck!

Best regards,
Examination Team
"""

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

                # Send email
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, msg.as_string())

            return jsonify({'success': True, 'message': 'Emails sent successfully!'})

        except Exception as e:
            print("❌ Email sending error:", e)
            return jsonify({'success': False, 'message': f'Failed to send emails: {str(e)}'}), 500

    return send_email_bp
