from flask import Blueprint, request, jsonify
import pandas as pd
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import pytz

def create_admin_routes(mysql):
    admin_bp = Blueprint('admin_routes', __name__)
    def convert_to_ist(dt):
        if dt is None:
            return None
        utc = pytz.utc
        ist = pytz.timezone('Asia/Kolkata')
        utc_dt = utc.localize(dt)
        ist_dt = utc_dt.astimezone(ist)
        return ist_dt.strftime('%Y-%m-%d %H:%M:%S')

    # ID Management Route
    @admin_bp.route('/reorganize-ids', methods=['POST'])
    def reorganize_ids():
        try:
            cursor = mysql.connection.cursor()
        
            # Execute the comprehensive reorganization script
            with open('scripts/reorganize_ids_complete.sql', 'r') as file:
                sql_script = file.read()
        
            # Split and execute each statement
            statements = sql_script.split(';')
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
        
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "All IDs reorganized successfully in perfect sequential order (1,2,3,4...)", "status": "complete"}), 200
        except Exception as e:
            print("Error reorganizing IDs:", e)
            mysql.connection.rollback()
            return jsonify({"error": f"Unable to reorganize IDs: {str(e)}"}), 500

    # ID Gap Detection Route
    @admin_bp.route('/check-id-gaps', methods=['GET'])
    def check_id_gaps():
        try:
            cursor = mysql.connection.cursor()
            gaps_report = {}
        
            # Check each table for gaps including all discovered tables
            tables = [
                ('mst_school', 'School_Id'),
                ('mst_faculty', 'Faculty_Id'),
                ('applicants', 'Applicant_Id'),
                ('applicant_attempt', 'Attempt_Id'),
                ('mst_admin', 'Admin_ID'),
                ('login_log', 'Log_ID')
            ]
        
            # Check if additional tables exist and add them
            cursor.execute("SHOW TABLES LIKE 'auto_grading'")
            if cursor.fetchone():
                tables.append(('auto_grading', 'Grading_Id'))
            
            cursor.execute("SHOW TABLES LIKE 'applicant_exam_assign'")
            if cursor.fetchone():
                tables.append(('applicant_exam_assign', 'Assign_ID'))
            
            cursor.execute("SHOW TABLES LIKE 'applicant_answers'")
            if cursor.fetchone():
                # Note: applicant_answers doesn't have its own ID, it references Attempt_Id
                pass
        
            for table_name, id_column in tables:
                try:
                    cursor.execute(f"""
                        SELECT 
                            COUNT(*) as total_records,
                            COALESCE(MIN({id_column}), 0) as min_id,
                            COALESCE(MAX({id_column}), 0) as max_id,
                            CASE WHEN COUNT(*) = 0 THEN 0 
                                 ELSE (COALESCE(MAX({id_column}), 0) - COALESCE(MIN({id_column}), 0) + 1) 
                            END as expected_count,
                            CASE WHEN COUNT(*) = 0 THEN 0 
                                 ELSE ((COALESCE(MAX({id_column}), 0) - COALESCE(MIN({id_column}), 0) + 1) - COUNT(*)) 
                            END as gaps
                        FROM {table_name}
                    """)
                    result = cursor.fetchone()
                
                    if result:
                        gaps_report[table_name] = {
                            'total_records': result[0],
                            'min_id': result[1],
                            'max_id': result[2],
                            'expected_count': result[3],
                            'gaps': result[4],
                            'has_gaps': result[4] > 0,
                            'status': 'Perfect Order' if result[4] == 0 and result[0] > 0 else ('Empty' if result[0] == 0 else 'Has Gaps')
                        }
                except Exception as table_error:
                    gaps_report[table_name] = {
                        'error': f"Unable to check table: {str(table_error)}"
                    }
        
            cursor.close()
            return jsonify(gaps_report), 200
        except Exception as e:
            print("Error checking ID gaps:", e)
            return jsonify({"error": "Unable to check ID gaps"}), 500

    # Faculty Routes
    @admin_bp.route('/faculty', methods=['GET'])
    def get_faculty():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT Faculty_Id, F_Name, F_Email, School_Id, Designation, Password 
                FROM mst_faculty 
                ORDER BY Faculty_Id
            """)
            faculty = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in faculty]
            cursor.close()
            return jsonify(result), 200
        except Exception as e:
            print("Error fetching faculty:", e)
            return jsonify({"error": "Unable to fetch faculty"}), 500

    @admin_bp.route('/faculty', methods=['POST'])
    def add_faculty():
        try:
            data = request.get_json()
            cursor = mysql.connection.cursor()
            
            # --- START CHANGE: Check for duplicate email ---
            cursor.execute("SELECT COUNT(*) FROM mst_faculty WHERE F_Email = %s", (data['F_Email'],))
            if cursor.fetchone()[0] > 0:
                cursor.close()
                return jsonify({"error": "A faculty member with this email already exists."}), 400
            # --- END CHANGE ---
            
            # Check for duplicate email
            cursor.execute("SELECT COUNT(*) FROM mst_faculty WHERE F_Email = %s", (data['F_Email'],))
            if cursor.fetchone()[0] > 0:
                cursor.close()
                return jsonify({"error": "A faculty member with this email already exists."}), 400
            
            cursor.execute("""
                INSERT INTO mst_faculty (F_Name, F_Email, School_Id, Designation, Password)
                VALUES (%s, %s, %s, %s, %s)
            """, (data['F_Name'], data['F_Email'], data['School_Id'], data['Designation'], data['Password']))
            
            mysql.connection.commit()
            faculty_id = cursor.lastrowid
            cursor.close()
            return jsonify({"message": "Faculty added successfully", "Faculty_Id": faculty_id}), 201
        except Exception as e:
            print("Error adding faculty:", e)
            # --- START CHANGE: Catch DB-level duplicate error ---
            if 'Duplicate entry' in str(e) and 'F_Email' in str(e):
                return jsonify({"error": "A faculty member with this email already exists."}), 400
            # --- END CHANGE ---
            return jsonify({"error": "Unable to add faculty"}), 500

    @admin_bp.route('/faculty/<int:faculty_id>', methods=['PUT'])
    def update_faculty(faculty_id):
        try:
            data = request.get_json()
            cursor = mysql.connection.cursor()
            
            # Updated query to include Password
            cursor.execute("""
                UPDATE mst_faculty 
                SET F_Name = %s, F_Email = %s, School_Id = %s, Designation = %s, Password = %s
                WHERE Faculty_Id = %s
            """, (data['F_Name'], data['F_Email'], data['School_Id'], data['Designation'], data['Password'], faculty_id))
            
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Faculty updated successfully"}), 200
        except Exception as e:
            print("Error updating faculty:", e)
            return jsonify({"error": "Unable to update faculty"}), 500

    @admin_bp.route('/faculty/<int:faculty_id>', methods=['DELETE'])
    def delete_faculty(faculty_id):
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM mst_faculty WHERE Faculty_Id = %s", (faculty_id,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Faculty deleted successfully"}), 200
        except Exception as e:
            print("Error deleting faculty:", e)
            return jsonify({"error": "Unable to delete faculty"}), 500

    # Schools Routes
    @admin_bp.route('/schools', methods=['GET'])
    def get_schools():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT School_Id, School_Name, School_Short FROM mst_school ORDER BY School_Id")
            schools = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in schools]
            cursor.close()
            return jsonify(result), 200
        except Exception as e:
            print("Error fetching schools:", e)
            return jsonify({"error": "Unable to fetch schools"}), 500

    @admin_bp.route('/schools', methods=['POST'])
    def add_school():
        try:
            data = request.get_json()
            cursor = mysql.connection.cursor()
            
            # --- START CHANGE: Check for duplicate School_Name or School_Short ---
            cursor.execute("SELECT School_Name, School_Short FROM mst_school WHERE School_Name = %s OR School_Short = %s", 
                           (data['School_Name'], data['School_Short']))
            existing = cursor.fetchone()
            if existing:
                cursor.close()
                if existing[0] == data['School_Name']:
                    return jsonify({"error": "A school with this name already exists."}), 400
                if existing[1] == data['School_Short']:
                    return jsonify({"error": "A school with this short name already exists."}), 400
            # --- END CHANGE ---
            
            cursor.execute("SELECT School_Name, School_Short FROM mst_school WHERE School_Name = %s OR School_Short = %s", 
                           (data['School_Name'], data['School_Short']))
            existing = cursor.fetchone()
            if existing:
                cursor.close()
                if existing[0] == data['School_Name']:
                    return jsonify({"error": "A school with this name already exists."}), 400
                if existing[1] == data['School_Short']:
                    return jsonify({"error": "A school with this short name already exists."}), 400
            
            cursor.execute("""
                INSERT INTO mst_school (School_Name, School_Short)
                VALUES (%s, %s)
            """, (data['School_Name'], data['School_Short']))
            
            mysql.connection.commit()
            school_id = cursor.lastrowid
            cursor.close()
            return jsonify({"message": "School added successfully", "School_Id": school_id}), 201
        except Exception as e:
            print("Error adding school:", e)
            return jsonify({"error": "Unable to add school"}), 500

    @admin_bp.route('/schools/<int:school_id>', methods=['PUT'])
    def update_school(school_id):
        try:
            data = request.get_json()
            cursor = mysql.connection.cursor()
            
            cursor.execute("""
                UPDATE mst_school 
                SET School_Name = %s, School_Short = %s
                WHERE School_Id = %s
            """, (data['School_Name'], data['School_Short'], school_id))
            
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "School updated successfully"}), 200
        except Exception as e:
            print("Error updating school:", e)
            return jsonify({"error": "Unable to update school"}), 500

    @admin_bp.route('/schools/<int:school_id>', methods=['DELETE'])
    def delete_school(school_id):
        try:
            cursor = mysql.connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM mst_faculty WHERE School_Id = %s", (school_id,))
            faculty_count = cursor.fetchone()[0]
            
            if faculty_count > 0:
                cursor.close()
                return jsonify({"error": f"Cannot delete school. {faculty_count} faculty members are associated with this school."}), 400
            
            cursor.execute("DELETE FROM mst_school WHERE School_Id = %s", (school_id,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "School deleted successfully"}), 200
        except Exception as e:
            print("Error deleting school:", e)
            return jsonify({"error": "Unable to delete school"}), 500

    # Applicants Routes
    @admin_bp.route('/applicants', methods=['GET'])
    def get_applicants():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT Applicant_Id, Full_Name, Email, Phone, DOB, Gender, Address, Registration_Date
                FROM applicants 
                ORDER BY Applicant_Id
            """)
            applicants = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in applicants]
            cursor.close()
            return jsonify(result), 200
        except Exception as e:
            print("Error fetching applicants:", e)
            return jsonify({"error": "Unable to fetch applicants"}), 500

    @admin_bp.route('/applicants/<int:applicant_id>', methods=['DELETE'])
    def delete_applicant(applicant_id):
        try:
            cursor = mysql.connection.cursor()
        
            # Get all attempt IDs for this applicant
            cursor.execute("SELECT Attempt_Id FROM applicant_attempt WHERE Applicant_Id = %s", (applicant_id,))
            attempt_ids = [row[0] for row in cursor.fetchall()]
        
            # Delete from applicant_answers table first
            answers_deleted = 0
            if attempt_ids:
                for attempt_id in attempt_ids:
                    cursor.execute("SELECT COUNT(*) FROM applicant_answers WHERE Attempt_Id = %s", (attempt_id,))
                    answer_count = cursor.fetchone()[0]
                    if answer_count > 0:
                        cursor.execute("DELETE FROM applicant_answers WHERE Attempt_Id = %s", (attempt_id,))
                        answers_deleted += answer_count
        
            # Delete related records
            cursor.execute("SELECT COUNT(*) FROM applicant_attempt WHERE Applicant_Id = %s", (applicant_id,))
            attempt_count = cursor.fetchone()[0]
        
            if attempt_count > 0:
                cursor.execute("DELETE FROM applicant_attempt WHERE Applicant_Id = %s", (applicant_id,))
        
            # Delete from auto_grading table
            try:
                if attempt_ids:
                    cursor.execute("DELETE FROM auto_grading WHERE Attempt_Id IN (%s)" % ','.join(['%s'] * len(attempt_ids)), attempt_ids)
            except Exception as e:
                pass
        
            # Delete from applicant_exam_assign table
            try:
                cursor.execute("DELETE FROM applicant_exam_assign WHERE Applicant_Id = %s", (applicant_id,))
            except Exception as e:
                pass
        
            # Delete from login_log table by User_Email
            cursor.execute("SELECT Email FROM applicants WHERE Applicant_Id = %s", (applicant_id,))
            row = cursor.fetchone()
            applicant_email = row[0] if row else None

            log_count = 0
            if applicant_email:
                cursor.execute("SELECT COUNT(*) FROM login_log WHERE User_Email = %s", (applicant_email,))
                log_count = cursor.fetchone()[0]
                if log_count > 0:
                    cursor.execute("DELETE FROM login_log WHERE User_Email = %s", (applicant_email,))
            
            # Finally delete the applicant
            cursor.execute("DELETE FROM applicants WHERE Applicant_Id = %s", (applicant_id,))
        
            mysql.connection.commit()
            cursor.close()
        
            message = f"Applicant deleted successfully"
            details = []
            if answers_deleted > 0:
                details.append(f"{answers_deleted} exam answers")
            if attempt_count > 0:
                details.append(f"{attempt_count} exam attempts")
            if log_count > 0:
                details.append(f"{log_count} login logs")
        
            if details:
                message += f" (also removed {', '.join(details)})"
        
            return jsonify({"message": message}), 200
        except Exception as e:
            print("Error deleting applicant:", e)
            mysql.connection.rollback()
            return jsonify({"error": f"Unable to delete applicant: {str(e)}"}), 500

    # Exam Attempts Routes
    @admin_bp.route('/attempts', methods=['GET'])
    def get_attempts():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT Attempt_Id, Applicant_Id, Exam_Paper_Id, Start_Time, End_Time, Status,
                       Security_Violations, Screen_Log, Fullscreen_Mode, Browser_Info,
                       Submission_Type, Termination_Reason, Escape_Key_Violations,
                       Lockdown_Mode, Fullscreen_Exit_Attempts, Fullscreen_Lock_Mode,
                       Keyboard_Violations
                FROM applicant_attempt 
                ORDER BY Attempt_Id
            """)
            attempts = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in attempts]
            cursor.close()
            return jsonify(result), 200
        except Exception as e:
            print("Error fetching attempts:", e)
            return jsonify({"error": "Unable to fetch attempts"}), 500

    @admin_bp.route('/attempts', methods=['POST'])
    def add_attempt():
        try:
            data = request.get_json()
            cursor = mysql.connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM applicants WHERE Applicant_Id = %s", (data['Applicant_Id'],))
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return jsonify({"error": "Applicant not found"}), 400
            
            cursor.execute("""
                INSERT INTO applicant_attempt (
                    Applicant_Id, Exam_Paper_Id, Status, Security_Violations,
                    Screen_Log, Fullscreen_Mode, Browser_Info, Submission_Type,
                    Termination_Reason, Escape_Key_Violations, Lockdown_Mode,
                    Fullscreen_Exit_Attempts, Fullscreen_Lock_Mode, Keyboard_Violations
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['Applicant_Id'], data['Exam_Paper_Id'], data['Status'],
                data['Security_Violations'], data.get('Screen_Log', ''),
                data.get('Fullscreen_Mode', 1), data.get('Browser_Info', ''),
                data['Submission_Type'], data.get('Termination_Reason', ''),
                data.get('Escape_Key_Violations', 0), data.get('Lockdown_Mode', 1),
                data.get('Fullscreen_Exit_Attempts', 0), data.get('Fullscreen_Lock_Mode', 1),
                data.get('Keyboard_Violations', 0)
            ))
            
            mysql.connection.commit()
            attempt_id = cursor.lastrowid
            cursor.close()
            return jsonify({"message": "Attempt added successfully", "Attempt_Id": attempt_id}), 201
        except Exception as e:
            print("Error adding attempt:", e)
            return jsonify({"error": f"Unable to add attempt: {str(e)}"}), 500

    @admin_bp.route('/attempts/<int:attempt_id>', methods=['PUT'])
    def update_attempt(attempt_id):
        try:
            data = request.get_json()
            cursor = mysql.connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM applicants WHERE Applicant_Id = %s", (data['Applicant_Id'],))
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return jsonify({"error": "Applicant not found"}), 400
            
            cursor.execute("""
                UPDATE applicant_attempt 
                SET Applicant_Id = %s, Exam_Paper_Id = %s, Status = %s,
                    Security_Violations = %s, Submission_Type = %s,
                    Termination_Reason = %s, Escape_Key_Violations = %s,
                    Fullscreen_Exit_Attempts = %s, Keyboard_Violations = %s
                WHERE Attempt_Id = %s
            """, (
                data['Applicant_Id'], data['Exam_Paper_Id'], data['Status'],
                data['Security_Violations'], data['Submission_Type'],
                data.get('Termination_Reason', ''), data.get('Escape_Key_Violations', 0),
                data.get('Fullscreen_Exit_Attempts', 0), data.get('Keyboard_Violations', 0),
                attempt_id
            ))
            
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Attempt updated successfully"}), 200
        except Exception as e:
            print("Error updating attempt:", e)
            return jsonify({"error": f"Unable to update attempt: {str(e)}"}), 500

    @admin_bp.route('/attempts/<int:attempt_id>', methods=['DELETE'])
    def delete_attempt(attempt_id):
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM applicant_attempt WHERE Attempt_Id = %s", (attempt_id,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Attempt deleted successfully"}), 200
        except Exception as e:
            print("Error deleting attempt:", e)
            return jsonify({"error": f"Unable to delete attempt: {str(e)}"}), 500

    # Admin Management Routes
    @admin_bp.route('/admins', methods=['GET'])
    def get_admins():
        try:
            cursor = mysql.connection.cursor()
            # Added Password to SELECT query so it can be edited
            cursor.execute("SELECT Admin_ID, Name, Email, Password FROM mst_admin ORDER BY Admin_ID")
            admins = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in admins]
            cursor.close()
            return jsonify(result), 200
        except Exception as e:
            print("Error fetching admins:", e)
            return jsonify({"error": "Unable to fetch admins"}), 500

    @admin_bp.route('/admins', methods=['POST'])
    def add_admin():
        try:
            data = request.get_json()
            cursor = mysql.connection.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT COUNT(*) FROM mst_admin WHERE Email = %s", (data['Email'],))
            if cursor.fetchone()[0] > 0:
                cursor.close()
                return jsonify({"error": "Email already exists"}), 400
            
            cursor.execute("""
                INSERT INTO mst_admin (Name, Email, Password)
                VALUES (%s, %s, %s)
            """, (data['Name'], data['Email'], data['Password']))
            
            mysql.connection.commit()
            admin_id = cursor.lastrowid
            cursor.close()
            return jsonify({"message": "Admin added successfully", "Admin_ID": admin_id}), 201
        except Exception as e:
            print("Error adding admin:", e)
            return jsonify({"error": f"Unable to add admin: {str(e)}"}), 500

    @admin_bp.route('/admins/<int:admin_id>', methods=['PUT'])
    def update_admin(admin_id):
        try:
            data = request.get_json()
            cursor = mysql.connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM mst_admin WHERE Email = %s AND Admin_ID != %s", (data['Email'], admin_id))
            if cursor.fetchone()[0] > 0:
                cursor.close()
                return jsonify({"error": "Email already exists"}), 400
            
            # Updated query to include Password
            cursor.execute("""
                UPDATE mst_admin 
                SET Name = %s, Email = %s, Password = %s
                WHERE Admin_ID = %s
            """, (data['Name'], data['Email'], data['Password'], admin_id))
            
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Admin updated successfully"}), 200
        except Exception as e:
            print("Error updating admin:", e)
            return jsonify({"error": f"Unable to update admin: {str(e)}"}), 500

    @admin_bp.route('/admins/<int:admin_id>', methods=['DELETE'])
    def delete_admin(admin_id):
        try:
            cursor = mysql.connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM mst_admin")
            admin_count = cursor.fetchone()[0]
            
            if admin_count <= 1:
                cursor.close()
                return jsonify({"error": "Cannot delete the last admin account"}), 400
            
            cursor.execute("DELETE FROM mst_admin WHERE Admin_ID = %s", (admin_id,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Admin deleted successfully"}), 200
        except Exception as e:
            print("Error deleting admin:", e)
            return jsonify({"error": f"Unable to delete admin: {str(e)}"}), 500

    # Login Logs Routes
    @admin_bp.route('/logs', methods=['GET'])
    def get_logs():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""SELECT Log_ID, User_Email, Role, Login_Time, Logout_Time FROM login_log ORDER BY Log_ID""")
            logs = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = []
            for row in logs:
                log_dict = dict(zip(columns, row))
                if log_dict.get('Login_Time'):
                    log_dict['Login_Time'] = log_dict['Login_Time'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(log_dict['Login_Time'], 'strftime') else str(log_dict['Login_Time'])
                if log_dict.get('Logout_Time'):
                    log_dict['Logout_Time'] = log_dict['Logout_Time'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(log_dict['Logout_Time'], 'strftime') else str(log_dict['Logout_Time'])
                result.append(log_dict)
        
            cursor.close()
            return jsonify(result), 200
        except Exception as e:
            print("Error fetching logs:", e)
            return jsonify({"error": "Unable to fetch logs"}), 500

    @admin_bp.route('/logs/<int:log_id>', methods=['DELETE'])
    def delete_log(log_id):
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM login_log WHERE Log_ID = %s", (log_id,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Log deleted successfully"}), 200
        except Exception as e:
            print("Error deleting log:", e)
            return jsonify({"error": f"Unable to delete log: {str(e)}"}), 500

    # Bulk delete operations
    @admin_bp.route('/applicants/bulk-delete', methods=['POST'])
    def bulk_delete_applicants():
        try:
            data = request.get_json()
            applicant_ids = data.get('applicant_ids', [])
        
            if not applicant_ids:
                return jsonify({"error": "No applicant IDs provided"}), 400
        
            cursor = mysql.connection.cursor()
            deleted_count = 0
            errors = []
            total_answers_deleted = 0
            total_attempts_deleted = 0
            total_logs_deleted = 0
        
            for applicant_id in applicant_ids:
                try:
                    cursor.execute("SELECT Attempt_Id FROM applicant_attempt WHERE Applicant_Id = %s", (applicant_id,))
                    attempt_ids = [row[0] for row in cursor.fetchall()]
                
                    if attempt_ids:
                        for attempt_id in attempt_ids:
                            cursor.execute("SELECT COUNT(*) FROM applicant_answers WHERE Attempt_Id = %s", (attempt_id,))
                            answer_count = cursor.fetchone()[0]
                            if answer_count > 0:
                                cursor.execute("DELETE FROM applicant_answers WHERE Attempt_Id = %s", (attempt_id,))
                                total_answers_deleted += answer_count
                
                    cursor.execute("SELECT COUNT(*) FROM applicant_attempt WHERE Applicant_Id = %s", (applicant_id,))
                    attempt_count = cursor.fetchone()[0]
                    if attempt_count > 0:
                        cursor.execute("DELETE FROM applicant_attempt WHERE Applicant_Id = %s", (applicant_id,))
                        total_attempts_deleted += attempt_count
                
                    cursor.execute("SELECT Email FROM applicants WHERE Applicant_Id = %s", (applicant_id,))
                    row = cursor.fetchone()
                    applicant_email = row[0] if row else None
                    if applicant_email:
                        cursor.execute("SELECT COUNT(*) FROM login_log WHERE User_Email = %s", (applicant_email,))
                        log_count = cursor.fetchone()[0]
                        if log_count > 0:
                            cursor.execute("DELETE FROM login_log WHERE User_Email = %s", (applicant_id,))
                            total_logs_deleted += log_count
                
                    cursor.execute("DELETE FROM applicants WHERE Applicant_Id = %s", (applicant_id,))
                    deleted_count += 1
                except Exception as e:
                    errors.append(f"Error deleting applicant {applicant_id}: {str(e)}")
        
            mysql.connection.commit()
            cursor.close()
        
            message = f"Successfully deleted applicants"
            details = []
            if total_answers_deleted > 0:
                details.append(f"{total_answers_deleted} exam answers")
            if total_attempts_deleted > 0:
                details.append(f"{total_attempts_deleted} exam attempts")
            if total_logs_deleted > 0:
                details.append(f"{total_logs_deleted} login logs")
        
            if details:
                message += f" (also removed {', '.join(details)})"
        
            if errors:
                message += f". Errors: {'; '.join(errors)}"
        
            return jsonify({"message": message}), 200
        except Exception as e:
            print("Error in bulk delete:", e)
            mysql.connection.rollback()
            return jsonify({"error": f"Bulk delete failed: {str(e)}"}), 500

    # Student Upload Routes
    ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @admin_bp.route('/add_students', methods=['POST'])
    def add_students():
        file = request.files.get('file')
        exam_id = request.form.get('exam_id')

        if not file or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid or missing file'}), 400

        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            required_columns = ['Full_Name', 'Email', 'Password', 'Phone', 'DOB', 'Gender', 'Address']
            if not all(col in df.columns for col in required_columns):
                return jsonify({'error': 'Missing required columns in uploaded file'}), 400

            cursor = mysql.connection.cursor()
            successful_uploads = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    cursor.execute("""INSERT INTO applicants (Full_Name, Email, Password, Phone, DOB, Gender, Address) VALUES (%s, %s, %s, %s, %s, %s, %s)""", (
                        row['Full_Name'],
                        row['Email'],
                        row['Password'],
                        row['Phone'],
                        row['DOB'],
                        row['Gender'],
                        row['Address']
                    ))
                    successful_uploads += 1

                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
                    continue

            mysql.connection.commit()
            cursor.close()

            return jsonify({
                'success': True,
                'message': f'Successfully uploaded {successful_uploads} students',
                'successful_uploads': successful_uploads,
                'errors': errors
            }), 200

        except Exception as e:
            print("Upload Error:", e)
            return jsonify({'error': str(e)}), 500

    @admin_bp.route('/upload_students', methods=['POST'])
    def upload_students():
        file = request.files.get('file')
        uploaded_by = request.form.get('email')
        role = request.form.get('role', 'Admin')

        if not file or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid or missing file'}), 400

        try:
            filename = secure_filename(file.filename)
            upload_path = os.path.join('uploads/students', filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            file.save(upload_path)

            if filename.endswith('.csv'):
                df = pd.read_csv(upload_path)
            else:
                df = pd.read_excel(upload_path)

            required_columns = ['Full_Name', 'Email', 'Password', 'Phone', 'DOB', 'Gender', 'Address']
            if not all(col in df.columns for col in required_columns):
                return jsonify({'error': 'Missing required columns in uploaded file'}), 400

            cursor = mysql.connection.cursor()
            successful_uploads = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    cursor.execute("""INSERT INTO applicants (Full_Name, Email, Password, Phone, DOB, Gender, Address) VALUES (%s, %s, %s, %s, %s, %s, %s)""", (
                        row['Full_Name'],
                        row['Email'],
                        row['Password'],
                        row['Phone'],
                        row['DOB'],
                        row['Gender'],
                        row['Address']
                    ))
                    successful_uploads += 1

                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
                    continue

            try:
                cursor.execute("""INSERT INTO file_uploads (Uploaded_By, Role, File_Name, File_Path) VALUES (%s, %s, %s, %s)""", (uploaded_by, role, filename, upload_path))
            except Exception as e:
                print("Logging upload failed:", e)

            mysql.connection.commit()
            cursor.close()

            return jsonify({
                'success': True,
                'message': f'Successfully uploaded {successful_uploads} students and logged the upload',
                'successful_uploads': successful_uploads,
                'errors': errors
            }), 200

        except Exception as e:
            print("Upload Error:", e)
            return jsonify({'error': str(e)}), 500

    # Conducted Exams Route - Admin can see ALL conducted exams
    @admin_bp.route('/conducted_exams', methods=['GET'])
    def get_all_conducted_exams():
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT 
                    ee.Exam_Id,
                    ee.Exam_Name,
                    ee.Exam_Date,
                    ee.faculty_email,
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
                WHERE TIMESTAMP(ee.Exam_Date, ee.Exam_Time) + INTERVAL ee.Duration_Minutes MINUTE <= NOW()
                GROUP BY ee.Exam_Id, ee.Exam_Name, ee.Exam_Date, ee.faculty_email, attempts.attempted_applicants
                ORDER BY ee.Exam_Date DESC
            """
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            exams = []
            for row in cursor.fetchall():
                exams.append(dict(zip(columns, row)))
            cursor.close()
            return jsonify({"success": True, "exams": exams}), 200
        except Exception as e:
            print("Error fetching conducted exams:", e)
            return jsonify({"success": False, "error": str(e)}), 500

    # Conducted Exams by Faculty - Admin can filter by specific faculty
    @admin_bp.route('/conducted_exams/<faculty_email>', methods=['GET'])
    def get_conducted_exams_by_faculty(faculty_email):
        try:
            cursor = mysql.connection.cursor()
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
            columns = [desc[0] for desc in cursor.description]
            exams = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return jsonify({"success": True, "exams": exams}), 200
        except Exception as e:
            print("Error fetching conducted exams for faculty:", e)
            return jsonify({"success": False, "error": str(e)}), 500
        
    @admin_bp.route('/exam/delete/<int:exam_id>', methods=['DELETE'])
    def delete_exam(exam_id):
        try:
            cursor = mysql.connection.cursor()
            
            cursor.execute("SELECT Exam_Paper_Id FROM exam_paper WHERE Exam_Id = %s", (exam_id,))
            exam_papers = [row[0] for row in cursor.fetchall()]
            
            if exam_papers:
                for exam_paper_id in exam_papers:
                    cursor.execute("SELECT Attempt_Id FROM applicant_attempt WHERE Exam_Paper_Id = %s", (exam_paper_id,))
                    attempts = [row[0] for row in cursor.fetchall()]
                    
                    if attempts:
                        for attempt_id in attempts:
                            cursor.execute("DELETE FROM applicant_answers WHERE Attempt_Id = %s", (attempt_id,))
                    
                    cursor.execute("DELETE FROM applicant_attempt WHERE Exam_Paper_Id = %s", (exam_paper_id,))
            
            cursor.execute("DELETE FROM applicant_exam_assign WHERE Exam_Id = %s", (exam_id,))
            cursor.execute("DELETE FROM exam_paper WHERE Exam_Id = %s", (exam_id,))
            cursor.execute("DELETE FROM Entrance_Exam WHERE Exam_Id = %s", (exam_id,))
            
            mysql.connection.commit()
            cursor.close()
            
            return jsonify({"success": True, "message": "Exam deleted successfully"}), 200
        except Exception as e:
            print("Error deleting exam:", e)
            mysql.connection.rollback()
            return jsonify({"success": False, "error": f"Unable to delete exam: {str(e)}"}), 500

    @admin_bp.route('/admin/exam/delete/<int:exam_id>', methods=['DELETE'])
    def admin_delete_exam(exam_id):
        try:
            cursor = mysql.connection.cursor()
            
            cursor.execute("SELECT Exam_Paper_Id FROM exam_paper WHERE Exam_Id = %s", (exam_id,))
            exam_papers = [row[0] for row in cursor.fetchall()]
            
            if exam_papers:
                for exam_paper_id in exam_papers:
                    cursor.execute("SELECT Attempt_Id FROM applicant_attempt WHERE Exam_Paper_Id = %s", (exam_paper_id,))
                    attempts = [row[0] for row in cursor.fetchall()]
                    
                    if attempts:
                        for attempt_id in attempts:
                            cursor.execute("DELETE FROM applicant_answers WHERE Attempt_Id = %s", (attempt_id,))
                    
                    cursor.execute("DELETE FROM applicant_attempt WHERE Exam_Paper_Id = %s", (exam_paper_id,))
            
            cursor.execute("DELETE FROM applicant_exam_assign WHERE Exam_Id = %s", (exam_id,))
            cursor.execute("DELETE FROM exam_paper WHERE Exam_Id = %s", (exam_id,))
            cursor.execute("DELETE FROM Entrance_Exam WHERE Exam_Id = %s", (exam_id,))
            
            mysql.connection.commit()
            cursor.close()
            
            return jsonify({"success": True, "message": "Exam deleted successfully"}), 200
        except Exception as e:
            print("Error deleting exam:", e)
            mysql.connection.rollback()
            return jsonify({"success": False, "error": f"Unable to delete exam: {str(e)}"}), 500

    return admin_bp