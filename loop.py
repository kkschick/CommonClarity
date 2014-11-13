from flask import Flask, make_response, send_file, session, request, redirect
import api
import json
import os
from werkzeug import secure_filename

UPLOAD_FOLDER = "./static/uploads/"
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.secret_key = '24KJSF98325KJLSDF972saf29832LFjasf87FZKFJL78f7ds98FSDKLF'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/test/")
def test():
    return _convert_to_JSON(api.get_one_student_data_by_test(1))


@app.route("/")
def index():
    return send_file("templates/index.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        csvfile = request.files['csvfile']
        if csvfile and allowed_file(csvfile.filename):
            filename = secure_filename(csvfile.filename)
            file_path = app.config['UPLOAD_FOLDER'] + filename
            csvfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    test_name = request.form.get("test_name")
    test_date = request.form.get("test_date")
    cohort_id = request.form["cohort"]
    api.parse_CSV(file_path, test_name, test_date, cohort_id)
    return redirect("/#/reports/")

def _convert_to_JSON(result):
    """Convert result object to a JSON web request."""

    response = make_response(json.dumps(result))
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.mimetype = "application/json"
    return response

@app.route("/api/addclass/", methods=['POST'])
def addclass():
    class_info = json.loads(request.data)
    cohort_name = (class_info.get("cohort")).get("name")
    teacher_id = session['user']
    cohort_id = api.add_new_cohort(cohort_name, teacher_id)
    list_of_students = class_info.get("students")
    for student in list_of_students:
        user_type = "student"
        first_name = student.get("first_name")
        last_name = student.get("last_name")
        username = student.get("username")
        password = student.get("password")
        student_id = api.create_student(user_type, first_name, last_name, username, password)
        api.add_student_to_cohort(student_id, cohort_id)
    return "Success"

@app.route("/api/getclasses/")
def get_cohorts():
    teacher_id = session['user']
    cohorts = api.get_teacher_cohorts(teacher_id)
    all_cohorts = []
    for cohort in cohorts:
        full_class = {}
        cohort_id = cohort.id
        students = api.get_students_in_cohort(cohort_id)
        full_class["cohort_id"] = cohort_id
        full_class["name"] = cohort.name
        full_class["students"] = students
        all_cohorts.append(full_class)
    return _convert_to_JSON(all_cohorts)

@app.route("/api/allcohortcounts/")
def all_cohort_data():
    teacher_id = session['user']
    response = api.get_all_cohort_data_by_test(teacher_id)
    return _convert_to_JSON(response)

@app.route("/api/singlecohortcounts/")
def single_cohort_data():
    response = api.get_one_cohort_data_by_test(1)
    return _convert_to_JSON(response)

@app.route("/api/singlestudentcounts/")
def single_student_data():
    response = api.get_one_student_data_by_test(2)
    return _convert_to_JSON(response)

@app.route("/api/signup/", methods=['POST'])
def adduser():
    new_user = json.loads(request.data)
    user_type = "teacher"
    first_name = new_user.get("first_name")
    last_name = new_user.get("last_name")
    email = new_user.get("email")
    username = new_user.get("username")
    password = new_user.get("password")
    api.create_teacher_user(user_type, first_name, last_name, email, username, password)
    return "Success"

@app.route("/api/login/", methods=['POST'])
def loginuser():
    user_to_login = json.loads(request.data)
    username = user_to_login.get("username")
    password = user_to_login.get("password")
    user = api.get_user(username, password)
    session['user'] = user.id
    return "Success"


@app.route("/api/logout/", methods=['POST'])
def process_logout():
    api.logout()


if __name__ == "__main__":
    app.run(debug = True)