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


class Door(Base):
    """One-directional portal from one room to another.

    Fields:
        id: Regular autoincrement row ID.
        source_room_id: This door is accessible only through this room.
        destination_room_id: Using this door will put you in this room.

    Note:
        Doors are one-directional, only accessible from source room.
        This is intentional to increase flexibility.

    """

    __tablename__ = 'doors'

    id = Column(Integer, primary_key=True)
    # TODO: requires_item?
    source_room_id = Column(
        String,
        ForeignKey('rooms.id'),
    )
    destination_room_id = Column(String, ForeignKey('rooms.id'))

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
