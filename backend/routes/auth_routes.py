from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
import jwt
from functools import wraps

SECRET_KEY = "SecretKeyKYKI786"

def create_auth_routes(mysql):
    auth_bp = Blueprint('auth', __name__)
    
    # ---------- JWT TOKEN VERIFICATION DECORATOR ----------
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            # Tokens are expected in Authorization header as: Bearer <token>
            if 'Authorization' in request.headers:
                try:
                    token = request.headers['Authorization'].split(" ")[1]
                except IndexError:
                    return jsonify({'message': 'Token format is invalid!'}), 401

            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                current_user = {
                    'email': data['email'],
                    'role': data['role']
                }
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token expired! Please login again.'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Invalid token!'}), 401

            return f(current_user, *args, **kwargs)
        return decorated

    @auth_bp.route('/login', methods=['POST'])
    def login():
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        # We no longer get 'role' from the request. We detect it.
        
        cursor = mysql.connection.cursor()
        
        user_found = None
        role = None
        user_id = None
        user_name = None
        db_email = None

        # --- 1. CHECK ADMIN TABLE ---
        if not user_found:
            cursor.execute("SELECT Admin_ID, Name, Email, Password FROM Mst_Admin WHERE Email = %s", (email,))
            admin = cursor.fetchone()
            if admin and admin[3] == password: # Check password
                user_found = True
                role = "Admin"
                user_id = admin[0]
                user_name = admin[1]
                db_email = admin[2]

        # --- 2. CHECK FACULTY TABLE (if not found yet) ---
        if not user_found:
            cursor.execute("SELECT Faculty_Id, F_Name, F_Email, Password FROM Mst_Faculty WHERE F_Email = %s", (email,))
            faculty = cursor.fetchone()
            if faculty and faculty[3] == password:
                user_found = True
                role = "Faculty"
                user_id = faculty[0]
                user_name = faculty[1]
                db_email = faculty[2]

        # --- 3. CHECK STUDENT/APPLICANT TABLE (if not found yet) ---
        if not user_found:
            cursor.execute("SELECT Applicant_Id, Full_Name, Email, Password FROM Applicants WHERE Email = %s", (email,))
            student = cursor.fetchone()
            if student and student[3] == password:
                user_found = True
                role = "Student"
                user_id = student[0]
                user_name = student[1]
                db_email = student[2]

        # --- 4. PROCESS LOGIN IF USER FOUND ---
        if user_found:
            # Explicitly insert login time as NOW
            login_time = datetime.now()
            insert_log_query = """
                INSERT INTO login_log (User_Email, Role, Login_Time)
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_log_query, (db_email, role, login_time))
            mysql.connection.commit()
            
            # Generate JWT token (valid 2 hours)
            token = jwt.encode({
                'email': db_email,
                'role': role,
                'exp': datetime.now(timezone.utc) + timedelta(hours=2)
            }, SECRET_KEY, algorithm="HS256")

            # Construct Response
            response_data = {
                'status': 'success',
                'token': token,
                'role': role,
                'name': user_name,
                'email': db_email,
                'login_time': login_time.strftime('%Y-%m-%d %H:%M:%S')
            }

            # Add ID if it is a student (Frontend requirement)
            if role == "Student":
                response_data['id'] = user_id
            
            cursor.close()
            return jsonify(response_data), 200

        cursor.close()
        return jsonify({'status': 'fail', 'message': 'Invalid credentials'}), 401

    @auth_bp.route('/logout', methods=['POST'])
    def logout():
        data = request.json
        email = data.get('email')
        role = data.get('role')

        try:
            cursor = mysql.connection.cursor()
            # Update only latest login record for this user
            update_query = """
                UPDATE login_log
                SET Logout_Time = %s
                WHERE Log_ID = (
                    SELECT Log_ID FROM (
                        SELECT Log_ID
                        FROM login_log
                        WHERE User_Email = %s AND Role = %s
                        ORDER BY Log_ID DESC
                        LIMIT 1
                    ) AS sub
                )
            """
            cursor.execute(update_query, (datetime.now(), email, role))
            mysql.connection.commit()
            return jsonify({'success': True, 'message': 'Logout time recorded'})
        except Exception as e:
            print("Error in logout route:", e)
            return jsonify({'success': False, 'message': 'Logout logging failed'}), 500
        
    # ---------- SAMPLE PROTECTED ROUTE ----------
    @auth_bp.route('/verify-token', methods=['GET'])
    @token_required
    def verify_token(current_user):
        return jsonify({
            'status': 'valid',
            'user': current_user
        }), 200

    return auth_bp