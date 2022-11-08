from os import path
from sqlite3 import connect
import json

with open(path.join(path.dirname(path.dirname(__file__)), "config.json")) as f:
    debug = json.load(f)['base']['debug']
if debug: dbName = "c4e_debug.db"
else: dbName = "c4e.db"
con = connect(path.join(path.dirname(__file__), dbName))
c = con.cursor()

def execute(querry, commit = False):
    c.execute(querry)
    if commit: con.commit()
    return c

def execute_one(querry, commit = False, index = 0):
    c = execute(querry, commit)
    return c.fetchone()[index]

def commit():
    con.commit()
