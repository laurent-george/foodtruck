"""
Food truck rest api
"""

import hug
import redis

from config import cfg

geodata_key = cfg['db_keys']['truck_geo_data_key']
redis_db = redis.StrictRedis(host=cfg['redis']['host'],
                             port=cfg['redis']['port'],
                             db=cfg['redis']['db_num'],
                             decode_responses=True)


@hug.get('/food_trucks', examples='status=APPROVED&nearby=-122.4194,37.7749,1000', output=hug.output_format.json, versions=1)
def get_all_food_trucks(nearby: hug.types.comma_separated_list = None,
                        status: hug.types.comma_separated_list = None,
                        cuisines: hug.types.comma_separated_list = None,
                        attributes: hug.types.comma_separated_list = None,
                        limit: hug.types.number = 10):
    """
    Get food trucks list that match parameters

    :param nearby: [longitude, latitude, radius] where radius is in meters
    :param status: list to filter on permit status (e.g APPROVED, REQUESTED, EXPIRED, SUSPEND, ISSUED, INACTIVE)
                    if status is None, APPROVED status is considered
    :param cuisines: list to filter on cuisines (e.g arab, north_american, italian, drinks_and_snacks,
                                                        south_american, asian, other)
                    if status is None, APPROVED status is considered
    :param attributes: list of attribute to get, filter is None -> return all keys
                    if attributes is None, all the available keys are returned
    :param limit: if above 0 function return a maximum of *limit* elements, otherwise all found trucks are returned
    :return: list of food truck entry where each entry is a dict (e.g [{truck_id: "1", name: "truck1", ...},
                                                                       {truck_id: "2", name: "truck2" ..}, ... ])
    """
    if status is None:
        status = ["APPROVED"]

    # getting indexes of truck that match the provided status
    keys = redis_db.sunion(["status:" + requested_status for requested_status in status])

    if cuisines:
        cuisines_match_keys = redis_db.sunion(["cuisine:" + requested_cuisine for requested_cuisine in cuisines])
        keys = cuisines_match_keys.intersection(keys)

    if nearby:
        longitude, latitude, radius = nearby
        # getting truck in nearby region
        nearby_keys = get_truck_near_to_pos(radius=radius, longitude=longitude, latitude=latitude)
        keys = [key for key in nearby_keys if key in keys]  # nos using set union in order to keep the ascending order

    keys = list(keys)

    # keeping only *limit* trucks
    if limit > 0:
        keys = keys[0:limit]

    pipe = redis_db.pipeline(transaction=True)

    for key in keys:
        pipe.hgetall(key)
        # pipe.hmget(key, ['status', 'status'])  # <<-- TODO: check if hmget + constructing dict is faster here
    res = pipe.execute()

    # filtering on attributes
    if attributes:
        res = [{k: v for (k, v) in entry.items() if k in attributes} for entry in res]

    return res


@hug.get('/food_trucks/{truck_id}')
def get_food_truck(truck_id, attributes: hug.types.comma_separated_list = None):
    """
    Get attributes of a specific truck

    :param truck_id: id of a truck
    :param attributes: list of attribute to get, filter is None -> return all keys
    :return: a Python dict of the hash's name/value pairs"

    """
    res = redis_db.hgetall(truck_id)
    if not attributes:
        return res
    return {k: v for (k, v) in res.items() if k in attributes}


def get_truck_near_to_pos(radius=1, longitude=0, latitude=0):
    """
    Return ids of trucks entry that are in a radius around a target point

    :param radius: radius in meter
    :param longitude: target point longitude
    :param latitude: target point latitude
    :return: list of truck_id, the list is sorted in distance to target ascending order
    """
    # using redis a geo radius functionnality (Time complexity: O(N+log(M)) where N is the number of elements inside
    # the bounding box of the circular area and M is the number of items inside the index.
    georadius_cmd = "GEORADIUS {} {} {} {} m ASC".format(geodata_key, longitude, latitude, radius)
    res = redis_db.execute_command(georadius_cmd)
    return res


def main():
    import time
    start = time.time()
    res = get_all_food_trucks(limit=-1, nearby=[-122.4194, 37.7749, 1000])
    print(len(res))
    duration = time.time() - start
    print("Duration is {}".format(duration))


if __name__ == "__main__":
    main()
