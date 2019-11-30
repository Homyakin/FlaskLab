from app import app
from flask import render_template
from flask import request, escape
from analytics import analyzer
from database import database
import os

ANOVA_COLS = ['CityPopulation', 'EmploymentStatus',
              'Gender', 'HasDebt', 'JobPref', 'JobWherePref',
              'MaritalStatus', 'SchoolDegree']

ELLIPSE_COLS = ['FixedAcidity', 'VolatileAcidity', 'CitricAcid',
                'ResidualSugar', 'Chlorides', 'FreeSulfurDioxide',
                'TotalSulfurDioxide', 'Density', 'PH',
                'Sulphates', 'Alcohol']

VALUES = {'EmploymentStatus': ['Employed for wages',
                               'Self-employed business owner',
                               'Self-employed freelancer'],
          'Gender': ['male', 'female'],
          'JobWherePref': ['in an office with other developers', 'from home',
                           'no preference'],
          'SchoolDegree': ['some college credit, no degree',
                           'bachelor\'s degree',
                           'associate\'s degree',
                           'high school diploma or equivalent (GED)',
                           "master's degree (non-professional)", 'Ph.D.',
                           'trade, technical, or vocational training',
                           'professional degree (MBA, MD, JD, etc.)',
                           'some high school',
                           'no high school (secondary school)'],
          'LanguageAtHome': ['English', 'Khmer', 'Spanish', 'Greek',
                             'Hindi', 'Swedish', 'French',
                             'Serbo-Croatian', 'Bengali',
                             'Yue (Cantonese) Chinese', 'Tagalog', 'Tamil',
                             'Mandarin Chinese', 'Korean', 'Russian',
                             'German', 'Polish', 'Balochi',
                             'Malay Bhasa Indonesia', 'Italian', 'Dutch',
                             'Romanian', 'Arabic', 'Portuguese', 'Marathi',
                             'Persian', 'Hungarian', 'Turkish', 'Chinese',
                             'Danish', 'Croatian', 'Bulgarian', 'Slovak',
                             'Vietnamese', 'Japanese', 'Lithuanian', 'Cebuano',
                             'Assamese', 'Finnish', 'Serbian', 'Nepali',
                             'Malayalam', 'Gujarati', 'Hebrew', 'Amharic',
                             'Afrikaans', 'Uzbek', 'Tatar', 'Ukrainian', 'Igbo',
                             'Telugu', 'Indonesian', 'Haitian Creole',
                             'Central Bicolano', 'Punjabi', 'Norwegian', 'Urdu',
                             'Macedonian', 'Estonian', 'Egyptian Arabic',
                             'Thai', 'Bosnian', 'Romani', 'Adyghe', 'Somali',
                             'Czech', 'Zulu', 'Yoruba', 'Kurdish', 'Swahili',
                             'Maithili', 'Kannada', 'Wolof', 'Oriya',
                             'Odia (Oriya)', 'Hausa', 'Belarusian'],
          'EmploymentField': ['food and beverage',
                              'arts, entertainment, sports, or media',
                              'education', 'software development',
                              'law enforcement and fire and rescue',
                              'health care',
                              'architecture or physical engineering',
                              'transportation',
                              'finance', 'sales',
                              'office and administrative support',
                              'construction and extraction',
                              'software development and IT',
                              'farming, fishing, and forestry', 'legal'],
          'CityPopulation': ['between 100,000 and 1 million',
                             'more than 1 million',
                             'less than 100,000'],
          'HasDebt': ['1', '0'],
          'JobPref': ['freelance ', 'work for a startup',
                      'start your own business',
                      'work for a medium-sized company',
                      'work for a multinational corporation'],
          'MaritalStatus': ['married or domestic partnership',
                            'single, never married',
                            'separated', 'divorced', 'widowed'],


          }

old_files = []


def clear_old_files(fn):
    def wrapper(*args, **kwargs):
        for i in old_files:
            os.remove(i)
        old_files.clear()
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper


@app.route("/", methods=['GET'])
@clear_old_files
def main():
    return render_template("index.html")


