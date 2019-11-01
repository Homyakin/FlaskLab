from flask import Flask
from flask_cachebuster import CacheBuster

app = Flask(__name__)
config = {'extensions': ['.js', '.css', '.csv'], 'hash_size': 5}
cache_buster = CacheBuster(config=config)
cache_buster.init_app(app)
