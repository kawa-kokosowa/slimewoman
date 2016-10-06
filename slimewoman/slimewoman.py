"""Main API

"""

import os
import glob

import sqlalchemy

import models


engine = sqlalchemy.create_engine('sqlite:///develop.db')
session = sqlalchemy.orm.sessionmaker(bind=engine)()
models.Base.metadata.create_all(engine)


class GameState(object):

    def __init__(self):
        self.current_room = None  # or id?


def create_quest_db_from_dir(directory):

    for file_path in glob.glob(os.path.join(directory, "*.xml")):

        with open(file_path) as f:
            new_room = models.Room.from_xml_string(f.read())

        session.add(new_room)
