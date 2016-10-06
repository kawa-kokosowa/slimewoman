"""Test models.py

"""

from __future__ import absolute_import

import sqlalchemy

from tests import common
from slimewoman import models


class TestRooms(common.BaseTest):
    """Ensure the following about rooms:

    * A room can be created containing multiple doors
    * A room can be created containing multiple items
    * Deleting a door from a room deletes the door
    * Deleting an item from a room does NOT delete the item from DB
    * Deleting a room does not remove its items from DB
    * Deleting a room also deletes its doors

    """

    def test_room_doors(self):
        # We create three rooms, A, B, and C
        #
        # + - + - +  % is a door
        # | A % B |  - and + are walls
        # + - + % +
        #     | C |
        #     + - +

        # Room A
        room_a_door_east = models.Door(
            source_room_id="Room A",
            destination_room_id="Room B",
        )
        room_a = models.Room(
            id="Room A",
            doors_in_room=[room_a_door_east],
        )
        self.session.add(room_a)

        # Room B
        room_b_door_west = models.Door(
            source_room_id="Room B",
            destination_room_id="Room A",
        )
        room_b_door_south = models.Door(
            source_room_id="Room B",
            destination_room_id="Room C",
        )
        room_b = models.Room(
            id="Room B",
            doors_in_room=[room_b_door_west, room_b_door_south],
        )
        self.session.add(room_b)

        # Room C
        room_c_door_north = models.Door(
            source_room_id="Room C",
            destination_room_id="Room B",
        )
        room_c = models.Room(
            id="Room C",
            doors_in_room=[room_c_door_north],
        )
        self.session.add(room_c)

        # ...finally commit all the changes
        self.session.commit()

        # now try to test by querying

        # Room A's Doors
        results = self.session.query(models.Door).filter_by(source_room_id=room_a.id)
        assert [r for r in results] == [room_a_door_east]

        # Room B's Doors
        results = self.session.query(models.Door).filter_by(source_room_id=room_b.id)
        assert [r for r in results] == [room_b_door_west, room_b_door_south]

        # Room C's Doors
        results = self.session.query(models.Door).filter_by(source_room_id=room_c.id)
        assert [r for r in results] == [room_c_door_north]

        # Ensure all the doors are there...
        results = self.session.query(models.Door).all()
        assert results == [
            room_a_door_east,
            room_b_door_west,
            room_b_door_south,
            room_c_door_north
        ]

        # delete a room; its associated doors should be deleted, too

        # delete Room A
        self.session.delete(room_a)
        results = self.session.query(models.Door).all()
        assert [r for r in results] == [room_b_door_west, room_b_door_south, room_c_door_north]

        # delete Room B
        self.session.delete(room_b)
        results = self.session.query(models.Door).all()
        assert [r for r in results] == [room_c_door_north]

        # delete Room C
        self.session.delete(room_c)
        results = self.session.query(models.Door).all()
        assert [r for r in results] == []

    def test_from_xml_string(self):

        with open('tests/sample_project/room_a.xml') as f:
            room = models.Room.from_xml_string(f.read())

        assert len(room.doors_in_room) == 1
        assert room.doors_in_room[0].source_room_id == "room a"
        assert room.doors_in_room[0].destination_room_id == "room b"


if __name__ == '__main__':
    unittest.main()
