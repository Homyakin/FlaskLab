from app import app
from flask import render_template
from flask import request, escape
from analytics import analyzer


@app.route("/", methods=['GET'])
def main():
    return render_template("index.html")


@app.route("/analyze", methods=['GET'])
def analyze():
    field1 = escape(request.args.get('field1'))
    field2 = escape(request.args.get('field2'))
    contingency_table = analyzer.get_contingency_table(field1, field2)
    # expected_table = analyzer.get_expected_table(field1, field2)
    return render_template("analysis.html", field1=field1, field2=field2, contingency=contingency_table)

