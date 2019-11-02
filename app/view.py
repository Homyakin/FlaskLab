from app import app
from flask import render_template
from flask import request, escape
from analytics import analyzer
from database import database

values = {'EmploymentStatus': ['Employed for wages', 'Self-employed business owner',
                               'Self-employed freelancer'],
          'Gender': ['male', 'female'],
          'JobWherePref': ['in an office with other developers', 'from home', 'no preference'],
          'SchoolDegree': ['some college credit, no degree', "bachelor's degree", "associate's degree",
                           'high school diploma or equivalent (GED)',
                           "master's degree (non-professional)", 'Ph.D.',
                           'trade, technical, or vocational training',
                           'professional degree (MBA, MD, JD, etc.)', 'some high school',
                           'no high school (secondary school)'],
          'LanguageAtHome': ['English', 'Khmer', 'Spanish', 'Greek', 'Hindi', 'Swedish', 'French',
                             'Serbo-Croatian', 'Bengali', 'Yue (Cantonese) Chinese', 'Tagalog', 'Tamil',
                             'Mandarin Chinese', 'Korean', 'Russian', 'German', 'Polish', 'Balochi',
                             'Malay Bhasa Indonesia', 'Italian', 'Dutch', 'Romanian', 'Arabic',
                             'Portuguese', 'Marathi', 'Persian', 'Hungarian', 'Turkish', 'Chinese', 'Danish',
                             'Croatian', 'Bulgarian', 'Slovak', 'Vietnamese', 'Japanese', 'Lithuanian',
                             'Cebuano', 'Assamese', 'Finnish', 'Serbian', 'Nepali', 'Malayalam', 'Gujarati',
                             'Hebrew', 'Amharic', 'Afrikaans', 'Uzbek', 'Tatar', 'Ukrainian', 'Igbo',
                             'Telugu', 'Indonesian', 'Haitian Creole', 'Central Bicolano', 'Punjabi',
                             'Norwegian', 'Urdu', 'Macedonian', 'Estonian', 'Egyptian Arabic', 'Thai',
                             'Bosnian', 'Romani', 'Adyghe', 'Somali', 'Czech', 'Zulu', 'Yoruba', 'Kurdish',
                             'Swahili', 'Maithili', 'Kannada', 'Wolof', 'Oriya', 'Odia (Oriya)', 'Hausa',
                             'Belarusian'],
          'EmploymentField': ['food and beverage', 'arts, entertainment, sports, or media', 'education',
                              'software development', 'law enforcement and fire and rescue',
                              'health care', 'architecture or physical engineering', 'transportation',
                              'finance', 'sales', 'office and administrative support',
                              'construction and extraction', 'software development and IT',
                              'farming, fishing, and forestry', 'legal']

          }


@app.route("/", methods=['GET'])
def main():
    return render_template("index.html")


@app.route("/analyze", methods=['GET'])
def analyze():
    field1 = escape(request.args.get('field1'))
    field2 = escape(request.args.get('field2'))
    with database.create_connection() as conn:
        data = database.get(conn, field1, field2)
        contingency_table = analyzer.get_contingency_table(data, field1, field2)
        statistic, expected_table = analyzer.get_statistic_and_expected_table(contingency_table)
        return render_template("analysis.html", field1=field1, field2=field2, contingency=contingency_table,
                               statistic=statistic, expected=expected_table)


def post_insert_data():
    form_result = {}
    if request.json is None:
        if (request.form.get('EmploymentField') not in values['EmploymentField']
                or request.form.get('EmploymentStatus') not in values['EmploymentStatus']
                or request.form.get('Gender') not in values['Gender']
                or request.form.get('LanguageAtHome') not in values['LanguageAtHome']
                or request.form.get('JobWherePref') not in values['JobWherePref']
                or request.form.get('SchoolDegree') not in values['SchoolDegree']):
            return render_template("insert.html", selected=values, message="Value error")
        form_result['EmploymentField'] = request.form.get('EmploymentField')
        form_result['EmploymentStatus'] = request.form.get('EmploymentStatus')
        form_result['Gender'] = request.form.get('Gender')
        form_result['LanguageAtHome'] = request.form.get('LanguageAtHome')
        form_result['JobWherePref'] = request.form.get('JobWherePref')
        form_result['SchoolDegree'] = request.form.get('SchoolDegree')
        try:
            form_result['Income'] = int(request.form.get('Income'))
        except ValueError:
            return render_template("insert.html", selected=values, message="Income must be int")
    else:
        form_result = request.json
    with database.create_connection() as conn:
        return render_template("insert.html", selected=values, message=database.insert(conn, form_result))


@app.route("/insert", methods=['POST', 'GET'])
def insert_data():
    if request.method == 'GET':
        return render_template("insert.html", selected=values)
    else:
        return post_insert_data()
