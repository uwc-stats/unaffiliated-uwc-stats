from flask import flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from fuzzywuzzy import fuzz

from iso3166 import countries

import math
import sqlite3

import pandas as pd
import json
import plotly
import plotly.express as px

from uwc_back import list_uwc, list_countries, list_school




from flask import Markup










from uwc_back import blur


filter_query = """
    SELECT * FROM scholars
"""

conn_scholars = sqlite3.connect('scholars.db')
c_scholars = conn_scholars.cursor()
sql_scholars = c_scholars.execute(filter_query).fetchall()

scholars = []
for scholar in sql_scholars:
    scholars.append(list(scholar))
scholars = blur(scholars)

print(scholars)
