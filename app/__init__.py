from flask import Flask
import pandas as pd

app = Flask(__name__)
data = pd.read_csv('./data/data.csv')
