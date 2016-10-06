"""AKA "Display"

"""

import urwid


class RoomUI(object):
    OVERLAY_WIDTH_IN_PERCENT = 60
    OVERLAY_HEIGHT_IN_PERCENT = 60

    def __init__(self, adventure):
        self.main = None

    def menu(self):
        """Menu from current room.

        Needs to add thing for picking up items.

        """

        title = self.adventure.current_room.title.upper()
        description = self.adventure.current_room.description
        body = [urwid.Text(title),
                urwid.Divider(),
                urwid.Text(description),
                urwid.Divider()]

        for c in self.adventure.current_room.exits + self.adventure.current_room.inventory:
            button_name = c.name

            if hasattr(c, "needs_key") and c.needs_key:
                button_name += " [LOCKED]"

            button = urwid.Button(button_name)
            urwid.connect_signal(button, 'click', self.item_chosen, c.name)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))

        button = urwid.Button("QUIT")
        urwid.connect_signal(button, 'click', self.exit_program)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
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

    def item_chosen(self, button, choice):
        """Can use this to create menu again.

        """

        # change the current room to choice
        # TODO: this should probably be a method of adventure,
        # such as getitem
        current_room = self.adventure.current_room

        for door in current_room.exits:

            if door.name.lower() == choice:

                if door.needs_key:
                    
                    if self.adventure.player.inventory.has_item_of_name('key'):
                        door.needs_key = False
                        self.adventure.player.inventory.remove_item_of_name('key')
                        continue
                    else:
                        continue

                self.adventure.set_room_by_link_id(choice)
                self.make_room()
                return None

        current_room.pickup_item(self.adventure.player, choice)
        self.make_room()
        return None

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


# sorting out urwid gui mess

