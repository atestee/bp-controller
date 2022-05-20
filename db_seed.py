import json
import os
from datetime import datetime
from uuid import UUID
import bson as bson

from db_utils import mongo_client, database
from db_config import Collection


def read_data(file_name):
    f = open(file_name, "r+", encoding="utf-8")
    data = json.load(f)
    f.close()
    return data


def _add_cities():
    print("Adding available cities")
    cities_collection = mongo_client[database][Collection.AVAILABLE_CITIES.value]
    # cities_collection.delete_many({})
    file_path = os.path.join("data", "available_cities", "prague.json")
    data = read_data(file_path)
    cities_collection.insert_one(data)


def _add_city_models():
    print("Adding city models")
    city_models_collection = mongo_client[database][Collection.CITY_MODELS.value]
    # city_models_collection.delete_many({})
    file_path = os.path.join("data", "city_models", "prague.json")
    data = read_data(file_path)
    city_models_collection.insert_one(data)


def _add_job_information():
    print("Adding job information")
    job_info_collection = mongo_client[database][Collection.JOB_INFORMATION.value]
    # job_info_collection.delete_many({})
    job_info_dir = os.path.join("data", "job_information")
    for file in os.listdir(job_info_dir):
        job_info_data = read_data(os.path.join(job_info_dir, file))
        job_info_data_loaded = {
            "jobId": bson.Binary.from_uuid(UUID(job_info_data["jobId"]), uuid_representation=3),
            "jobName": job_info_data["jobName"],
            "startTime": datetime.strptime(job_info_data["startTime"], '%Y-%m-%d %H:%M:%S.%f'),
            "endTime": datetime.strptime(job_info_data["endTime"], '%Y-%m-%d %H:%M:%S.%f'),
            "status": job_info_data["status"],
            "parameters": job_info_data["parameters"]
        }
        job_info_collection.insert_one(job_info_data_loaded)


def _add_job_results():
    print("Adding job results")
    job_results_collection = mongo_client[database][Collection.JOB_RESULTS.value]
    # job_results_collection.delete_many({})
    job_results_dir = os.path.join("data", "job_results")
    for file in os.listdir(job_results_dir):
        job_result_data = read_data(os.path.join(job_results_dir, file))
        job_result_data["jobId"] = bson.Binary.from_uuid(UUID(job_result_data["jobId"]), uuid_representation=3)
        job_results_collection.insert_one(job_result_data)


def run_db_seed():
    _add_cities()
    _add_city_models()
    _add_job_information()
    _add_job_results()


if __name__ == '__main__':
    run_db_seed()