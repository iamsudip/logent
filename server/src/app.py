#!/usr/bin/env python


from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from pymongo import MongoClient


app = Flask(__name__)
api = Api(app)
client = MongoClient()

class AggregateLogs(Resource):
    def get(self, query):
        return {'hello': 'world'}

    def post(self):
        data = request.get_json(force=True)
        print data

api.add_resource(AggregateLogs, '/')


if __name__ == '__main__':
    app.run(debug=True)
