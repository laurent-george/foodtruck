"""
Script that allows to populate the database
"""


from config import cfg
import redis
import json
import time

redis_db = redis.StrictRedis(host=cfg['redis']['host'],
                             port=cfg['redis']['port'],
                             db=cfg['redis']['db_num'],
                             decode_responses=True)


def add_truck_in_db(id, name, longitude=0, latitude=0, status=None, geodata_key=cfg['db_keys']['truck_geo_data_key'],
                    fooditems=""):
    pipe = redis_db.pipeline(transaction=True)
    # TODO: revoir comment on store les donnee, json/serialize autre ?
    pipe.hmset(id, {'name': name, 'longitude': longitude, 'latitude': latitude,
                    'status': status, 'truck_id': id, 'fooditems': fooditems})
    pipe.execute_command("GEOADD {} {} {} {}".format(geodata_key, longitude, latitude, id))
    pipe.execute()

# TODO: externaliser les update de la base dans un autre fichier (comment faire ca avec le singleton ? passer par l'api rest?)
# une solution serait de creer une nouvelle connection a la base redis (donc d'avoir les parametre du port de la base quelque part)
def load_dataset_from_json(file, dataset_origin='sf'):
    data = []
    with open(file) as f:
        data = json.load(f)

    for entry in data:
        id = entry['objectid']
        latitude = entry['latitude']
        longitude = entry['longitude']
        name = entry['applicant']
        status = entry['status']
        fooditems = entry.get('fooditems', '')

        # TODO: refactor this.. so we don't rewrite all keys.. using a mapping for instance .. TODO: laurent
        add_truck_in_db(id, name, longitude=longitude, latitude=latitude, status=status, fooditems=fooditems)

def load_schedule_data(file, dataset_origin='sf'):
    data = []
    with open(file) as f:
        data = json.load(f)   # TODO: ici on charge tout le fichier.. peut etre trouver une astuce pour charger bout par bout

    for entry in data:
        id = entry['locationid']
        dayofweekstr = entry['dayofweekstr']
        day = entry['dayorder']
        start_time = entry['start24']
        end_time = entry['end24']
        print("Adding entry for {} : {}".format(id, start_time))

        # TODO: remove this kind of hack.. maybee move to something different with redis
        redis_db.hmset(id, {'schedule_' + dayofweekstr: (start_time, end_time)})



def main():
    start = time.time()
    load_dataset_from_json('rqzj-sfat.json')
    duration = time.time() - start
    print("Duration of load database is {}".format(duration))
    load_schedule_data('bbb8-hzi6.json')


if __name__ == "__main__":
    main()

