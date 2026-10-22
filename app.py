
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DATABASE = "students.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER NOT NULL,
                course TEXT NOT NULL
            )
        """)

        # Add new columns without deleting existing records.
        new_columns = {
            "phone": "TEXT",
            "address": "TEXT",
            "city": "TEXT",
            "state": "TEXT",
            "postal_code": "TEXT",
            "date_of_birth": "TEXT",
            "gender": "TEXT",
            "qualification": "TEXT",
            "enrollment_year": "INTEGER",
            "guardian_name": "TEXT",
            "emergency_contact": "TEXT"
        }

        existing_columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(students)"
            ).fetchall()
        }

        for column, data_type in new_columns.items():
            if column not in existing_columns:
                conn.execute(
                    f"ALTER TABLE students ADD COLUMN "
                    f"{column} {data_type}"
                )


@app.route("/")
def home():
    return render_template("welcome.html")

@app.route("/registration")
def registration_form():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    # Required fields
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    age_text = request.form.get("age", "").strip()
    course = request.form.get("course", "").strip()

    if not all([name, email, age_text, course]):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("home"))

    try:
        age = int(age_text)
        if not 1 <= age <= 120:
            raise ValueError
    except ValueError:
        flash("Please enter a valid age between 1 and 120.", "error")
        return redirect(url_for("home"))

    # Additional fields
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()
    city = request.form.get("city", "").strip()
    state = request.form.get("state", "").strip()
    postal_code = request.form.get("postal_code", "").strip()
    date_of_birth = request.form.get("date_of_birth", "").strip()
    gender = request.form.get("gender", "").strip()
    qualification = request.form.get("qualification", "").strip()
    enrollment_year_text = request.form.get("enrollment_year", "").strip()
    guardian_name = request.form.get("guardian_name", "").strip()
    emergency_contact = request.form.get("emergency_contact", "").strip()

    enrollment_year = None

    if enrollment_year_text:
        try:
            enrollment_year = int(enrollment_year_text)
            if not 1900 <= enrollment_year <= 2100:
                raise ValueError
        except ValueError:
            flash("Please enter a valid enrollment year.", "error")
            return redirect(url_for("home"))

    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO students (
                    name, email, age, course, phone, address,
                    city, state, postal_code, date_of_birth,
                    gender, qualification, enrollment_year,
                    guardian_name, emergency_contact
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, email, age, course, phone, address,
                city, state, postal_code, date_of_birth,
                gender, qualification, enrollment_year,
                guardian_name, emergency_contact
            ))

        flash("Student registered successfully!", "success")
        return redirect(url_for("view_students"))

    except sqlite3.Error:
        app.logger.exception("Could not save student")
        flash("There was a database error. Please try again.", "error")
        return redirect(url_for("home"))


@app.route("/students")
def view_students():
    with get_db_connection() as conn:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

    return render_template("students.html", students=students)


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    with get_db_connection() as conn:
        conn.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

    flash("Student record deleted.", "success")
    return redirect(url_for("view_students"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
