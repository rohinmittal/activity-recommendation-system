from flask import Flask
from pymongo import MongoClient
import json, pickle

client = MongoClient()
db = client.data
db.data.remove()
db.users.remove()
json_data = json.loads(open('./files/output.json').read())
db.data.insert_many([json_data[i] for i in range(len(json_data))])
f = open('./files/classifier.pickle', 'rb')
classifier = pickle.load(f)
f.close()

app = Flask(__name__)
import application.views
