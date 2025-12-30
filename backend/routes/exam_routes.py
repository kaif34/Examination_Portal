from flask import Blueprint, request, jsonify
from datetime import datetime
import traceback
import MySQLdb.cursors


def create_exam_routes(mysql):
    exam_bp = Blueprint('exam', __name__)

    @exam_bp.route('/create', methods=['POST'])
    def create_exam():
        data = request.json
        exam_name = data.get('exam_name')
        exam_date = data.get('exam_date')      # format: YYYY-MM-DD
        exam_time = data.get('exam_time')      # format: HH:MM
        duration = data.get('duration')         # integer
        total_questions = data.get('total_questions')
        max_marks = data.get('max_marks')
        faculty_email = data.get('faculty_email')

        if not all([exam_name, exam_date, exam_time, duration, total_questions, max_marks, faculty_email]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        try:
            exam_datetime_str = f"{exam_date} {exam_time}"
            exam_datetime = datetime.strptime(exam_datetime_str, "%Y-%m-%d %H:%M")
            current_datetime = datetime.now()

            if exam_datetime < current_datetime:
                return jsonify({'success': False, 'message': 'Exam date/time cannot be in the past'}), 400

            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO Entrance_Exam 
                (Exam_Name, Exam_Date, Exam_Time, Duration_Minutes, Total_Questions, Max_Marks, Faculty_Email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (exam_name, exam_date, exam_time, duration, total_questions, max_marks, faculty_email))
            mysql.connection.commit()
            exam_id = cursor.lastrowid
            cursor.close()

            return jsonify({
                'success': True,
                'message': f'Exam created successfully with ID: {exam_id}',
                'exam_id': exam_id
            })

        except Exception as e:
            print("DB error:", e)
            return jsonify({'success': False, 'message': 'Database error'}), 500

    @exam_bp.route('/get_exams/<faculty_email>', methods=['GET'])
    def get_exams(faculty_email):
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT Exam_Id, Exam_Name, Exam_Date, Exam_Time, Duration_Minutes,
                       Total_Questions, Max_Marks
                FROM Entrance_Exam
                WHERE Faculty_Email = %s
            """, (faculty_email,))
            exams = cursor.fetchall()
            cursor.close()

            exam_list = []
            for row in exams:
                exam_list.append({
                    'Exam_Id': row[0],
                    'Exam_Name': row[1],
                    'Exam_Date': str(row[2]),
                    'Exam_Time': str(row[3]),
                    'Duration_Minutes': row[4],
                    'Total_Questions': row[5],
                    'Max_Marks': row[6]
                })

            return jsonify({'success': True, 'exams': exam_list})

        except Exception as e:
            print("Error fetching exams:", e)
            return jsonify({'success': False, 'message': 'Server error'}), 500

    @exam_bp.route('/get_exam_by_id/<int:exam_id>', methods=['GET'])
    def get_exam_by_id(exam_id):
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT Exam_Id, Exam_Name, Exam_Date, Exam_Time, Duration_Minutes,
                       Total_Questions, Max_Marks, Faculty_Email
                FROM Entrance_Exam
                WHERE Exam_Id = %s
            """, (exam_id,))
            row = cursor.fetchone()
            cursor.close()

            if row:
                exam = {
                    'Exam_Id': row[0],
                    'Exam_Name': row[1],
                    'Exam_Date': str(row[2]),
                    'Exam_Time': str(row[3]),
                    'Duration_Minutes': row[4],
                    'Total_Questions': row[5],
                    'Max_Marks': row[6],
                    'Faculty_Email': row[7]
                }
                return jsonify({'exam': exam})
            else:
                return jsonify({'error': 'Exam not found'}), 404

        except Exception as e:
            print("Exception occurred:", e)
            traceback.print_exc()
            return jsonify({'error': 'Server error'}), 500

    @exam_bp.route('/delete/<int:exam_id>', methods=['DELETE'])
    def delete_exam(exam_id):
        try:
            cursor = mysql.connection.cursor()

            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            cursor.execute("""
                DELETE FROM exam_paper_questions 
                WHERE Exam_Paper_Id IN (
                    SELECT Exam_Paper_Id FROM exam_paper WHERE Exam_Id = %s)
            """, (exam_id,))
            cursor.execute("DELETE FROM exam_paper WHERE Exam_Id = %s", (exam_id,))
            cursor.execute("DELETE FROM entrance_question_bank WHERE Exam_Id = %s", (exam_id,))
            cursor.execute("DELETE FROM applicant_exam_assign WHERE Exam_Id = %s", (exam_id,))
            cursor.execute("DELETE FROM Entrance_Exam WHERE Exam_Id = %s", (exam_id,))

            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            mysql.connection.commit()
            cursor.close()

            return jsonify({'success': True, 'message': 'Exam deleted successfully!'})

        except Exception as e:
            print("Error deleting exam:", e)
            return jsonify({'success': False, 'message': 'Failed to delete exam'}), 500

    # New route to get question bank and paper status
    @exam_bp.route('/status/<int:exam_id>', methods=['GET'])
    def get_exam_status(exam_id):
        try:
            cursor = mysql.connection.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM entrance_question_bank WHERE Exam_Id = %s
            """, (exam_id,))
            qb_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM exam_paper WHERE Exam_Id = %s
            """, (exam_id,))
            qp_count = cursor.fetchone()[0]

            cursor.close()

            status = {
                'has_question_bank': qb_count > 0,
                'has_question_paper': qp_count > 0
            }
            return jsonify({'success': True, 'status': status})

        except Exception as e:
            print("Error in get_exam_status:", e)
            return jsonify({'success': False, 'message': 'Server error'}), 500

    return exam_bp
