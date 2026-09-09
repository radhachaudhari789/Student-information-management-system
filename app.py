from flask import Flask, render_template, request
import sqlite3
import os
from supabase import create_client, Client
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SECRET_KEY"))

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
    students = supabase.table("students").select("class_name, percentage").execute().data

    total_students = len(students)

    classes = set()
    valid_percentages = []

    for student in students:
        class_name = student.get("class_name")
        percentage = student.get("percentage")

        if class_name:
            classes.add(class_name)

        try:
            valid_percentages.append(float(percentage))
        except (ValueError, TypeError):
            pass

    total_classes = len(classes)

    if valid_percentages:
        average_percentage = round(
            sum(valid_percentages) / len(valid_percentages), 2
        )
    else:
        average_percentage = 0

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

    admin_password = os.environ.get("ADMIN_PASSWORD")

    if username == "admin" and password == admin_password:
        return dashboard()

    return "Invalid username or password!"

@app.route("/search-student", methods=["GET", "POST"])
def search_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        class_name = request.form.get("class_name", "").strip()
        roll_number = request.form.get("roll_number", "").strip()

        if name:
            result = supabase.table("students").select("*").ilike(
                "name", f"%{name}%"
            ).limit(1).execute()

        elif class_name and roll_number:
            result = supabase.table("students").select("*").eq(
                "class_name", class_name
            ).eq(
                "roll_number", roll_number
            ).limit(1).execute()

        else:
            return render_template(
                "search_student.html",
                error="Please enter a student name or both class and roll number."
            )

        if result.data:
            student_data = result.data[0]

            student = (
                student_data.get("id"),
                student_data.get("roll_number"),
                student_data.get("name"),
                student_data.get("class_name"),
                student_data.get("father_name"),
                student_data.get("mother_name"),
                student_data.get("parent_contact"),
                student_data.get("percentage"),
                student_data.get("date_of_birth"),
                student_data.get("address")
            )

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
    result = supabase.table("students").select("*").eq(
        "id", student_id
    ).single().execute()

    student_data = result.data

    student = (
        student_data.get("id"),
        student_data.get("roll_number"),
        student_data.get("name"),
        student_data.get("class_name"),
        student_data.get("father_name"),
        student_data.get("mother_name"),
        student_data.get("parent_contact"),
        student_data.get("percentage"),
        student_data.get("date_of_birth"),
        student_data.get("address")
    )

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

    supabase.table("students").update({
        "roll_number": roll_number,
        "name": name,
        "class_name": class_name,
        "father_name": father_name,
        "mother_name": mother_name,
        "parent_contact": parent_contact,
        "percentage": percentage,
        "date_of_birth": date_of_birth,
        "address": address
    }).eq("id", student_id).execute()

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
    supabase.table("students").delete().eq(
        "id", student_id
    ).execute()

    return "Student deleted successfully!"

@app.route("/view-students")
def view_students():
    data = supabase.table("students").select("*").execute().data

    students = []

    for student in data:
        students.append((
            student.get("id"),
            student.get("roll_number"),
            student.get("name"),
            student.get("class_name"),
            student.get("father_name"),
            student.get("mother_name"),
            student.get("parent_contact"),
            student.get("percentage"),
            student.get("date_of_birth"),
            student.get("address")
        ))

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
    data = supabase.table("students").select("*").eq(
        "class_name", class_name
    ).execute().data

    students = []

    for student in data:
        students.append((
            student.get("id"),
            student.get("roll_number"),
            student.get("name"),
            student.get("class_name"),
            student.get("father_name"),
            student.get("mother_name"),
            student.get("parent_contact"),
            student.get("percentage"),
            student.get("date_of_birth"),
            student.get("address")
        ))

    return render_template(
        "class_students.html",
        students=students,
        class_name=class_name
    )
@app.route("/top-students")
def top_students():
    data = supabase.table("students").select("*").execute().data

    students = []

    for student in data:
        percentage = student.get("percentage")

        if percentage is not None and str(percentage).strip() != "":
            try:
                percentage_value = float(percentage)
            except ValueError:
                continue

            students.append((
                student.get("id"),
                student.get("roll_number"),
                student.get("name"),
                student.get("class_name"),
                student.get("father_name"),
                student.get("mother_name"),
                student.get("parent_contact"),
                student.get("percentage"),
                student.get("date_of_birth"),
                student.get("address")
            ))

    students.sort(
        key=lambda student: (
            int(student[3]) if str(student[3]).isdigit() else 999,
            -float(student[7])
        )
    )

    top_students_by_class = {}

    for student in students:
        class_name = student[3]

        if class_name not in top_students_by_class:
            top_students_by_class[class_name] = []

        if len(top_students_by_class[class_name]) < 3:
            top_students_by_class[class_name].append(student)

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

    supabase.table("students").insert({
        "roll_number": roll_number,
        "name": name,
        "class_name": class_name,
        "father_name": father_name,
        "mother_name": mother_name,
        "parent_contact": parent_contact,
        "percentage": percentage,
        "date_of_birth": date_of_birth,
        "address": address
    }).execute()

    return render_template(
        "add_student.html",
        message="Student added successfully!"
    )

init_db()

if __name__ == "__main__":
    app.run()