import json
import os
import urllib3
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from data_prepare import prepare_data

app = Flask(__name__)
api = Api(app)
CORS(app)


# class AvailableCitiesController(Resource):
#     f = open('data/availableCities.json')
#     availableCities = json.load(f)
#
#     def get(self):
#         return self.availableCities
#
#
# class CityModelController(Resource):
#     parser = reqparse.RequestParser()
#     parser.add_argument("selectedCity")
#     parser.add_argument("isCheck")
#     parser.add_argument("isCheckAll")
#
#     cityCenterCoords = json.load(open('data/cityCoordinates.json'))
#
#     def get(self, selectedCity):
#         args = self.parser.parse_args()
#         selected_city_model_path = os.path.join("data", "cityModels", selectedCity + ".json")
#         f = open(selected_city_model_path)
#         city_model = json.load(f)
#         return city_model


class FinishedJob(Resource):
    def get(self, job_id):
        http = urllib3.PoolManager()
        url = 'http://localhost:5000/v0/clusters/' + job_id + '/get-result'
        resp = http.request('GET', url)
        print(resp.data.decode('utf-8'))
        resp = prepare_data(json.loads(resp.data.decode('utf-8')))
        return resp

        # response_file_path = os.path.join("data", "response_" + job_id + "_processed.json")
        # f = open(response_file_path)
        # job = json.load(f)
        # return job

    # POST request notifying about the job being finished and saved in MongoDB
    def post(self, job_id):
        print(job_id + " received")
        return job_id + " received"


# api.add_resource(AvailableCitiesController, '/api/cities/')
# api.add_resource(CityModelController, '/api/city-model/<selectedCity>')
api.add_resource(FinishedJob, '/api/finished-job/<job_id>')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
