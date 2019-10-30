from app import app
from flask import render_template
from flask import request, escape
import analytics

@app.route("/", methods=['GET'])
def main():
    return render_template("index.html")


@app.route("/analyze", methods=['GET'])
def analyze():
    field1 = escape(request.args.get('field1'))
    field2 = escape(request.args.get('field2'))
    table = analytics.contingency_table(field1, field2)

    return "analyzer"
