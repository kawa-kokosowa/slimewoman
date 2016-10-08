"""AKA "Display"

"""

import urwid

from slimewoman import models
from slimewoman import database


session = database.connect()


class StateClientUi(object):
    """This is simply a client which interfaces with the
    database. In the future, this will be a REST client
    to a REST server, possibly (if I want multiplayer).

    """

    OVERLAY_WIDTH_IN_PERCENT = 60
    OVERLAY_HEIGHT_IN_PERCENT = 60

    def __init__(self, session, gamestate):
        self.session = session
        self.gamestate = gamestate
        self.main = None

    def menu(self):
        """Menu from current room.

        Needs to add thing for picking up items.

        """

        title = self.gamestate.current_room.id.upper()
        description = self.gamestate.current_room.description
        body = [urwid.Text(title),
                urwid.Divider(),
                urwid.Text(description),
                urwid.Divider()]

        # add the menu buttons for doors
        doors_in_current_room = self.gamestate.current_room.doors_in_room
        for door in doors_in_current_room:
            button_name = 'Door to %s' % door.destination_room_id

            if door.require_items:
                button_name += " [NEEDS: %s]" % ', '.join([item.id for item in door.require_items])

            button = urwid.Button(button_name)
            urwid.connect_signal(button, 'click', self.open_door, door)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))

        # add the menu buttons for rooms
        current_items_in_room = self.gamestate.current_room.items_in_room
        for item in current_items_in_room:
            button_name = item.id
            button = urwid.Button(button_name)
            urwid.connect_signal(button, 'click', self.take_item_from_current_room, item)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))

        # add the quit button and return our listbox (menu) of buttons
        button = urwid.Button("QUIT")
        urwid.connect_signal(button, 'click', self.exit_program)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        # add inventory at bottom
        body.append(urwid.Text('Inventory: ' + ', '.join([item.id for item in self.gamestate.inventory])))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    @staticmethod
    def exit_program(button):
        raise urwid.ExitMainLoop()

    def make_room(self):
        """GUI"""

        listbox_menu = self.menu()
        self.main.original_widget = listbox_menu

    def list_inventory(self):
        """asdf"""

        self.main.original_widget = new_thing

    def open_door(self, button, door):
        """Urwid button callback"""

        # if this door takes items, make sure the player has all the
        # items and that we've taken them away from player inventory
        if door.require_items:
            # gather a list of items to remove in case player has
            # all of them in their inventory
            items_to_remove = []
            for item_required in door.require_items:
                if not item_required in self.gamestate.inventory:
                    break
            # else if break never occurred, that means player had every
            # required item and we can change the room
            else:
                self.gamestate.current_room_id = door.destination_room_id
                self.session.commit()
        else:
            # ... no items required to open!
            self.gamestate.current_room_id = door.destination_room_id
            self.session.commit()

        self.make_room()

    def take_item_from_current_room(self, button, item):
        """Urwid button callback"""

        current_room = self.gamestate.current_room
        current_room.items_in_room.remove(item)
        self.gamestate.inventory.append(item)
        self.session.commit()
        self.make_room()

    def run(self):
        listbox_menu = self.menu()
        self.main = urwid.Padding(listbox_menu, left=2, right=2)
        overlay_width = ('relative', self.OVERLAY_WIDTH_IN_PERCENT)
        overlay_height = ('relative', self.OVERLAY_HEIGHT_IN_PERCENT)
        top = urwid.Overlay(self.main, urwid.SolidFill(u'*'),
                            align='center', width=overlay_width,
                            valign='middle', height=overlay_height,
                            min_width=20, min_height=9)
        urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()


# runtime
# create gamestate
session = database.connect(init_db=True)
database.create_from_dir(session, 'tests/sample_project/')
gamestate = models.GameState(current_room_id="Room A")
session.add(gamestate)
session.commit()
console_ui = StateClientUi(session, gamestate)
console_ui.run()
