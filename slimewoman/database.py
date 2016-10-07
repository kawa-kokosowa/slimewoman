from __future__ import absolute_import

import glob
import os

import sqlalchemy

DATABASE_URI = 'sqlite://'


def connect(init_db=False):
    from slimewoman import models
    engine = sqlalchemy.create_engine(DATABASE_URI)
    db_session = sqlalchemy.orm.scoped_session(
        sqlalchemy.orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    )
    models.Base.query = db_session.query_property()

    if init_db:
        models.Base.metadata.create_all(bind=engine)

    return db_session


def create_from_dir(db_session, directory):
    from slimewoman import models

    for file_path in glob.glob(os.path.join(directory, "*.xml")):

        with open(file_path) as f:
            new_room = models.Room.from_xml_string(f.read())

        db_session.add(new_room)

    db_session.commit()
