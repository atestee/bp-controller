import json
from shapely.geometry import Polygon


def parse_geojsons(clusters):
    for cluster in clusters:
        print(cluster["feedingTransitStops"])
        cluster["excludedResidentialBuildings"] = json.loads(cluster["excludedResidentialBuildings"])
        cluster["includedResidentialBuildings"] = json.loads(cluster["includedResidentialBuildings"])
        cluster["geography"] = json.loads(cluster["geography"])

    return clusters

def add_cluster_name(data):
    for res in data:
        geography = res['geography']
        if len(res['feedingTransitStops']) > 3:
            name = str(res['feedingTransitStops'][0]) + "-" + str(res['feedingTransitStops'][-1])
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
        # print(name)
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
        print(P_center.x)
        bounds["southWest"] = [P_bounds[1], P_bounds[0]]
        bounds["northEast"] = [P_bounds[3], P_bounds[2]]
        cluster["geography"]["features"][0]["properties"]["bounds"] = bounds.copy()
        cluster["geography"]["features"][0]["properties"]["center"] = [P_center.y, P_center.x]

    return data


def prepare_data(data):
    clusters_geojsons_pased = parse_geojsons(data["clusters"])
    clusters_names_added = add_cluster_name(clusters_geojsons_pased)
    clusters_bounds_added = add_cluster_bounds_and_center(clusters_names_added)
    processed_data = {
        "clusters": clusters_bounds_added
    }
    return processed_data


# if __name__ == '__main__':
#     response_data = json.load(open("data/response_1649688791438.json", "r", encoding='utf-8'))
#     processed_data = prepare_data(response_data)
#     f = open("data/response_1649688791438_processed.json", "w", encoding='utf-8')
#     f.write(json.dumps(processed_data))
#     f.close()
