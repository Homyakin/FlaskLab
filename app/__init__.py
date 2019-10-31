from flask import Flask
import pandas as pd
from flask_cachebuster import CacheBuster

app = Flask(__name__)
config = {'extensions': ['.js', '.css', '.csv'], 'hash_size': 5}
cache_buster = CacheBuster(config=config)
cache_buster.init_app(app)
data = pd.read_csv('./app/data/data.csv')
data = data[['EmploymentField', 'EmploymentStatus',
             'Gender', 'LanguageAtHome',
             'JobWherePref', 'SchoolDegree',
             'Income']]
data = data[data['Gender'].isin(['male', 'female'])]
data.dropna(inplace=True)
