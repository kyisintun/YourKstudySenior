from flask import Flask, render_template
from flask import request, redirect
import psycopg2
import os
import psycopg2


app = Flask(__name__)

db_url = os.environ.get('DATABASE_URL')

if db_url: 
    conn = psycopg2.connect(db_url)
else:
    conn = psycopg2.connect(
        host="localhost",
        database="kstudy",
        user="postgres",
        password="kangtaehyun52!"
    )

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/universities')
def universities():

    cur = conn.cursor()

    cur.execute("SELECT * FROM universities")

    universities_data = cur.fetchall()

    cur.close()

    return render_template(
        'universities.html',
        universities=universities_data
    )

@app.route('/university/<int:university_id>')
def university_detail(university_id):

    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM universities WHERE id = %s",
        (university_id,)
    )

    university = cur.fetchone()

    cur.close()

    return render_template(
        'university_detail.html',
        university=university
    )

@app.route('/language-program/<int:university_id>')
def language_program(university_id):

    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM language_institutes
        WHERE university_id = %s
    """, (university_id,))

    programs = cur.fetchall()

    cur.close()

    return render_template(
        'language_program.html',
        programs=programs
    )

@app.route('/undergraduate-program/<int:university_id>')
def undergraduate_program(university_id):

    cur = conn.cursor()

    # =========================
    # Majors
    # =========================

    cur.execute("""
        SELECT
            department_name,
            major_name
        FROM majors
        WHERE university_id = %s
        ORDER BY department_name
    """, (university_id,))

    majors = cur.fetchall()

    # =========================
    # Tuition Fees
    # =========================

    cur.execute("""
        SELECT
            department_name,
            tuition_fee
        FROM tuition_fees
        WHERE university_id = %s
    """, (university_id,))

    tuition_fees = cur.fetchall()

    # =========================
    # Scholarships
    # =========================

    cur.execute("""
        SELECT
            score,
            percentage
        FROM scholarships
        WHERE university_id = %s
    """, (university_id,))

    scholarships = cur.fetchall()

    cur.close()

    return render_template(
        'undergraduate_program.html',
        majors=majors,
        tuition_fees=tuition_fees,
        scholarships=scholarships
    )


@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    recommendations = []
    program_type = None

    if request.method == 'POST':
        program_type = request.form.get('program_type')
        city = request.form['city']
        min_budget = request.form['min_budget']
        max_budget = request.form['max_budget']

        cur = conn.cursor()

        if program_type == 'language':
            # 1. 어학당 기준 추천 SQL (도시, 등록금 min~max 범위 조건)
            cur.execute("""
                SELECT 
                    u.id, 
                    u.uni_name, 
                    u.city, 
                    li.tuition_fee
                FROM universities u
                JOIN language_institutes li ON u.id = li.university_id
                WHERE LOWER(u.city) = LOWER(%s)
                  AND li.tuition_fee >= %s
                  AND li.tuition_fee <= %s
                ORDER BY li.tuition_fee ASC
            """, (city, min_budget, max_budget))
            
            # 템플릿에서 딕셔너리처럼 쉽게 꺼내 쓸 수 있도록 맵핑
            rows = cur.fetchall()
            recommendations = [
                {'id': r[0], 'uni_name': r[1], 'city': r[2], 'tuition_fee': r[3]} 
                for r in rows
            ]

        elif program_type == 'undergraduate':
            # 2. 학부 기준 추천 SQL (도시, 전공 학과별 등록금 min~max 범위, TOPIK 조건)
            topik = request.form['topik']
            major_keyword = request.form.get('major', '').strip()

            # 전공 키워드 입력 여부에 따른 동적 쿼리 구성
            query = """
                SELECT DISTINCT
                    u.id,
                    u.uni_name,
                    u.city,
                    u.topik_requirement,
                    m.department_name,
                    m.major_name,
                    t.tuition_fee
                FROM universities u
                JOIN majors m ON u.id = m.university_id
                JOIN tuition_fees t ON u.id = t.university_id AND m.department_name = t.department_name
                WHERE LOWER(u.city) = LOWER(%s)
                  AND t.tuition_fee >= %s
                  AND t.tuition_fee <= %s
                  AND u.topik_requirement <= %s
            """
            params = [city, min_budget, max_budget, topik]

            if major_keyword:
                query += " AND (m.major_name LIKE %s OR m.department_name LIKE %s)"
                params.append(f"%{major_keyword}%")
                params.append(f"%{major_keyword}%")

            query += " ORDER BY t.tuition_fee ASC"
            
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            recommendations = [
                {
                    'id': r[0], 'uni_name': r[1], 'city': r[2], 
                    'topik_requirement': r[3], 'department_name': r[4], 
                    'major_name': r[5], 'tuition_fee': r[6]
                } 
                for r in rows
            ]

        cur.close()

    return render_template(
        'recommendation.html',
        recommendations=recommendations,
        program_type=program_type
    )

@app.route('/qna')
def qna():
    cur = conn.cursor()

    # 질문 정보와 함께 답변(answer)의 개수를 COUNT하여 가져옵니다.
    cur.execute("""
        SELECT 
            q.id,
            q.title,
            q.created_at,
            COUNT(a.id) AS answer_count
        FROM questions q
        LEFT JOIN answer a ON q.id = a.question_id
        GROUP BY q.id, q.title, q.created_at
        ORDER BY q.created_at DESC
    """)

    questions_data = cur.fetchall()
    cur.close()

    questions = [
        {
            'id': row[0],
            'title': row[1],
            'created_at': row[2],
            'answer_count': row[3]
        } for row in questions_data
    ]

    return render_template(
        'qna.html',
        questions=questions
    )

@app.route('/create-question', methods=['GET', 'POST'])
def create_question():

    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO questions
            (title, content)
            VALUES (%s, %s)
        """, (
            title,
            content
        ))

        conn.commit()

        cur.close()

        return redirect('/qna')

    return render_template('create_question.html')

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question_detail(question_id):

    cur = conn.cursor()

    # answer submit
    if request.method == 'POST':

        answer_content = request.form['content']

        cur.execute("""
            INSERT INTO answer
            (question_id, content)
            VALUES (%s, %s)
        """, (
            question_id,
            answer_content
        ))

        conn.commit()

    # question
    cur.execute("""
        SELECT
            title,
            content,
            created_at
        FROM questions
        WHERE id = %s
    """, (question_id,))

    question = cur.fetchone()

    # answers
    cur.execute("""
        SELECT
            id, 
            content,
            created_at
        FROM answer
        WHERE question_id = %s
        ORDER BY created_at DESC
    """, (question_id,))

    answers = cur.fetchall()

    cur.close()

    return render_template(
        'question_detail.html',
        question=question,
        answers=answers, 
        question_id=question_id
    )

@app.route('/delete-question/<int:question_id>')
def delete_question(question_id):

    cur = conn.cursor()

    # delete answers first
    cur.execute("""
        DELETE FROM answer
        WHERE question_id = %s
    """, (question_id,))

    # delete question
    cur.execute("""
        DELETE FROM questions
        WHERE id = %s
    """, (question_id,))

    conn.commit()

    cur.close()

    return redirect('/qna')

@app.route('/delete-answer/<int:answer_id>')
def delete_answer(answer_id):

    cur = conn.cursor()

    # find question_id first
    cur.execute("""
        SELECT question_id
        FROM answer
        WHERE id = %s
    """, (answer_id,))

    result = cur.fetchone()

    if result:

        question_id = result[0]

        # delete answer
        cur.execute("""
            DELETE FROM answer
            WHERE id = %s
        """, (answer_id,))

        conn.commit()

        cur.close()

        return redirect(f'/question/{question_id}')

    cur.close()

    return redirect('/qna')




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

