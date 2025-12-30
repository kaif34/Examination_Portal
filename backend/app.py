import os
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from dotenv import load_dotenv  # Import dotenv
from db_config import init_mysql

# --- Route Imports ---
from routes.auth_routes import create_auth_routes 
from routes.question_routes import create_question_routes
from routes.exam_routes import create_exam_routes
from routes.admin_routes import create_admin_routes
from routes.ExamNotification import exam_notify_bp
from routes.applicants import create_applicants_bp
from routes.AddApplicants_exam import create_add_applicants_exam_bp
from routes.assign_applicants import create_assign_routes
from routes.send_exam_email import create_send_email_routes
from routes.assigned_applicants_routes import create_assigned_applicants_routes
from routes.exam_paper_routes import create_exam_paper_routes
from routes.student_routes import create_student_routes
from routes.AddStudents import create_add_students_bp
from routes.faculty_routes import create_faculty_routes
from routes.ViewResponses import create_view_responses_bp
from routes.ViewAnswers import create_view_answers_bp

# 1. Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# 2. Initialize MySQL 
# (This now uses the updated db_config.py to read from .env)
mysql = init_mysql(app)

# 3. Mail Configuration (Reads from .env)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)

# --- Register Blueprints ---

# Auth & Admin
app.register_blueprint(create_auth_routes(mysql), url_prefix="/api/auth")
app.register_blueprint(create_admin_routes(mysql), url_prefix='/api/admin')

# Questions & Exams
app.register_blueprint(create_question_routes(mysql), url_prefix="/api/questions")
app.register_blueprint(create_exam_routes(mysql), url_prefix="/api/exam")
exam_paper_bp = create_exam_paper_routes(mysql)
app.register_blueprint(exam_paper_bp, url_prefix="/api/paper")

# Students & Faculty
app.register_blueprint(create_add_students_bp(mysql), url_prefix="/api")
app.register_blueprint(create_faculty_routes(mysql), url_prefix='/api/faculty')
student_bp = create_student_routes(mysql)
app.register_blueprint(student_bp, url_prefix="/api/student")

# Responses & Answers
app.register_blueprint(create_view_responses_bp(mysql), url_prefix='/responses')
app.register_blueprint(create_view_answers_bp(mysql))

# Notifications & Emails
app.register_blueprint(exam_notify_bp)
app.register_blueprint(create_send_email_routes(mysql))

# Applicants & Assignments
app.register_blueprint(create_add_applicants_exam_bp(mysql), url_prefix='/api')
app.register_blueprint(create_assign_routes(mysql))
app.register_blueprint(create_applicants_bp(mysql))
app.register_blueprint(create_assigned_applicants_routes(mysql))


if __name__ == "__main__":
    # Get port from .env, default to 5001
    port = int(os.getenv('PORT', 5001))
    app.run(debug=True, port=port)