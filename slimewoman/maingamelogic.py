"""Main API

"""

import os
import glob

import sqlalchemy

from slimewoman import models
from slimewoman import database


class GameState(object):

    def __init__(self):
        self.current_room = None  # or id?
