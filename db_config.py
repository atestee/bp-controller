from enum import Enum

# TODO: change the database URI and name
MONGO_URL = ""
MONGO_DATABASE = ""


class Collection(Enum):
    AVAILABLE_CITIES = "availablecities"
    CITY_MODELS = "citymodels"
    JOB_RESULTS = "results"
    JOB_INFORMATION = "job_management"
