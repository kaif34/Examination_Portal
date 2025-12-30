from flask import Blueprint, request, jsonify
import MySQLdb.cursors
from functools import wraps
import jwt
from routes.auth_routes import SECRET_KEY  # Replace with your JWT secret key

def create_faculty_routes(mysql):
    faculty_bp = Blueprint("faculty_bp", __name__)

    # -------------------------
    # JWT Token decorator
    # -------------------------
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = { "email": data["email"], "role": data["role"] }
            token = None
            if "Authorization" in request.headers:
                auth_header = request.headers["Authorization"]
                token = auth_header.split(" ")[1] if " " in auth_header else auth_header

            if not token:
                return jsonify({"success": False, "message": "Token is missing!"}), 401

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                request.faculty_email = data["email"]
            except Exception as e:
                return jsonify({"success": False, "message": f"Token is invalid: {str(e)}"}), 401

            return f(current_user, *args, **kwargs)
        return decorated

    # -------------------------
    # Faculty Login
    # -------------------------
    @faculty_bp.route("/login", methods=["POST"])
    def faculty_login():
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM Mst_Faculty WHERE F_Email = %s", (email,))
            faculty = cursor.fetchone()
            cursor.close()

            if not faculty:
                return jsonify({"success": False, "message": "Faculty not found"}), 404

            # Plain text password check (insecure, consider hashing)
            if faculty["F_Password"] == password:
                token = jwt.encode({"email": faculty["F_Email"]}, SECRET_KEY, algorithm="HS256")
                return jsonify({
                    "success": True,
                    "token": token,
                    "faculty": {
                        "id": faculty["F_ID"],
                        "name": faculty["F_Name"],
                        "email": faculty["F_Email"]
                    }
                })
            else:
                return jsonify({"success": False, "message": "Invalid password"}), 401

        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    # -------------------------
    # Faculty Profile
    # -------------------------
    @faculty_bp.route("/profile", methods=["GET"])
    @token_required
    def get_faculty_profile(current_user):
        email = current_user["email"]
        if current_user["role"] != "Faculty":
            return jsonify({"message": "Unauthorized"}), 403
        
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT F_ID, F_Name, F_Email FROM Mst_Faculty WHERE F_Email = %s", (email,))
            faculty = cursor.fetchone()
            cursor.close()

            if faculty:
                return jsonify({"success": True, "faculty": faculty})
            else:
                return jsonify({"success": False, "message": "Faculty not found"}), 404

        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500


    # -------------------------
    # Conducted Exams by Faculty Email (without token)
    # -------------------------
    @faculty_bp.route("/conducted_exams/<faculty_email>", methods=["GET"])
    def get_conducted_exams_by_email(faculty_email):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = """
                SELECT 
                    ee.Exam_Id,
                    ee.Exam_Name,
                    ee.Exam_Date,
                    COUNT(DISTINCT aea.Applicant_Id) AS total_applicants,
                    COALESCE(attempts.attempted_applicants, 0) AS attempted_applicants
                FROM Entrance_Exam ee
                LEFT JOIN applicant_exam_assign aea ON ee.Exam_Id = aea.Exam_Id
                LEFT JOIN (
                    SELECT ep.Exam_Id, COUNT(DISTINCT aa.Applicant_Id) AS attempted_applicants
                    FROM exam_paper ep
                    JOIN applicant_attempt aa ON ep.Exam_Paper_Id = aa.Exam_Paper_Id
                    WHERE aa.Status = 'Submitted'
                    GROUP BY ep.Exam_Id
                ) AS attempts ON ee.Exam_Id = attempts.Exam_Id
                WHERE ee.faculty_email = %s
                  AND TIMESTAMP(ee.Exam_Date, ee.Exam_Time) + INTERVAL ee.Duration_Minutes MINUTE <= NOW()
                GROUP BY ee.Exam_Id, ee.Exam_Name, ee.Exam_Date, attempts.attempted_applicants
                ORDER BY ee.Exam_Date DESC
            """
            cursor.execute(query, (faculty_email,))
            exams = cursor.fetchall()
            cursor.close()

            return jsonify({"success": True, "exams": exams})

        except Exception as e:
            print("Error fetching conducted exams:", e)
            return jsonify({"success": False, "message": str(e)}), 500
    
    
    
    # -------------------------
    # Conducted Exams with Applicant Attempts
    # -------------------------
    @faculty_bp.route("/conducted_exams", methods=["GET"])
    @token_required
    def get_conducted_exams():
        faculty_email = request.faculty_email
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = """
                SELECT 
                    ee.Exam_Id,
                    ee.Exam_Name,
                    ee.Exam_Date,
                    COUNT(DISTINCT aea.Applicant_Id) AS total_applicants,
                    COALESCE(attempts.attempted_applicants, 0) AS attempted_applicants
                FROM Entrance_Exam ee
                LEFT JOIN applicant_exam_assign aea ON ee.Exam_Id = aea.Exam_Id
                LEFT JOIN (
                    SELECT ep.Exam_Id, COUNT(DISTINCT aa.Applicant_Id) AS attempted_applicants
                    FROM exam_paper ep
                    JOIN applicant_attempt aa ON ep.Exam_Paper_Id = aa.Exam_Paper_Id
                    WHERE aa.Status = 'Submitted'
                    GROUP BY ep.Exam_Id
                ) AS attempts ON ee.Exam_Id = attempts.Exam_Id
                WHERE ee.faculty_email = %s
                GROUP BY ee.Exam_Id, ee.Exam_Name, ee.Exam_Date, attempts.attempted_applicants
                ORDER BY ee.Exam_Date DESC
            """
            cursor.execute(query, (faculty_email,))
            exams = cursor.fetchall()
            cursor.close()

            return jsonify({"success": True, "exams": exams})

        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    # -------------------------
    # Exam Applicants Statistics
    # -------------------------
    @faculty_bp.route("/exam_applicants_stats", methods=["GET"])
    @token_required
    def get_exam_applicants_stats():
        faculty_email = request.faculty_email
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = """
                SELECT 
                    ee.Exam_Id,
                    ee.Exam_Name,
                    COUNT(DISTINCT aea.Applicant_Id) AS total_applicants,
                    COALESCE(attempts.attempted_applicants, 0) AS attempted_applicants
                FROM Entrance_Exam ee
                LEFT JOIN applicant_exam_assign aea ON ee.Exam_Id = aea.Exam_Id
                LEFT JOIN (
                    SELECT ep.Exam_Id, COUNT(DISTINCT aa.Applicant_Id) AS attempted_applicants
                    FROM exam_paper ep
                    JOIN applicant_attempt aa ON ep.Exam_Paper_Id = aa.Exam_Paper_Id
                    WHERE aa.Status = 'Submitted'
                    GROUP BY ep.Exam_Id
                ) AS attempts ON ee.Exam_Id = attempts.Exam_Id
                WHERE ee.faculty_email = %s
                GROUP BY ee.Exam_Id, ee.Exam_Name, attempts.attempted_applicants
                ORDER BY ee.Exam_Name
            """
            cursor.execute(query, (faculty_email,))
            stats = cursor.fetchall()
            cursor.close()

            return jsonify({"success": True, "stats": stats})

        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    return faculty_bp
