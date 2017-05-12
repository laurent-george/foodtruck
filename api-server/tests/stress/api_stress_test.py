#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from locust import HttpLocust, TaskSet

TIMEOUT = 3


def get_all_food_trucks(l):
    l.client.get("/v1/food_trucks", timeout=TIMEOUT)


def get_near_by_food_trucks(l):
    """
    using a fix position in SF
    """
    radius = random.randrange(1000, 10000)
    "/v1/food_trucks?nearby=(-122.4194,37.7749,1000)"
    l.client.get("/v1/food_trucks?nearby=-122.4194,37.7749,{}".format(radius),
                 timeout=TIMEOUT, name="/food_trucks?nearby=[lgn,lat,radius])")


class UserBehavior(TaskSet):
    tasks = {get_all_food_trucks: 1, get_near_by_food_trucks: 10}


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 200
    max_wait = 1000
