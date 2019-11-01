from app import app
from flask import render_template
from flask import request, escape
from analytics import analyzer
from database import database


@app.route("/", methods=['GET'])
def main():
    return render_template("index.html")


@app.route("/analyze", methods=['GET'])
def analyze():
    field1 = escape(request.args.get('field1'))
    field2 = escape(request.args.get('field2'))
    contingency_table = analyzer.get_contingency_table(field1, field2)
    statistic, expected_table = analyzer.get_statistic_and_expected_table(field1, field2, contingency_table)
    return render_template("analysis.html", field1=field1, field2=field2, contingency=contingency_table,
                           statistic=statistic, expected=expected_table)


def post_insert_data():
    form_result = {}
    if request.json is None:
        form_result['EmploymentField'] = request.form.get('EmploymentField')
        form_result['EmploymentStatus'] = request.form.get('EmploymentStatus')
        form_result['Gender'] = request.form.get('Gender')
        form_result['LanguageAtHome'] = request.form.get('LanguageAtHome')
        form_result['JobWherePref'] = request.form.get('JobWherePref')
        form_result['SchoolDegree'] = request.form.get('SchoolDegree')
        form_result['Income'] = request.form.get('Income')
    else:
        form_result = request.json
    print(form_result)
    return render_template("insert.html", message=database.insert(form_result))


@app.route("/insert", methods=['POST', 'GET'])
def insert_data():
    if request.method == 'GET':
        return render_template("insert.html")
    else:
        return post_insert_data()
