from __future__ import absolute_import

import glob
import os
import xml.etree.ElementTree

import sqlalchemy

DATABASE_URI = 'sqlite://'


def connect(init_db=False, autocommit=False, autoflush=False):
    from slimewoman import models
    engine = sqlalchemy.create_engine(DATABASE_URI)
    db_session = sqlalchemy.orm.scoped_session(
        sqlalchemy.orm.sessionmaker(
            autocommit=autocommit,
            autoflush=autoflush,
            bind=engine
        )
    )
    models.Base.query = db_session.query_property()

    if init_db:
        models.Base.metadata.create_all(bind=engine)

    return db_session


def from_xml_string(cls, xml_string):

    return room


def create_from_dir(db_session, directory):
    from slimewoman import models

    for file_path in glob.glob(os.path.join(directory, "*.xml")):

        with open(file_path) as f:
            xml_string = f.read()

        root = xml.etree.ElementTree.fromstring(xml_string)
        room_id = root.attrib['id']

        # build the items_in_room
        items_in_room = []
        for item_tag in root.iter('item'):
            new_item = models.Item(
                id=item_tag.attrib['id'],
                find_phrase=item_tag.attrib['find_phrase'],
                source_room_id=room_id,
            )
            new_item = db_session.merge(new_item)
            items_in_room.append(new_item)

        db_session.commit()

        # build the doors
        doors = []
        require_items = []
        for door_tag in root.iter('door'):

            # first get all items
            if 'require_items' in door_tag.attrib:
                for item_id in door_tag.attrib['require_items'].split(', '):
                    new_item = db_session.merge(models.Item(id=item_id, source_room_id=room_id))
                    require_items.append(new_item)

            db_session.commit()

            # create the door
            door = models.Door(
                source_room_id=room_id,
                destination_room_id=door_tag.attrib['destination'],
                require_items=require_items,
            )
            doors.append(door)

        # create the items!
        for item in require_items + items_in_room:
            merged_item = db_session.merge(item)

        # finally, create the room with its doors and items
        room = models.Room(
            id=room_id,
            doors_in_room=doors,
            starting='starting' in root.attrib,
            description=root.find('description').text,
            items_in_room=items_in_room,
        )
        db_session.add(room)

    db_session.commit()
