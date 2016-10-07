import sqlalchemy

DATABASE_URI = 'sqlite://'


def connect():
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
    return db_session


def init_db():
    from slimewoman import models
    Base.metadata.create_all(bind=engine)


def create_from_dir(directory):
    from slimewoman import models

    for file_path in glob.glob(os.path.join(directory, "*.xml")):

        with open(file_path) as f:
            new_room = models.Room.from_xml_string(f.read())

        yield new_room
