from flask import Blueprint, jsonify
import MySQLdb.cursors

def create_view_answers_bp(mysql):
    view_answers_bp = Blueprint('view_answers', __name__)

    @view_answers_bp.route('/api/answers/<int:attempt_id>', methods=['GET'])
    def get_answers(attempt_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("""
                SELECT aa.Answer_Id, aa.Attempt_Id, aa.Question_Id, aa.Selected_Option_Id, aa.Answer_Text,
                       qb.Question_Type, qb.Question_Text, qb.Option_A, qb.Option_B, qb.Option_C, qb.Option_D,
                       qb.Correct_Answer
                FROM applicant_answers aa
                JOIN entrance_question_bank qb ON aa.Question_Id = qb.Question_Id
                WHERE aa.Attempt_Id = %s
                ORDER BY aa.Answer_Id
            """, (attempt_id,))
            answers = cursor.fetchall()
            cursor.close()
            return jsonify({"answers": answers}), 200
        except Exception as e:
            import traceback; traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    return view_answers_bp
