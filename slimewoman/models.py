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


gamestate_inventory_table = Table(
    'gamestate_inventory',
    Base.metadata,
    Column('gamestate_id', Integer, ForeignKey('game_states.id')),
    Column('item_id', String, ForeignKey('items.id')),
)


class Item(Base):
    """Items belong to a source room because they're found in
    that source room, and that's what gives the item its definiton.

    See sample project's xml.

    """

    __tablename__ = 'items'

    id = Column(String, primary_key=True)
    find_phrase = Column(String)
    source_room_id = Column(
        String,
        ForeignKey('rooms.id'),
    )


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
    destination_room_id = Column(String, ForeignKey('rooms.id'), nullable=False)
    require_take_items = relationship(
        'Item',
        secondary=require_take_items_table,
        cascade='all,delete',
    )

    def __repr__(self):
        return (
            '<Door source_room_id=%s, destination_room_id=%s>'
            % (self.source_room_id, self.destination_room_id)
        )


class Room(Base):
    """

    Rooms create both doors and items, which belong to this room. Items
    are always found in a room, thus items all have a source_room_id.
    Doors also belong to and are defined by a room. Deleting a room will
    delete both its items and doors.

    """

    __tablename__ = 'rooms'

    id = Column(String, primary_key=True)
    description = Column(String)
    starting = Column(Boolean, default=False)

    doors_in_room = relationship(
        Door,
        backref='rooms',
        foreign_keys=[Door.source_room_id,],
        cascade='all,delete',
    )
    items_in_room = relationship(
        Item,
        backref='rooms',
        foreign_keys=[Item.source_room_id,],
        cascade='all,delete',
    )

    def __repr__(self):
        return '<Room "%s" (%d doors)>' % (self.name, len(self.doors))

    @classmethod
    def from_xml_string(cls, xml_string):
        root = xml.etree.ElementTree.fromstring(xml_string)
        room_id = root.attrib['id']

        # build the items_in_room
        items_in_room = []
        for item_tag in root.iter('item'):
            item = Item(
                id=item_tag.attrib['id'],
                find_phrase=item_tag.attrib['find_phrase'],
            )
            items_in_room.append(item)

        # build the doors
        doors = []
        for door_tag in root.iter('door'):

            # first get all items
            items = []
            if 'require_take_items' in door_tag.attrib:
                for item_id in door_tag.attrib['require_take_items'].split(', '):
                    new_item = Item(id=item_id)
                    items.append(new_item)

            # create the door
            door = Door(
                source_room_id=room_id,
                destination_room_id=door_tag.attrib['destination'],
                require_take_items=items,
            )
            doors.append(door)

        # finally, create the room with its doors and items
        room = cls(
            id=room_id,
            doors_in_room=doors,
            starting='starting' in root.attrib,
            description=root.find('description').text,
            items_in_room=items_in_room,
        )
        return room


class GameState(Base):
    __tablename__ = 'game_states'

    id = Column(Integer, primary_key=True)
    current_room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)

    inventory = relationship(
        'Item',
        secondary=gamestate_inventory_table,
    )
    current_room = relationship('Room')