@app.route("/analyze", methods=['GET'])
@clear_old_files
def analyze():
    field1 = escape(request.args.get('field1'))
    field2 = escape(request.args.get('field2'))
    with database.create_connection() as conn:
        data = database.get(conn, [field1, field2])
        contingency_table = analyzer.get_contingency_table(data,
                                                           field1,
                                                           field2)
        statistic, expected_table = analyzer.get_statistic_and_expected_table(contingency_table)
        return render_template("analysis.html",
                               field1=field1,
                               field2=field2,
                               contingency=contingency_table,
                               statistic=statistic,
                               expected=expected_table)


@app.route("/anova", methods=['GET'])
@clear_old_files
def choose_anova():
    return render_template("anova.html", cols=ANOVA_COLS)


@app.route("/anova_result", methods=['GET'])
@clear_old_files
def launch_anova():
    with database.create_connection() as conn:
        cols = []
        for i in ANOVA_COLS:
            if i in request.args:
                cols.append(i)
        cols.append('Income')
        data = database.get(conn, cols)
        anova_result = analyzer.anova_cols(data, cols)
        return render_template("anova_result.html", result=anova_result.split('\n'))


def post_insert_data():
    form_result = {}
    if request.json is None:
        if (request.form.get('EmploymentField') not in VALUES['EmploymentField']
                or request.form.get('EmploymentStatus') not in VALUES['EmploymentStatus']
                or request.form.get('Gender') not in VALUES['Gender']
                or request.form.get('LanguageAtHome') not in VALUES['LanguageAtHome']
                or request.form.get('JobWherePref') not in VALUES['JobWherePref']
                or request.form.get('SchoolDegree') not in VALUES['SchoolDegree']
                or request.form.get('CityPopulation') not in VALUES['CityPopulation']
                or request.form.get('MaritalStatus') not in VALUES['MaritalStatus']
                or request.form.get('JobPref') not in VALUES['JobPref']
                or request.form.get('HasDebt') not in VALUES['HasDebt']):
            return render_template("insert.html", selected=VALUES, message="Value error")
        form_result['EmploymentField'] = request.form.get('EmploymentField')
        form_result['EmploymentStatus'] = request.form.get('EmploymentStatus')
        form_result['Gender'] = request.form.get('Gender')
        form_result['LanguageAtHome'] = request.form.get('LanguageAtHome')
        form_result['JobWherePref'] = request.form.get('JobWherePref')
        form_result['SchoolDegree'] = request.form.get('SchoolDegree')
        form_result['CityPopulation'] = request.form.get('CityPopulation')
        form_result['HasDebt'] = request.form.get('HasDebt')
        form_result['JobPref'] = request.form.get('JobPref')
        form_result['MaritalStatus'] = request.form.get('MaritalStatus')
        try:
            form_result['Income'] = int(request.form.get('Income'))
        except ValueError:
            return render_template("insert.html",
                                   selected=VALUES,
                                   message="Income must be int")
    else:
        form_result = request.json
    with database.create_connection() as conn:
        return render_template("insert.html",
                               selected=VALUES,
                               message=database.insert(conn, form_result))


@app.route("/insert", methods=['POST', 'GET'])
@clear_old_files
def insert_data():
    if request.method == 'GET':
        return render_template("insert.html", selected=VALUES)
    else:
        return post_insert_data()


@app.route("/update")
@clear_old_files
def update_data():
    return analyzer.update_data()


@app.route("/ellipse", methods=['GET'])
@clear_old_files
def choose_ellipse():
    return render_template("ellipse.html", cols=ELLIPSE_COLS)


@app.route("/ellipse_result", methods=['GET'])
@clear_old_files
def launch_drow_ellipse():
    x = request.args.get('first')
    y = request.args.get('second')
    if x is None or y is None or x not in ELLIPSE_COLS or y not in ELLIPSE_COLS:
        return render_template("ellipse.html", cols=ELLIPSE_COLS)
    fname = analyzer.draw_ellipse(x, y)
    old_files.append(fname)
    return render_template("ellipse_result.html", fname=fname)


@app.route("/pca")
@clear_old_files
def launch_pca():
    u, n_comp = analyzer.define_equation()
    equations = analyzer.print_latex(u)
    return render_template("pca.html", equations=equations, n_comp=n_comp)
