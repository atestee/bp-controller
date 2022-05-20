import json
from uuid import UUID
import bson as bson
from pymongo import MongoClient
import db_config as mongo_utils

mongo_client = MongoClient(mongo_utils.MONGO_URL)
database = mongo_utils.MONGO_DATABASE


# AVAILABLE CITIES
def find_available_cites():
    collection = mongo_client[database][mongo_utils.Collection.AVAILABLE_CITIES.value]
    return list(collection.find())[0]["availableCitiesList"]


# CITY MODEL
def find_one_city_model_by_name(name):
    collection = mongo_client[database][mongo_utils.Collection.CITY_MODELS.value]
    return collection.find_one({"name": name}).get("cityModel")


# JOB INFORMATION
# create
def insert_one_job_information(job_information):
    job_information_collection = mongo_client[database][mongo_utils.Collection.JOB_INFORMATION.value]
    return job_information_collection.insert_one(job_information)


# read
def find_all_job_information():
    job_information_collection = mongo_client[database][mongo_utils.Collection.JOB_INFORMATION.value]
    return job_information_collection.find()


# update
def update_job_information_end_time_and_status(job_id, end_time):
    job_information_collection = mongo_client[database][mongo_utils.Collection.JOB_INFORMATION.value]
    filter = {"jobId": bson.Binary.from_uuid(UUID(job_id), uuid_representation=3)}
    newvalues = {"$set": {'endTime': end_time, "status": "FINISHED"}}
    return job_information_collection.update_one(filter, newvalues)


# JOB RESULT
def insert_one_job_result(result):
    results_collection = mongo_client[database][mongo_utils.Collection.JOB_RESULTS.value]
    return results_collection.insert_one(result)


# read
def find_one_job_result_by_id(job_id):
    collection = mongo_client[database][mongo_utils.Collection.JOB_RESULTS.value]
    result = collection.find_one({"jobId": bson.Binary.from_uuid(UUID(job_id), uuid_representation=3)})
    result["jobId"] = job_id
    result.pop("_id")
    return result
