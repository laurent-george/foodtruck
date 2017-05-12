"""
Script that allows to populate the database
"""

import redis
import json
import requests

from config import cfg
from cuisine_classifier import CuisineClassifier


redis_db = redis.StrictRedis(host=cfg['redis']['host'],
                             port=cfg['redis']['port'],
                             db=cfg['redis']['db_num'],
                             decode_responses=True)


def add_truck_in_db(id, name, longitude=0, latitude=0, status=None, geodata_key=cfg['db_keys']['truck_geo_data_key'],
                    fooditems='', cuisines=''):
    pipe = redis_db.pipeline(transaction=True)
    redis_db.sadd('possible_status', status)
    for cuisine in cuisines:
        redis_db.sadd('possible_cuisines', cuisine)
    possible_status = redis_db.smembers('possible_status')
    possible_cuisines = redis_db.smembers('possible_cuisines')
    pipe.hmset(id, {'name': name, 'longitude': longitude, 'latitude': latitude,
                    'status': status, 'truck_id': id, 'fooditems': fooditems, 'cuisines': cuisines})
    pipe.sadd('status:' + status, id)

    # update status index
    for s in possible_status:
        if s == status:
            pipe.sadd('status:' + s, id)
        else:
            pipe.srem('status:' + s, id)

    # update cuisines index
    for s in possible_cuisines:
        if s in cuisines:
            pipe.sadd('cuisine:' + s, id)
        else:
            pipe.srem('cuisine:' + s, id)

    pipe.execute_command("GEOADD {} {} {} {}".format(geodata_key, longitude, latitude, id))
    pipe.execute()


def open_json(url, local=False):
    if local:
        with open(url) as f:
            data = json.load(f)
    else:
        response = requests.get(url)
        if response.status_code != 200:
            raise ConnectionError("Error downloading file {}, status_code is {}".format(url, response.status_code))
        data = response.json()
    return data


def load_dataset_from_json(url, dataset_origin='sf', local=False):
    clf = CuisineClassifier(cfg['datasets_local']['cuisines'])
    data = open_json(url, local=local)

    for entry in data:
        id = ':'.join(['truck', dataset_origin, entry['objectid']])
        latitude = entry['latitude']
        longitude = entry['longitude']
        name = entry['applicant']
        status = entry['status']
        fooditems = entry.get('fooditems', '')
        cuisines = clf.compute_match_cuisines(fooditems)

        # TODO: refactor this.. so we don't rewrite all keys.. using a mapping for instance .. TODO: laurent
        add_truck_in_db(id, name,
                        longitude=longitude,
                        latitude=latitude,
                        status=status,
                        fooditems=fooditems,
                        cuisines=cuisines)


def load_schedule_data(url, dataset_origin='sf', local=False):
    data = open_json(url, local=local)

    for entry in data:
        id = ':'.join(['truck', dataset_origin, entry['locationid']])
        dayofweekstr = entry['dayofweekstr']
        #day = entry['dayorder']
        start_time = entry['start24']
        end_time = entry['end24']

        redis_db.hmset(id, {'schedule:' + dayofweekstr: (start_time, end_time)})


def load_local_datasets():
    trucks_json_uri = cfg['datasets_local']['trucks']
    schedule_json_uri = cfg['datasets_local']['schedules']
    load_dataset_from_json(trucks_json_uri, local=True)
    load_schedule_data(schedule_json_uri, local=True)


def load_remote_datasets():
    trucks_json_uri = cfg['datasets']['trucks']
    schedule_json_uri = cfg['datasets']['schedules']
    try:
        load_dataset_from_json(trucks_json_uri)
        load_schedule_data(schedule_json_uri)
    except ConnectionError:
        print('Problem fetching datasets online')


def main():
    # load_local_datasets()
    load_remote_datasets()

if __name__ == "__main__":
    main()
