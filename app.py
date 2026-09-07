from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT,
            name TEXT,
            class_name TEXT,
            father_name TEXT,
            mother_name TEXT,
            parent_contact TEXT,
            percentage TEXT,
            date_of_birth TEXT,
address TEXT
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT class_name)
        FROM students
        WHERE class_name IS NOT NULL AND class_name != ''
    """)
    total_classes = cursor.fetchone()[0]

    cursor.execute("SELECT percentage FROM students")
    percentages = cursor.fetchall()

    valid_percentages = []

    for row in percentages:
        try:
            value = float(row[0])
            valid_percentages.append(value)
        except (ValueError, TypeError):
            pass

    if valid_percentages:
        average_percentage = round(
            sum(valid_percentages) / len(valid_percentages), 2
        )
    else:
        average_percentage = 0

    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_classes=total_classes,
        average_percentage=average_percentage
    )


@app.route("/logout")
def logout():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "REMOVED":
        return dashboard()

    return "Invalid username or password!"
@app.route("/search-student", methods=["GET", "POST"])
def search_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        class_name = request.form.get("class_name", "").strip()
        roll_number = request.form.get("roll_number", "").strip()

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        if name:
            cursor.execute(
                "SELECT * FROM students WHERE name LIKE ?",
                ("%" + name + "%",)
            )

        elif class_name and roll_number:
            cursor.execute(
                "SELECT * FROM students WHERE class_name = ? AND roll_number = ?",
                (class_name, roll_number)
            )

        else:
            conn.close()
            return render_template(
                "search_student.html",
                error="Please enter a student name or both class and roll number."
            )

        student = cursor.fetchone()
        conn.close()

        if student:
            return render_template(
                "student_details.html",
                student=student
            )

        return render_template(
            "search_student.html",
            error="Student not found. Please check the entered details."
        )

    return render_template("search_student.html")
@app.route("/edit-student/<int:student_id>")
def edit_student(student_id):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )

@app.route("/update-student/<int:student_id>", methods=["POST"])
def update_student(student_id):
    roll_number = request.form["roll_number"]
    name = request.form["name"]
    class_name = request.form["class_name"]
    father_name = request.form["father_name"]
    mother_name = request.form["mother_name"]
    parent_contact = request.form["parent_contact"]
    percentage = request.form["percentage"]
    date_of_birth = request.form["date_of_birth"]
    address = request.form["address"]

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students
        SET roll_number = ?,
            name = ?,
            class_name = ?,
            father_name = ?,
            mother_name = ?,
            parent_contact = ?,
            percentage = ?,
            date_of_birth = ?,
            address = ?
        WHERE id = ?
    """, (
        roll_number,
        name,
        class_name,
        father_name,
        mother_name,
        parent_contact,
        percentage,
        date_of_birth,
        address,
        student_id
    ))

    conn.commit()
    conn.close()

    return render_template(
        "edit_student.html",
        student=(
            student_id,
            roll_number,
            name,
            class_name,
            father_name,
            mother_name,
            parent_contact,
            percentage,
            date_of_birth,
            address
        ),
        message="Student updated successfully!"
    )

@app.route("/delete-student/<int:student_id>")
def delete_student(student_id):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    return "Student deleted successfully!"


@app.route("/view-students")
def view_students():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template(
        "view_students.html",
        students=students
    )


@app.route("/add-student")
def add_student():
    return render_template("add_student.html")


@app.route("/class-wise")
def class_wise():
    classes = list(range(1, 11))

    return render_template(
        "class_wise.html",
        classes=classes
    )


@app.route("/class-wise/<class_name>")
def class_wise_students(class_name):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE class_name = ?",
        (class_name,)
    )

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "class_students.html",
        students=students,
        class_name=class_name
    )
@app.route("/top-students")
def top_students():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM students
        WHERE percentage IS NOT NULL
        AND percentage != ''
        ORDER BY CAST(class_name AS INTEGER),
                 CAST(percentage AS REAL) DESC
    """)

    students = cursor.fetchall()
    conn.close()

    top_students_by_class = {}

    for student in students:
        class_name = student[3]

        if class_name not in top_students_by_class:
            top_students_by_class[class_name] = []

        if len(top_students_by_class[class_name]) < 3:
            top_students_by_class[class_name].append(student)

    # Arrange classes numerically: 1, 2, 3 ... 10
    top_students_by_class = dict(
        sorted(
            top_students_by_class.items(),
            key=lambda item: int(item[0])
        )
    )

    return render_template(
        "top_students.html",
        top_students_by_class=top_students_by_class
    )

@app.route("/save-student", methods=["POST"])
def save_student():
    roll_number = request.form["roll_number"]
    name = request.form["name"]
    class_name = request.form["class_name"]
    father_name = request.form["father_name"]
    mother_name = request.form["mother_name"]
    parent_contact = request.form["parent_contact"]
    percentage = request.form["percentage"]
    date_of_birth = request.form["date_of_birth"]
    address = request.form.get("address", "")

    # Validate parent contact
    if parent_contact and (
        not parent_contact.isdigit() or len(parent_contact) != 10
    ):
        return render_template(
            "add_student.html",
            error="Parent contact must be exactly 10 digits."
        )

    # Validate percentage
    if percentage:
        try:
            percentage_value = float(percentage)

            if percentage_value < 0 or percentage_value > 100:
                return render_template(
                    "add_student.html",
                    error="Percentage must be between 0 and 100."
                )

        except ValueError:
            return render_template(
                "add_student.html",
                error="Please enter a valid percentage."
            )

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO students
    (roll_number, name, class_name, father_name,
     mother_name, parent_contact, percentage, date_of_birth,address)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
""", (
    roll_number,
    name,
    class_name,
    father_name,
    mother_name,
    parent_contact,
    percentage,
    date_of_birth,
    address
))

    conn.commit()
    conn.close()

    return render_template(
        "add_student.html",
        message="Student added successfully!"
    )


if __name__ == "__main__":
    init_db()
    app.run()