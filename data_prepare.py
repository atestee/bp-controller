import json
import math
import pandas as pd
import numpy as np
import gtfstk as gt
from shapely.geometry import Polygon
import db_utils


def parse_geojsons(clusters):
    for cluster in clusters:
        cluster["excludedResidentialBuildings"] = json.loads(cluster["excludedResidentialBuildings"])
        cluster["includedResidentialBuildings"] = json.loads(cluster["includedResidentialBuildings"])
        cluster["geography"] = json.loads(cluster["geography"])

    return clusters


def get_properties_arrays(property, data) :
    arr = []
    for building in data["features"]:
        arr.append(building["properties"][property])
    return arr


def add_cluster_name(data):
    for res in data:
        geography = res['geography']
        if len(res['feedingTransitStops']) > 3:
            length = len(res['feedingTransitStops'])
            name = str(res['feedingTransitStops'][0]["name"]) + "-" + str(res['feedingTransitStops'][length-1]["name"])
        elif len(res['feedingTransitStops']) == 3:
            name = str(res['feedingTransitStops'][0]['name']) + "-" + \
                   str(res['feedingTransitStops'][1]['name']) + "-" + \
                   str(res['feedingTransitStops'][2]['name'])
        elif len(res['feedingTransitStops']) == 2:
            name = str(res['feedingTransitStops'][0]['name']) + "-" + \
                   str(res['feedingTransitStops'][1]['name'])
        else:
            name = str(res['feedingTransitStops'][0]['name'])

        geography["features"][0]["properties"]["name"] = name
        res['geography'] = geography
    return data


def add_cluster_bounds_and_center(data):
    bounds = {
        "southWest": None,
        "northEast": None
    }
    for cluster in data:
        coords = cluster["geography"]["features"][0]["geometry"]["coordinates"][0]
        P = Polygon(coords)
        P_bounds = P.bounds
        P_center = P.centroid
        bounds["southWest"] = [P_bounds[1], P_bounds[0]]
        bounds["northEast"] = [P_bounds[3], P_bounds[2]]
        cluster["geography"]["features"][0]["properties"]["bounds"] = bounds.copy()
        cluster["geography"]["features"][0]["properties"]["center"] = [P_center.y, P_center.x]

    return data


def calculate_histogram(data, nbins, max_value):
    data = np.array(data)
    delta = max_value / nbins
    histogram = np.zeros(nbins)
    for elem in data:
        idx = math.floor(elem / delta)
        if idx == nbins:
            idx -= 1
        histogram[idx] += 1

    return histogram


def add_cluster_histograms(data, nbins, parameters):
    histograms = {
        "taxiRideDurationMinutes": None,
        "taxiRideDistanceMeters": None
    }

    for cluster in data:
        arr1 = get_properties_arrays("taxiRideDurationMinutes", cluster["includedResidentialBuildings"])
        arr2 = get_properties_arrays("taxiRideDistanceMeters", cluster["includedResidentialBuildings"])

        histograms["taxiRideDurationMinutes"] = json.loads(pd.Series(calculate_histogram(arr1, nbins, int(parameters["maxTaxiRideDurationMinutes"]))).to_json(orient='values'))
        histograms["taxiRideDistanceMeters"] = json.loads(pd.Series(calculate_histogram(arr2, nbins, int(parameters["maxDrivingDistanceMeters"]))).to_json(orient='values'))

        cluster["histograms"] = histograms.copy()

    return data


def modify_transit_types(data):
    transit_types = {
        1: "metro",
        0: "tram",
        3: "bus",
        7: "funicular"
    }
    for t in data["numberOfPTStopsClustering"]:
        t["transitType"] = transit_types[t["transitType"]]

    return data


def replace_route_identification(data):
    feed = gt.read_gtfs("gtfs.zip", dist_units='m')
    routes = feed.routes

    lines = []
    included_routes = data["includedRoutes"]
    for transit_group in included_routes:
        if transit_group["inclusionType"] == "SUBSET":
            for route_short_name in transit_group["lines"]:
                lines.append(routes[routes["route_short_name"] == route_short_name]["route_id"])

            transit_group["lines"] = json.loads(pd.Series(np.array(lines).flatten().copy()).to_json(orient='values'))
            lines.clear()

    return data


def add_cluster_route_linestrings(data, city):
    transit_types = {
        1: "metro",
        0: "tram",
        3: "bus",
        7: "funicular"
    }
    city_model = db_utils.find_one_city_model_by_name(city)
    feed = gt.read_gtfs("gtfs.zip", dist_units='m')
    routes = feed.routes
    for cluster in data:
        route_id = cluster["routeId"]
        route_name = routes[routes["route_id"] == route_id]["route_short_name"].values[0]
        route_type_id = routes[routes["route_id"] == route_id]["route_type"]
        route_type = transit_types[route_type_id.values[0]]
        cluster["routeGeometry"] = city_model["availablePublicTransportRoutes"][route_type][route_name]
        cluster["routeType"] = route_type
        cluster["routeName"] = route_name
        cluster.pop("routeId")

    return data



def prepare_data(data):
    nbins = int(data["nbins"])
    city = data["city"]
    centerCoords = data["centerCoords"]
    jobName = data["jobName"]

    clusters_geojsons_pased = parse_geojsons(data["clusters"])
    clusters_names_added = add_cluster_name(clusters_geojsons_pased)
    clusters_bounds_added = add_cluster_bounds_and_center(clusters_names_added)
    clusters_histograms_added = add_cluster_histograms(clusters_bounds_added, nbins, data["parameters"])
    clusters_routes_linestrings_added = add_cluster_route_linestrings(clusters_histograms_added, city)
    parameters_transit_types_modified = modify_transit_types(data["parameters"])
    processed_data = {
        "clusters": clusters_routes_linestrings_added,
        "parameters": parameters_transit_types_modified,
        "nbins": nbins,
        "city": city,
        "centerCoords": centerCoords,
        "jobName": jobName
    }
    return processed_data


def save_data(data, file_name):
    f = open(file_name, "w+", encoding="utf-8")
    f.write(json.dumps(data))
    f.close()

