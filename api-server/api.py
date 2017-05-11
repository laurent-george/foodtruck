#import requests
import hug
import json
import redis
import time

from config import cfg


redis_db = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
geodata_key = cfg['db_keys']['truck_geo_data_key']

redis_db = redis.StrictRedis(host=cfg['redis']['host'],
                             port=cfg['redis']['port'],
                             db=cfg['redis']['db_num'],
                             decode_responses=True)


@hug.cli()
@hug.get('/food_trucks', examples='status=APPROVED&nearby=-122.4194,37.7749,1000', output=hug.output_format.json)
def get_all_food_trucks(nearby:hug.types.comma_separated_list=None,
                        status:hug.types.comma_separated_list=['APPROVED'],
                        filters:hug.types.comma_separated_list=None):
    print(nearby)
    # TODO: a revoir ca m'embette d'etre autant en lien avec redis
    # quid du choix de redis ? -> avantage plusieurs process apres qui tape sur la meme db

    if nearby:
        longitude, latitude, radius = nearby
        print("longitude is {}".format(longitude))
        keys = get_truck_near_to_pos(radius=radius, longitude=longitude, latitude=latitude)
    else:
        keys = redis_db.keys('[0-9]*')

    res = [get_food_truck(key, filters=filters) for key in keys]  ## TODO maybee limits here using a filter ?

    # keeping only truck with status that match the requested one
    res = [val for val in res if val['status'] in status]
    return res


def get_trucks_info(truck_id, filter=None):
    """
    Get attribute of a specific truc

    :param filter: list of attribute to get, filter is None -> return all keys
    :return: a Python dict of the hash's name/value pairs"
    """



@hug.cli()
@hug.get('/food_trucks/{truck_id}')
def get_food_truck(truck_id, filters:hug.types.comma_separated_list=None):
    """
    Get attribute of a specific truc

    :param filter: list of attribute to get, filter is None -> return all keys
    :return: a Python dict of the hash's name/value pairs"

    """
    print("Filter is {}".format(filters))
    res = redis_db.hgetall(truck_id)
    print(res)
    if not(filters):
        return res
    return {k: v for (k, v) in res.items() if k in filters}


@hug.cli()
def create_entry(id:hug.types.number,
                 name: hug.types.text,
                 facility_type: hug.types.OneOf(['Truck', 'Push Cart']),
                 address: hug.types.text,
                 latitude: hug.types.number,
                 longitude: hug.types.number):
    # TODO: utiliser un json en parametre plus propre ?
    print("Creating entry ")
    #add_truck_in_db()

@hug.cli()




def get_truck_near_to_pos(radius:hug.types.float_number=1, longitude:hug.types.float_number=0, latitude:hug.types.float_number=0):
    """
    Plop

    :param radius: radius in meter
    :param longitude:
    :param latitude:
    :return: list of truck_id, the list is sorted in ascending order
    """
    georadius_cmd = "GEORADIUS {} {} {} {} m ASC".format(geodata_key, longitude, latitude, radius)
   # Time complexity: O(N+log(M)) where N is the number of elements inside the bounding box of the circular area
   # delimited by center and radius and M is the number of items inside the index.
    res = redis_db.execute_command(georadius_cmd)
    #res_named = [redis_db.hmget(key, ['name']) for key, dist in res]
    #print(res_named)
    #print(res_dist)
    return res



def main():
    pass


if __name__ == "__main__":
    main()