from unittest import TestCase
# from mockredis import mock_strict_redis_client
from fakeredis import FakeStrictRedis
from mock import patch

import api

redis_db = FakeStrictRedis(host='0.0.0.0', port=6379, db=0, decode_responses=True)
# redis_db = mock_strict_redis_client(host='0.0.0.0', port=6379, db=0, decode_responses=True)


truck_1 = {'status': "APPROVED", 'id': 'truck:80423'}
truck_2 = {'status': "REQUESTED", 'id': 'truck:38124598'}


@patch('api.redis_db', redis_db)
class TestGetAllFoodTrucksDefault(TestCase):
    def setUp(self):

        def add_a_truck_to_mock_redis(id, status=None):
            if status is None:
                status = 'APPROVED'
            redis_db.hmset(id, {'name': "id_{}".format(id),
                                'longitude': 0,
                                'latitude': 0,
                                'status': status,
                                'truck_id': id,
                                'fooditems': '...'})

            redis_db.sadd("status:" + status, id)

        add_a_truck_to_mock_redis(truck_1['id'], status=truck_1['status'])
        add_a_truck_to_mock_redis(truck_2['id'], status=truck_2['status'])

        for i in range(100):
            add_a_truck_to_mock_redis("truck:" + str(i))

    def test_get_all_food_trucks(self):
        res = api.get_all_food_trucks()
        if len(res) == 0:
            self.fail()

    def test_get_all_food_trucks_with_limit(self):
        limit = 10
        res = api.get_all_food_trucks(limit=limit)
        self.assertEqual(len(res), limit)

    def test_get_all_food_trucks_status(self):
        res = api.get_all_food_trucks(status=['REQUESTED', 'OTHER'])
        if len(res) == 0:
            self.fail()
        res[0]['truck_id'] = truck_2['id']

    def test_get_all_food_trucks_attributes(self):
        res = api.get_all_food_trucks(attributes=['name', 'truck_id'])
        if len(res) == 0:
            self.fail()

        if set(res[0].keys()) != set(['name', 'truck_id']):
            self.fail()

    @patch('api.get_truck_near_to_pos', lambda radius, longitude, latitude: [truck_1['id']])
    def test_get_all_food_trucks_nearby(self):
        res = api.get_all_food_trucks(nearby=[1, 2, 3], status=["APPROVED"])
        if len(res) == 0:
            self.fail()
        self.assertEqual(res[0]['truck_id'], truck_1['id'])
