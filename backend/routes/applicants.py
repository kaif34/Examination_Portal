from flask import Blueprint, request, jsonify

def create_applicants_bp(mysql):
    applicants_bp = Blueprint('applicants', __name__)

    @applicants_bp.route('/api/applicants/add', methods=['POST'])
    def add_applicant():
        data = request.json
        try:
            cursor = mysql.connection.cursor()
            query = """
                INSERT INTO Applicants (Full_Name, Email, Password, Phone, DOB, Gender, Address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                data['Full_Name'],
                data['Email'],
                data['Password'],
                data.get('Phone'),
                data.get('DOB'),
                data.get('Gender'),
                data.get('Address')
            ))
            mysql.connection.commit()
            return jsonify({'success': True, 'message': 'Applicant added'})
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'error': str(e)})

    return applicants_bp
