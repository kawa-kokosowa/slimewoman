"""Test models.py

I also test database in here.

"""

from __future__ import absolute_import

import sqlalchemy

from tests import common
from slimewoman import models, database


class TestItems(common.BaseTest):
    pass


class TestDoors(common.BaseTest):
    """Ensure the following about doors:

    * A door can be created with a required item
    * Deleting required_item from door does not delete said item from
      the database.
    * Deleting an item removes it from the door's required_items

    """

    def test_requires_item(self):
        # First try to create a door which has two required items
        staff_of_rain = models.Item(
            id="Staff of Rain",
            find_phrase="open lid",
        )
        sunstone = models.Item(
            id="Sunstone",
            find_phrase="move rock",
        )
        required_items = [staff_of_rain, sunstone]
        door = models.Door(
            destination_room_id="some OTHER room",
            require_take_items=required_items,
        )
        self.session.add(door)
        self.session.commit()

        # Get the door we created
        hopefully_some_door = models.Door.query.filter_by(
            destination_room_id="some OTHER room",
        ).first()
        assert hopefully_some_door is door
        assert hopefully_some_door.destination_room_id == "some OTHER room"
        assert hopefully_some_door.require_take_items == required_items

        # try deleting the item
        self.session.delete(staff_of_rain)
        self.session.commit()
        
        assert hopefully_some_door.require_take_items == [sunstone]

        # try deleting the door
        self.session.delete(door)
        self.session.commit()

        assert models.Item.query.all() == [sunstone]


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
            destination_room_id="Room B",
        )
        room_a = models.Room(
            id="Room A",
            doors_in_room=[room_a_door_east],
        )
        self.session.add(room_a)

        # Room B
        room_b_door_west = models.Door(
            destination_room_id="Room A",
        )
        room_b_door_south = models.Door(
            destination_room_id="Room C",
        )
        room_b = models.Room(
            id="Room B",
            doors_in_room=[room_b_door_west, room_b_door_south],
        )
        self.session.add(room_b)

        # Room C
        room_c_door_north = models.Door(
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
        results = models.Door.query.filter_by(source_room_id=room_a.id)
        assert [r for r in results] == [room_a_door_east]

        # Room B's Doors
        results = models.Door.query.filter_by(source_room_id=room_b.id)
        assert [r for r in results] == [room_b_door_west, room_b_door_south]

        # ... query the DB to get room b's doors
        room_b_from_db = models.Room.query.get('Room B')
        assert room_b_from_db.doors_in_room == [room_b_door_west, room_b_door_south]

        # Room C's Doors
        results = models.Door.query.filter_by(source_room_id=room_c.id)
        assert [r for r in results] == [room_c_door_north]

        # Ensure all the doors are there...
        results = models.Door.query.all()
        assert results == [
            room_a_door_east,
            room_b_door_west,
            room_b_door_south,
            room_c_door_north
        ]

        # delete a room; its associated doors should be deleted, too

        # delete Room A
        self.session.delete(room_a)
        self.session.commit()
        results = models.Door.query.all()
        assert [r for r in results] == [room_b_door_west, room_b_door_south, room_c_door_north]

        # delete Room B
        self.session.delete(room_b)
        self.session.commit()
        results = models.Door.query.all()
        assert [r for r in results] == [room_c_door_north]

        # delete Room C
        self.session.delete(room_c)
        self.session.commit()
        results = models.Door.query.all()
        assert [r for r in results] == []

    def test_from_xml_string(self):

        with open('tests/sample_project/room_a.xml') as f:
            room = models.Room.from_xml_string(f.read())

        assert len(room.doors_in_room) == 1
        assert room.doors_in_room[0].source_room_id == "room a"
        assert room.doors_in_room[0].destination_room_id == "room b"


'''
class TestGameState(common.BaseTest):
    """Ensure the following about the GameState model:

    * You can create its inventory and set its current room on creation
    * Deleting items and the current room does
      not delete these items from the db
    * Deleting items and rooms removes from game state

    """

    def test_everything(self):
        # test inventory
        # create three items
        item_one = models.Item(
            id="Item One",
            find_phrase="pickup item one",
        )
        self.session.add(item_one)
        item_two = models.Item(
            id="Item Two",
            find_phrase='lolol',
        )
        self.session.add(item_two)
        item_three = models.Item(
            id="Item Three",
            find_phrase='oh gee',
        )
        self.session.add(item_three)
        self.session.commit()

        # test current room
        # create a room
        red_room = models.Room(id='Red Room')
        self.session.add(red_room)
        blue_room = models.Room(id='Blue Room')
        self.session.add(blue_room)
        self.session.commit()

        # finally create the game state
        gamestate = models.GameState(
            current_room_id='Red Room',
            inventory=[item_one, item_two, item_three],
        )
        self.session.add(gamestate)
        self.session.commit()
        gamestate_from_db = models.GameState.query.get(1)
        assert gamestate_from_db == gamestate
        assert gamestate_from_db.current_room == red_room
        assert gamestate_from_db.inventory == [item_one, item_two, item_three]


class TestDatabase(common.BaseTest):

    def test_create_from_dir(self):
        database.create_from_dir(self.session, "sample_project")
'''


if __name__ == '__main__':
    unittest.main()
