from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta


def create_student_routes(mysql):
    student_routes = Blueprint('student_routes', __name__)

    # Get next upcoming exam
    @student_routes.route('/exam', methods=['GET'])
    def get_exam_data():
        try:
            cur = mysql.connection.cursor()

            # Get the next upcoming exam
            cur.execute("""
                SELECT Exam_Id, Exam_Name, Exam_Date, Exam_Time, Duration_Minutes, 
                       Total_Questions, Max_Marks, Faculty_Email
                FROM entrance_exam 
                WHERE Exam_Date >= CURDATE()
                ORDER BY Exam_Date, Exam_Time 
                LIMIT 1
            """)
            exam = cur.fetchone()

            if not exam:
                cur.close()
                return jsonify({"message": "No upcoming exam found"}), 404

            exam_id = exam[0]

            # Get questions for this exam
            cur.execute("""
                SELECT q.Question_Id, q.Exam_Id, q.Question_Type, q.Question_Text, 
                       q.Option_A, q.Option_B, q.Option_C, q.Option_D
                FROM entrance_question_bank q   
                JOIN exam_paper_questions epq ON q.Question_Id = epq.Question_Id
                JOIN exam_paper ep ON epq.Exam_Paper_Id = ep.Exam_Paper_Id    
                WHERE ep.Exam_Id = %s
            """, (exam_id,))
            questions = cur.fetchall()

            # Get or create exam paper
            cur.execute("SELECT * FROM exam_paper WHERE Exam_Id = %s", (exam_id,))
            exam_paper = cur.fetchone()

            if not exam_paper:
                cur.execute("""
                    INSERT INTO exam_paper (Exam_Id, Title, Total_Marks, Duration_Minutes)
                    VALUES (%s, %s, %s, %s)
                """, (exam_id, exam[1], exam[6], exam[4]))
                mysql.connection.commit()
                exam_paper_id = cur.lastrowid
            else:
                exam_paper_id = exam_paper[0]

            cur.close()

            return jsonify({
                "exam": {
                    "Exam_Id": exam[0],
                    "Exam_Paper_Id": exam_paper_id,
                    "Exam_Name": exam[1],
                    "Exam_Date": str(exam[2]),
                    "Exam_Time": str(exam[3]),
                    "Duration_Minutes": exam[4],
                    "Total_Questions": exam[5],
                    "Max_Marks": exam[6],
                    "Faculty_Email": exam[7],
                },
                "questions": [
                    {
                        "Question_Id": q[0],
                        "Question_Type": q[2],
                        "Question_Text": q[3],
                        "Option_A": q[4],
                        "Option_B": q[5],
                        "Option_C": q[6],
                        "Option_D": q[7]
                    } for q in questions
                ]
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Start exam attempt
    @student_routes.route('/start-exam', methods=['POST'])
    def start_exam_attempt():
        try:
            data = request.json
            applicant_id = data.get('applicant_id')
            exam_id = data.get('exam_id')

            if not applicant_id or not exam_id:
                return jsonify({"message": "Applicant ID and Exam ID are required"}), 400

            cur = mysql.connection.cursor()

            # Get student email
            cur.execute("SELECT Email FROM applicants WHERE Applicant_Id = %s", (applicant_id,))
            applicant_result = cur.fetchone()

            if not applicant_result:
                cur.close()
                return jsonify({"error": "Applicant not found"}), 404

            student_email = applicant_result[0]

            # Get exam paper ID
            cur.execute("SELECT Exam_Paper_Id FROM exam_paper WHERE Exam_Id = %s", (exam_id,))
            exam_paper_result = cur.fetchone()

            if not exam_paper_result:
                cur.close()
                return jsonify({"error": "Exam paper not found"}), 404

            exam_paper_id = exam_paper_result[0]

            # Check if attempt already exists
            cur.execute("""
                SELECT Attempt_Id FROM applicant_attempt aa
                JOIN exam_paper ep ON aa.Exam_Paper_Id = ep.Exam_Paper_Id
                WHERE aa.Applicant_Id = %s AND ep.Exam_Id = %s
            """, (applicant_id, exam_id))

            existing_attempt = cur.fetchone()
            if existing_attempt:
                cur.close()
                return jsonify({
                    "message": "Attempt already exists",
                    "attempt_id": existing_attempt[0]
                }), 409

            # Create new attempt
            start_time = datetime.now()
            cur.execute("""
                INSERT INTO applicant_attempt (Applicant_Id, Student_Email, Exam_Paper_Id, Start_Time, Status)
                VALUES (%s, %s, %s, %s, %s)
            """, (applicant_id, student_email, exam_paper_id, start_time, "In Progress"))

            attempt_id = cur.lastrowid
            mysql.connection.commit()
            cur.close()

            return jsonify({
                "message": "Exam attempt started successfully",
                "attempt_id": attempt_id,
                "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S')
            })

        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"error": str(e)}), 500

    # Fetch exam by id with 10‑minute entry limit
    @student_routes.route('/exam/<int:exam_id>', methods=['POST'])
    def get_exam_by_id(exam_id):
        try:
            data = request.json
            applicant_id = data.get('applicant_id')

            if not applicant_id:
                return jsonify({"message": "Applicant ID is required"}), 400

            cur = mysql.connection.cursor()

            # 1. Check exam exists
            cur.execute("SELECT * FROM entrance_exam WHERE Exam_Id = %s", (exam_id,))
            exam = cur.fetchone()

            if not exam:
                cur.close()
                return jsonify({"message": "Invalid Exam ID"}), 404

            exam_date = exam[2]
            exam_time = exam[3]
            duration_minutes = exam[4]

            if isinstance(exam_time, timedelta):
                exam_datetime = datetime.combine(exam_date, (datetime.min + exam_time).time())
            else:
                exam_datetime = datetime.combine(exam_date, exam_time)

            exam_end_10_minutes = exam_datetime + timedelta(minutes=10)
            current_time = datetime.now()

            # Not started
            if current_time < exam_datetime:
                cur.close()
                return jsonify({
                    "error": f"Exam has not started yet. Please wait until {exam_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
                }), 425

            # Entry window over
            if current_time > exam_end_10_minutes:
                cur.close()
                return jsonify({
                    "error": "Exam entry time has expired. You cannot start the exam after 10 minutes of exam start time."
                }), 410

            # 3. Check assignment
            cur.execute("""
                SELECT COUNT(*) FROM applicant_exam_assign 
                WHERE Applicant_Id = %s AND Exam_Id = %s
            """, (applicant_id, exam_id))

            is_assigned = cur.fetchone()[0] > 0

            if not is_assigned:
                cur.close()
                return jsonify({
                    "message": "Access Denied",
                    "error": "You are not assigned to this exam. Please contact your faculty."
                }), 403

            # 4. Check previous attempt
            cur.execute("""
                SELECT Attempt_Id, Status FROM applicant_attempt aa
                JOIN exam_paper ep ON aa.Exam_Paper_Id = ep.Exam_Paper_Id
                WHERE aa.Applicant_Id = %s AND ep.Exam_Id = %s
            """, (applicant_id, exam_id))

            attempt_result = cur.fetchone()
            attempt_id = None
            if attempt_result:
                attempt_id, status = attempt_result
                if status in ['Submitted', 'Forcibly Ended']:
                    cur.close()
                    return jsonify({
                        "message": "Already Attempted",
                        "error": "You have already attempted this exam. Multiple attempts are not allowed."
                    }), 409

            # 5. Remaining time (full duration)
            remaining_seconds = duration_minutes * 60

            # 6. Questions
            cur.execute("""
                SELECT q.Question_Id, q.Exam_Id, q.Question_Type, q.Question_Text, 
                       q.Option_A, q.Option_B, q.Option_C, q.Option_D
                FROM entrance_question_bank q   
                JOIN exam_paper_questions epq ON q.Question_Id = epq.Question_Id
                JOIN exam_paper ep ON epq.Exam_Paper_Id = ep.Exam_Paper_Id    
                WHERE ep.Exam_Id = %s
            """, (exam_id,))
            questions = cur.fetchall()

            # Exam paper
            cur.execute("SELECT * FROM exam_paper WHERE Exam_Id = %s", (exam_id,))
            exam_paper = cur.fetchone()

            if not exam_paper:
                cur.execute("""
                    INSERT INTO exam_paper (Exam_Id, Title, Total_Marks, Duration_Minutes)
                    VALUES (%s, %s, %s, %s)
                """, (exam_id, exam[1], exam[6], exam[4]))
                mysql.connection.commit()
                exam_paper_id = cur.lastrowid
            else:
                exam_paper_id = exam_paper[0]

            cur.close()

            return jsonify({
                "exam": {
                    "Exam_Id": exam[0],
                    "Exam_Paper_Id": exam_paper_id,
                    "Exam_Name": exam[1],
                    "Exam_Date": str(exam[2]),
                    "Exam_Time": str(exam[3]),
                    "Duration_Minutes": exam[4],
                    "Total_Questions": exam[5],
                    "Max_Marks": exam[6],
                    "Faculty_Email": exam[7],
                    "Remaining_Seconds": remaining_seconds
                },
                "questions": [
                    {
                        "Question_Id": q[0],
                        "Question_Type": q[2],
                        "Question_Text": q[3],
                        "Option_A": q[4],
                        "Option_B": q[5],
                        "Option_C": q[6],
                        "Option_D": q[7]
                    } for q in questions
                ],
                "attempt_id": attempt_id
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Get assigned exams
    @student_routes.route('/assigned-exams/<int:applicant_id>', methods=['GET'])
    def get_assigned_exams(applicant_id):
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT ee.Exam_Id, ee.Exam_Name, ee.Exam_Date, ee.Exam_Time, 
                       ee.Duration_Minutes, ee.Total_Questions, ee.Max_Marks,
                       aea.Assigned_On,
                       CASE 
                           WHEN aa.Attempt_Id IS NOT NULL THEN 'Completed'
                           ELSE 'Pending'
                       END AS Status
                FROM applicant_exam_assign aea
                JOIN entrance_exam ee ON aea.Exam_Id = ee.Exam_Id
                LEFT JOIN applicant_attempt aa ON aa.Applicant_Id = aea.Applicant_Id 
                    AND aa.Exam_Paper_Id IN (
                        SELECT Exam_Paper_Id FROM exam_paper WHERE Exam_Id = ee.Exam_Id
                    )
                WHERE aea.Applicant_Id = %s
                ORDER BY ee.Exam_Date, ee.Exam_Time
            """, (applicant_id,))

            assigned_exams = cur.fetchall()
            cur.close()

            return jsonify({
                "assigned_exams": [{
                    "Exam_Id": exam[0],
                    "Exam_Name": exam[1],
                    "Exam_Date": str(exam[2]),
                    "Exam_Time": str(exam[3]),
                    "Duration_Minutes": exam[4],
                    "Total_Questions": exam[5],
                    "Max_Marks": exam[6],
                    "Assigned_On": str(exam[7]),
                    "Status": exam[8]
                } for exam in assigned_exams]
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Submit answers (normal finish / time‑up)
    @student_routes.route('/submit', methods=['POST'])
    def submit_answers():
        try:
            data = request.json
            applicant_id = data['applicant_id']
            exam_paper_id = data['exam_paper_id']
            answers = data['answers']
            attempt_id = data.get('attempt_id')

            cur = mysql.connection.cursor()

            end_time = datetime.now()

            # Update or create attempt
            if attempt_id:
                cur.execute("""
                    UPDATE applicant_attempt 
                    SET End_Time = %s, Status = %s
                    WHERE Attempt_Id = %s
                """, (end_time, "Submitted", attempt_id))
            else:
                cur.execute("SELECT Email FROM applicants WHERE Applicant_Id = %s", (applicant_id,))
                applicant_result = cur.fetchone()
                if not applicant_result:
                    cur.close()
                    return jsonify({"error": "Applicant not found"}), 404
                student_email = applicant_result[0]
                start_time = end_time
                cur.execute("""
                    INSERT INTO applicant_attempt (Applicant_Id, Student_Email, Exam_Paper_Id, Start_Time, End_Time, Status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (applicant_id, student_email, exam_paper_id, start_time, end_time, "Submitted"))
                attempt_id = cur.lastrowid

            total_marks = 0

            # Evaluate and store answers
            for ans in answers:
                question_id = ans['question_id']
                selected_option = ans['selected_option']
                if not selected_option:
                    continue

                cur.execute("""
                    SELECT Question_Type, Correct_Answer, Marks,
                           Option_A, Option_B, Option_C, Option_D
                    FROM entrance_question_bank
                    WHERE Question_Id = %s
                """, (question_id,))
                row = cur.fetchone()
                if not row:
                    continue

                q_type, correct_answer, marks, opt_a, opt_b, opt_c, opt_d = row
                option_map = {'A': opt_a, 'B': opt_b, 'C': opt_c, 'D': opt_d}

                if q_type in ('MCQ', 'TF'):
                    selected_text = option_map.get(selected_option, "")
                    is_correct = selected_text.strip().lower() == correct_answer.strip().lower()
                elif q_type in ('Fill', 'OneWord'):
                    selected_text = selected_option
                    is_correct = selected_text.strip().lower() == correct_answer.strip().lower()
                else:
                    is_correct = False
                    selected_text = selected_option

                if is_correct:
                    total_marks += marks

                cur.execute("""
                    INSERT INTO applicant_answers (Attempt_Id, Question_Id, Selected_Option_Id, Answer_Text)
                    VALUES (%s, %s, %s, %s)
                """, (
                    attempt_id,
                    question_id,
                    selected_option if q_type in ('MCQ', 'TF') else None,
                    selected_text if q_type in ('MCQ', 'TF') else selected_option
                ))

            # Store marks
            cur.execute("""
                UPDATE applicant_attempt SET Marks_Obtained = %s WHERE Attempt_Id = %s
            """, (total_marks, attempt_id))

            # Auto grading
            cur.execute("SELECT Total_Marks FROM exam_paper WHERE Exam_Paper_Id = %s", (exam_paper_id,))
            total_possible_marks = cur.fetchone()[0]
            grading_status = "Fail"
            if total_possible_marks > 0:
                percentage = (total_marks / total_possible_marks) * 100
                grading_status = "Pass" if percentage >= 40 else "Fail"

            cur.execute("""
                INSERT INTO auto_grading (Attempt_Id, Total_Score, Status)
                VALUES (%s, %s, %s)
            """, (attempt_id, total_marks, grading_status))

            mysql.connection.commit()

            # Auto logout (normal)
            cur2 = mysql.connection.cursor()
            cur2.execute("""
                UPDATE login_log
                SET Logout_Time = %s
                WHERE User_Email = (SELECT Student_Email FROM applicant_attempt WHERE Attempt_Id = %s)
                AND Role = 'Student'
                ORDER BY Log_ID DESC
                LIMIT 1
            """, (end_time, attempt_id))
            mysql.connection.commit()
            cur2.close()

            cur.execute("SELECT Student_Email FROM applicant_attempt WHERE Attempt_Id = %s", (attempt_id,))
            student_email = cur.fetchone()[0]
            cur.close()

            return jsonify({
                "message": "Answers submitted successfully",
                "Attempt_Id": attempt_id,
                "Student_Email": student_email,
                "Total_Marks": total_marks,
                "Status": grading_status
            })
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"error": str(e)}), 500

    # View all attempts
    @student_routes.route('/attempts/<int:applicant_id>', methods=['GET'])
    def get_attempts(applicant_id):
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT aa.Attempt_Id, aa.Start_Time, aa.End_Time, aa.Status, 
                       aa.Marks_Obtained, aa.Student_Email, ep.Title, ee.Exam_Name, ee.Max_Marks,
                       ag.Status as Grade_Status
                FROM applicant_attempt aa
                JOIN exam_paper ep ON aa.Exam_Paper_Id = ep.Exam_Paper_Id
                JOIN entrance_exam ee ON ep.Exam_Id = ee.Exam_Id
                LEFT JOIN auto_grading ag ON aa.Attempt_Id = ag.Attempt_Id
                WHERE aa.Applicant_Id = %s
                ORDER BY aa.Start_Time DESC
            """, (applicant_id,))
            attempts = cur.fetchall()
            cur.close()

            return jsonify({
                "attempts": [{
                    "Attempt_Id": a[0],
                    "Start_Time": str(a[1]),
                    "End_Time": str(a[2]),
                    "Status": a[3],
                    "Marks_Obtained": a[4],
                    "Student_Email": a[5],
                    "Paper_Title": a[6],
                    "Exam_Name": a[7],
                    "Max_Marks": a[8],
                    "Grade_Status": a[9]
                } for a in attempts],
                "total_attempts": len(attempts)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Exam status helper
    @student_routes.route('/exam-status/<int:exam_id>/<int:applicant_id>', methods=['GET'])
    def get_exam_status(exam_id, applicant_id):
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM entrance_exam WHERE Exam_Id = %s", (exam_id,))
            exam = cur.fetchone()

            if not exam:
                cur.close()
                return jsonify({"error": "Exam not found"}), 404

            exam_date = exam[2]
            exam_time = exam[3]
            duration_minutes = exam[4]
            if isinstance(exam_time, timedelta):
                exam_datetime = datetime.combine(exam_date, (datetime.min + exam_time).time())
            else:
                exam_datetime = datetime.combine(exam_date, exam_time)

            exam_end_entry_window = exam_datetime + timedelta(minutes=10)
            current_time = datetime.now()

            if current_time < exam_datetime:
                status = "NOT_STARTED"
                message = f"Exam will start at {exam_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
            elif current_time > exam_end_entry_window:
                status = "EXPIRED"
                message = "Exam entry time expired."
            else:
                status = "ACTIVE"
                remaining_seconds = int((exam_end_entry_window - current_time).total_seconds())
                message = f"Exam entry window is active. {remaining_seconds} seconds remaining."

            cur.execute("""
                SELECT COUNT(*) FROM applicant_attempt aa
                JOIN exam_paper ep ON aa.Exam_Paper_Id = ep.Exam_Paper_Id
                WHERE aa.Applicant_Id = %s AND ep.Exam_Id = %s
            """, (applicant_id, exam_id))
            already_attempted = cur.fetchone()[0] > 0

            if already_attempted:
                status = "COMPLETED"
                message = "You have already completed this exam."

            cur.close()
            return jsonify({
                "status": status,
                "message": message,
                "exam_datetime": exam_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                "exam_end_entry_window": exam_end_entry_window.strftime('%Y-%m-%d %H:%M:%S'),
                "current_time": current_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Force‑end exam due to misconduct (0 marks, Fail, reason logged)
    @student_routes.route('/force-end-exam', methods=['POST'])
    def force_end_exam():
        try:
            data = request.json
            attempt_id = data.get('attempt_id')
            reason = data.get('reason', 'Misconduct')
            
            if not attempt_id:
                return jsonify({"error": "Attempt ID required"}), 400
            
            cur = mysql.connection.cursor()
            
            # Validate attempt exists and get details
            cur.execute("""
                SELECT Attempt_Id, Applicant_Id, Student_Email, Exam_Paper_Id 
                FROM applicant_attempt 
                WHERE Attempt_Id = %s
            """, (attempt_id,))
            
            attempt_data = cur.fetchone()
            if not attempt_data:
                cur.close()
                return jsonify({"error": "Attempt ID not found"}), 404

            end_time = datetime.now()
            print(f"Force ending attempt {attempt_id} at {end_time} - Reason: {reason}")

            # Update attempt as forcibly ended with 0 marks
            cur.execute("""
                UPDATE applicant_attempt
                SET End_Time = %s, Status = %s, Marks_Obtained = 0
                WHERE Attempt_Id = %s
            """, (end_time, 'Forcibly Ended', attempt_id))

            # Insert/update auto grading with fail status
            cur.execute("""
                SELECT Attempt_Id FROM auto_grading WHERE Attempt_Id = %s
            """, (attempt_id,))
            
            if cur.fetchone():
                # Update existing grading
                cur.execute("""
                    UPDATE auto_grading 
                    SET Total_Score = 0, Status = 'Fail'
                    WHERE Attempt_Id = %s
                """, (attempt_id,))
            else:
                # Insert new grading
                cur.execute("""
                    INSERT INTO auto_grading (Attempt_Id, Total_Score, Status)
                    VALUES (%s, 0, 'Fail')
                """, (attempt_id,))

            # Auto logout the student
            student_email = attempt_data[2]
            cur.execute("""
                UPDATE login_log
                SET Logout_Time = %s
                WHERE User_Email = %s
                AND Role = 'Student'
                AND Logout_Time IS NULL
                ORDER BY Log_ID DESC
                LIMIT 1
            """, (end_time, student_email))

            mysql.connection.commit()
            cur.close()
            
            print(f"Forced end recorded and committed for attempt {attempt_id}")

            return jsonify({
                "message": "Exam forcibly ended",
                "Attempt_Id": attempt_id,
                "Status": "Forcibly Ended",
                "Marks_Obtained": 0,
                "Reason": reason
            })
            
        except Exception as e:
            mysql.connection.rollback()
            print("Error in force-end-exam route:", str(e))
            return jsonify({"error": str(e)}), 500

    return student_routes