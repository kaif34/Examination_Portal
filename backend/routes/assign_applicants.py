from flask import Blueprint, request, jsonify

def create_assign_routes(mysql):
    assign_bp = Blueprint('assign', __name__)

    @assign_bp.route('/api/assign_applicants', methods=['POST'])
    def assign_applicants():
        try:
            data = request.get_json()
            exam_id = data.get('exam_id')
            applicant_ids = data.get('applicant_ids', [])

            if not exam_id or not applicant_ids:
                return jsonify({'error': 'Exam ID and applicant IDs are required'}), 400

            conn = mysql.connection
            cursor = conn.cursor()

            for applicant_id in applicant_ids:
                cursor.execute("""
                    INSERT INTO applicant_exam_assign (Applicant_Id, Exam_Id)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE Assigned_On = CURRENT_TIMESTAMP
                """, (applicant_id, exam_id))

            conn.commit()
            return jsonify({'message': f'{len(applicant_ids)} applicants assigned successfully.'}), 200

        except Exception as e:
            print("Error in assigning applicants:", str(e))
            return jsonify({'error': 'Error assigning applicants'}), 500

    return assign_bp
