"""Main API

"""

from __future__ import absolute_import


# should be a db so you can have multiple chars
class GameState(object):

    def __init__(self):
        self.current_room = None  # or id?
        self.inventory = []
