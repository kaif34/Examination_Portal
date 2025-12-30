from flask import Blueprint, jsonify, request
import MySQLdb.cursors

def create_add_applicants_exam_bp(mysql):
    add_applicants_exam_bp = Blueprint('add_applicants_exam', __name__)

    # Route 1: Get all applicants
    @add_applicants_exam_bp.route('/applicants', methods=['GET'])
    def get_applicants():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM applicants")
            rows = cursor.fetchall()

            column_names = [i[0] for i in cursor.description]
            applicants = [dict(zip(column_names, row)) for row in rows]

            return jsonify({'success': True, 'applicants': applicants})
        except Exception as e:
            print("❌ Error loading applicants:", str(e))
            return jsonify({'success': False, 'message': 'Error loading applicants'})

    # Route 2: Get already assigned applicants for a specific exam
    @add_applicants_exam_bp.route('/get_assigned_applicants/<int:exam_id>', methods=['GET'])
    def get_assigned_applicants(exam_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = """
                SELECT a.Applicant_Id, a.Full_Name, a.Email
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

    # Route 3: Assign new applicants to an exam
    @add_applicants_exam_bp.route('/assign_applicants', methods=['POST'])
    def assign_applicants():
        try:
            data = request.get_json()
            exam_id = data.get('exam_id')
            applicant_ids = data.get('applicant_ids', [])

            if not exam_id or not applicant_ids:
                return jsonify({'success': False, 'message': 'Missing exam_id or applicant_ids'}), 400

            cursor = mysql.connection.cursor()

            # Fetch already assigned applicant IDs
            cursor.execute("SELECT Applicant_Id FROM applicant_exam_assign WHERE Exam_Id = %s", (exam_id,))
            already_assigned = set(row[0] for row in cursor.fetchall())

            # Filter out already assigned applicants
            new_ids = [aid for aid in applicant_ids if aid not in already_assigned]

            # Insert only new ones
            for aid in new_ids:
                cursor.execute(
                    "INSERT INTO applicant_exam_assign (Applicant_Id, Exam_Id) VALUES (%s, %s)",
                    (aid, exam_id)
                )

            mysql.connection.commit()

            return jsonify({'success': True, 'assigned_count': len(new_ids)})
        except Exception as e:
            print("❌ Error assigning applicants:", str(e))
            return jsonify({'success': False, 'message': 'Error assigning applicants'})

    return add_applicants_exam_bp
