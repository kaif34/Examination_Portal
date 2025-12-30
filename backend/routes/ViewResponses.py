from flask import Blueprint, request, jsonify
import MySQLdb.cursors

def create_view_responses_bp(mysql):
    view_responses_bp = Blueprint('view_responses', __name__)

    @view_responses_bp.route('/api/attempts', methods=['GET'])
    def get_attempts():
        exam_id = request.args.get('exam_id')
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            query = """
                SELECT 
                    aa.Attempt_Id, aa.Applicant_Id, aa.Student_Email, 
                    aa.Start_Time, aa.End_Time, aa.Marks_Obtained,
                    ep.Exam_Paper_Id, ep.Title AS Exam_Paper_Title, 
                    ee.Exam_Id, ee.Exam_Name, ee.Max_Marks,
                    ag.Status
                FROM applicant_attempt aa
                JOIN exam_paper ep ON aa.Exam_Paper_Id = ep.Exam_Paper_Id
                JOIN entrance_exam ee ON ep.Exam_Id = ee.Exam_Id
                LEFT JOIN auto_grading ag ON aa.Attempt_Id = ag.Attempt_Id
            """

            params = ()
            if exam_id:
                query += " WHERE ee.Exam_Id = %s"
                params = (exam_id,)
            query += " ORDER BY ep.Exam_Paper_Id, aa.Start_Time DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()

            for row in rows:
                row['Start_Time'] = row['Start_Time'].strftime("%Y-%m-%d %H:%M:%S") if row['Start_Time'] else None
                row['End_Time'] = row['End_Time'].strftime("%Y-%m-%d %H:%M:%S") if row['End_Time'] else None
                row['Marks_Obtained'] = float(row['Marks_Obtained']) if row['Marks_Obtained'] is not None else 0.0

            return jsonify({'attempts': rows}), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    return view_responses_bp
