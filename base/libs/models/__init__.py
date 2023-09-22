from triggers import *
from redis_om import Migrator


def init():
    Migrator().run()
