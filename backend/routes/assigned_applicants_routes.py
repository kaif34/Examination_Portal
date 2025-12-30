from flask import Blueprint, jsonify
import MySQLdb.cursors

def create_assigned_applicants_routes(mysql):
    assigned_applicants_bp = Blueprint('assigned_applicants', __name__)

    @assigned_applicants_bp.route('/api/get_assigned_applicants/<int:exam_id>', methods=['GET'])
    def get_assigned_applicants(exam_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = """
                SELECT a.Applicant_Id, a.Full_Name, a.Email, a.Password
                FROM applicant_exam_assign ae
                JOIN applicants a ON ae.Applicant_Id = a.Applicant_Id
                WHERE ae.Exam_Id = %s
            """
            cursor.execute(query, (exam_id,))
            assigned_applicants = cursor.fetchall()

            return jsonify({'success': True, 'assignedApplicants': assigned_applicants})
        except Exception as e:
            print("❌ Error loading assigned applicants:", str(e))
            return jsonify({'success': False, 'message': 'Error loading assigned applicants'})

    return assigned_applicants_bp
