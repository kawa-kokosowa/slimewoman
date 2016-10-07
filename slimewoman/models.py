import xml.etree.ElementTree

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# setup tables
require_take_items_table = Table(
    'require_take_items',
    Base.metadata,
    Column('door_id', Integer, ForeignKey('doors.id')),
    Column('item_id', String, ForeignKey('items.id')),
)


class Item(Base):
    __tablename__ = 'items'

    id = Column(String, primary_key=True)


# NOTE: does deleting a door auto remove it from room
class Door(Base):
    """One-directional portal from one room to another.

    Fields:
        id: Regular autoincrement row ID.
        source_room_id: This door is accessible only through this room.
        destination_room_id: Using this door will put you in this room.
        requires_item_id: The item this door requires to bring player
            to destination_room_id.

    Notes:
        Doors are one-directional, only accessible from source room.
        This is intentional to increase flexibility.

    """

    __tablename__ = 'doors'

    id = Column(Integer, primary_key=True)
    source_room_id = Column(
        String,
        ForeignKey('rooms.id'),
    )
    destination_room_id = Column(String, ForeignKey('rooms.id'))
    require_take_items = relationship(
        'Item',
        secondary=require_take_items_table,
    )

    def __repr__(self):
        return (
            '<Door source_room_id=%s, destination_room_id=%s>'
            % (self.source_room_id, self.destination_room_id)
        )


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(String, primary_key=True)
    doors_in_room = relationship(
        Door,
        backref='rooms',
        #cascade_backrefs=False,
        primaryjoin=id==Door.source_room_id,
        cascade='all,delete',
    )

    def __repr__(self):
        return '<Room "%s" (%d doors)>' % (self.name, len(self.doors))

    @classmethod
    def from_xml_string(cls, xml_string):
        root = xml.etree.ElementTree.fromstring(xml_string)
        room_id = root.attrib['id']

        # build the doors
        doors = []
        for door_tag in root.iter('door'):
            door = Door(
                source_room_id=room_id,
                destination_room_id=door_tag.attrib['destination'],
            )
            doors.append(door)

        room = cls(
            id=room_id,
            doors_in_room=doors,
        )
        return room
