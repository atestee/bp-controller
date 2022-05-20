import json
import uuid
from uuid import UUID
from datetime import datetime
import bson
import requests
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from pymongo import MongoClient
from flask_cors import CORS

import data_prepare
from data_prepare import prepare_data
import db_config as mongo_utils
import db_utils

app = Flask(__name__)
api = Api(app)
CORS(app)

mongo_client = MongoClient(mongo_utils.MONGO_URL)
database = mongo_utils.MONGO_DATABASE


class AvailableCitiesController(Resource):
    # GET /api/cities
    # responds with the list of available
    def get(self):
        return db_utils.find_available_cites()


class CityModelController(Resource):
    # GET /api/city-model/<selected-city>
    def get(self, selected_city):
        return db_utils.find_one_city_model_by_name(selected_city)


class JobListController(Resource):
    # POST /api/job
    def post(self):
        startTime = datetime.now()
        req = request.get_json()
        req["excludedGeography"] = json.loads(req["excludedGeography"])
        req = data_prepare.replace_route_identification(req)
        req_for_analysis = req.copy()
        req_for_analysis.pop("nbins")
        req_for_analysis.pop("jobName")
        req_for_analysis.pop("centerCoords")
        req_for_analysis.pop("city")
        res = requests.post('http://localhost:5001/v0/clusters/new-job', json=req_for_analysis)
        job_id = res.json()["jobId"]
        parameters = {
            "minWalkingDistanceMeters": req["minWalkingDistanceMeters"],
            "maxDrivingDistanceMeters": req["maxDrivingDistanceMeters"],
            "maxTaxiRideDurationMinutes": req["maxTaxiRideDurationMinutes"],
            "numberOfPTStopsClustering": req["numberOfPTStopsClustering"]
        }

        job_information = {
            "jobId": bson.Binary.from_uuid(UUID(job_id), uuid_representation=3),
            "jobName": req["jobName"],
            "startTime": startTime,
            "endTime": None,
            "status": "RUNNING",
            "parameters": parameters
        }

        job_data = {
            "jobId": bson.Binary.from_uuid(UUID(job_id), uuid_representation=3),
            "jobName": req["jobName"],
            "parameters": parameters,
            "nbins": req["nbins"],
            "centerCoords": req["centerCoords"],
            "city": req["city"]
        }

        db_utils.insert_one_job_information(job_information)
        db_utils.insert_one_job_result(job_data)

        return res.json()


class JobController(Resource):
    # GET request serving the job results corresponding to job_id
    def get(self, job_id):
        return prepare_data(db_utils.find_one_job_result_by_id(job_id))

    # POST request notifying about the job being finished and saved in MongoDB
    def post(self, job_id):
        end_time = datetime.now()
        # modify the status and endTime
        db_utils.update_job_information_end_time_and_status(job_id, end_time)

        return jsonify({"jobId": job_id})


class JobInformationController(Resource):
    def get(self):
        result = db_utils.find_all_job_information()
        result_list = list(result)
        job_management_array = []
        for res in result_list:
            job_management_array.append({
                "jobId": str(res["jobId"].as_uuid(3)),
                "jobName": res["jobName"],
                "startTime": str(res["startTime"]),
                "endTime": str(res["endTime"]),
                "status": res["status"],
                "parameters": data_prepare.modify_transit_types(res["parameters"])
            })

        return job_management_array[::-1]


api.add_resource(AvailableCitiesController, '/api/cities/')
api.add_resource(CityModelController, '/api/city-model/<selected_city>')
api.add_resource(JobController, '/api/job/<job_id>')
api.add_resource(JobListController, '/api/job')
api.add_resource(JobInformationController, '/api/job-information')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

