from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB_NAME = r"C:\Users\HP\OneDrive\Desktop\advance python\LMS2.db"

# Database helper
def query_db(query, args=(), one=False):
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row  # column names enable
    cur = con.cursor()
    cur.execute(query, args)
    data = cur.fetchall()
    con.commit()
    con.close()
    if one:
        return dict(data[0]) if data else None
    else:
        return [dict(row) for row in data]

# ------------------ Teachers ------------------

@app.route("/teachers")
def teachers():
    data = query_db("SELECT * FROM teacher")
    return render_template("teachers.html", data=data)

@app.route("/add_teacher", methods=["GET", "POST"])
def add_teacher():
    if request.method == "POST":
        teacher_id = request.form["teacher_id"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        gender = request.form["gender"]
        dob = request.form["date_of_birth"]
        hire_date = request.form["hire_date"]
        subject = request.form["subject"]
        phone = request.form["phone_number"]
        email = request.form["email"]
        salary = request.form["salary"]

        query_db(
            """INSERT INTO teacher 
               (teacher_id, first_name, last_name, gender, date_of_birth, hire_date, subject, phone_number, email, salary) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (teacher_id, first_name, last_name, gender, dob, hire_date, subject, phone, email, salary),
        )
        return redirect(url_for("teachers"))
    return render_template("add_teacher.html")

@app.route("/update_teacher/<teacher_id>", methods=["GET", "POST"])
def update_teacher(teacher_id):
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        gender = request.form["gender"]
        dob = request.form["date_of_birth"]
        hire_date = request.form["hire_date"]
        subject = request.form["subject"]
        phone = request.form["phone_number"]
        email = request.form["email"]
        salary = request.form["salary"]

        query_db(
            """UPDATE teacher 
               SET first_name=?, last_name=?, gender=?, date_of_birth=?, hire_date=?, subject=?, phone_number=?, email=?, salary=? 
               WHERE teacher_id=?""",
            (first_name, last_name, gender, dob, hire_date, subject, phone, email, salary, teacher_id),
        )
        return redirect(url_for("teachers"))

    teacher = query_db("SELECT * FROM teacher WHERE teacher_id=?", (teacher_id,), one=True)
    return render_template("update_teacher.html", teacher=teacher)

@app.route("/delete_teacher/<teacher_id>")
def delete_teacher(teacher_id):
    query_db("DELETE FROM teacher WHERE teacher_id=?", (teacher_id,))
    return redirect(url_for("teachers"))

# ------------------ Students ------------------

@app.route("/students")
def students():
    data = query_db("SELECT * FROM student_records")
    return render_template("students.html", data=data)

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        gender = request.form["gender"]
        race = request.form["race_ethnicity"]
        parent_edu = request.form["parental_level_of_education"]
        lunch = request.form["lunch"]
        test_prep = request.form["test_preparation_course"]
        math = request.form["math_score"]
        reading = request.form["reading_score"]
        writing = request.form["writing_score"]
        teacher_id = request.form["teacher_id"]

        query_db(
            """INSERT INTO student_records 
               (gender, race_ethnicity, parental_level_of_education, lunch, test_preparation_course, math_score, reading_score, writing_score, teacher_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (gender, race, parent_edu, lunch, test_prep, math, reading, writing, teacher_id),
        )
        return redirect(url_for("students"))
    return render_template("add_student.html")

@app.route("/update_student/<int:student_id>", methods=["GET", "POST"])
def update_student(student_id):
    if request.method == "POST":
        gender = request.form["gender"]
        race = request.form["race_ethnicity"]
        parent_edu = request.form["parental_level_of_education"]
        lunch = request.form["lunch"]
        test_prep = request.form["test_preparation_course"]
        math = request.form["math_score"]
        reading = request.form["reading_score"]
        writing = request.form["writing_score"]
        teacher_id = request.form["teacher_id"]

        query_db(
            """UPDATE student_records 
               SET gender=?, race_ethnicity=?, parental_level_of_education=?, lunch=?, test_preparation_course=?, math_score=?, reading_score=?, writing_score=?, teacher_id=? 
               WHERE id=?""",
            (gender, race, parent_edu, lunch, test_prep, math, reading, writing, teacher_id, student_id),
        )
        return redirect(url_for("students"))

    student = query_db("SELECT * FROM student_records WHERE id=?", (student_id,), one=True)
    return render_template("update_student.html", student=student)

@app.route("/delete_student/<int:student_id>")
def delete_student(student_id):
    query_db("DELETE FROM student_records WHERE id=?", (student_id,))
    return redirect(url_for("students"))
@app.route("/classes")
def classes():
    query = """
        SELECT 
            c.class_id,
            c.class_name,
            c.section,
            t.first_name || ' ' || t.last_name AS teacher_name
        FROM class c
        JOIN teacher t ON c.teacher_id = t.teacher_id
    """
    data = query_db(query)
    return render_template("classes.html", data=data)



# ------------------ Run Custom SQL ------------------
def run_select(query):
    # --- safety: sirf SELECT allow ---
    q = query.strip()
    if not q.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")
    if ";" in q[:-1]:  # allow only trailing ;
        raise ValueError("Multiple statements are not allowed.")

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(q)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    con.close()
    return cols, rows


@app.route("/run_query", methods=["GET", "POST"])
def run_query():
    columns, rows, error, query = [], [], None, ""
    if request.method == "POST":
        query = request.form.get("query", "")
        try:
            columns, rows = run_select(query)
        except Exception as e:
            error = str(e)
    return render_template("run_query.html", columns=columns, rows=rows, error=error, query=query)


# ------------------ Main ------------------

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
