import glob
import urwid


class Room(object):

    def __init__(self, link_id, title, exits, description):
        self.link_id = link_id
        self.title = title
        self.exits = exits
        self.description = description

    @staticmethod
    def validate_and_clean(expected_row_name, unsafe_row):
        expected_row_name_with_syntax = expected_row_name.upper() + ": "
        assert unsafe_row.startswith(expected_row_name_with_syntax)
        row_without_name = unsafe_row.replace(expected_row_name_with_syntax, " ", 1) 
        return row_without_name.strip()
    
    @classmethod
    def from_string(cls, room_string):
        room_file_contents = room_string.split('\n')
        link_id = cls.validate_and_clean("link_id", room_file_contents[0]).lower()
        title = cls.validate_and_clean("title", room_file_contents[1])
        exits = cls.validate_and_clean("exits", room_file_contents[2]).split(",")
        description = '\n'.join(room_file_contents[3:]).strip()

        return cls(link_id, title, exits, description)


class Adventure(object):
    ROOM_NAME_PATTERN = "*.room.txt"

    def __init__(self, rooms):
        self.rooms = rooms
        self.current_room = self.rooms["first_room"]

    @classmethod
    def from_directory(cls, directory):
        rooms = {}

        for room_file_name in glob.glob(directory + '/' + cls.ROOM_NAME_PATTERN):

            with open(room_file_name) as f:
                room_file_string = f.read()
                room = Room.from_string(room_file_string)
                rooms[room.link_id] = room

        return cls(rooms)

    def set_room_by_link_id(self, link_id):
        self.current_room = self.rooms[link_id]


class RoomUI(object):
    OVERLAY_WIDTH_IN_PERCENT = 60
    OVERLAY_HEIGHT_IN_PERCENT = 60

    def __init__(self, adventure):

        self.adventure = adventure
        self.main = None

    def menu(self):
        """Menu from current room.

        """

        title = self.adventure.current_room.title.upper()
        description = self.adventure.current_room.description
        body = [urwid.Text(title),
                urwid.Divider(),
                urwid.Text(description),
                urwid.Divider()]

        for c in self.adventure.current_room.exits:
            button = urwid.Button(c)
            urwid.connect_signal(button, 'click', self.item_chosen, c)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))

        button = urwid.Button("QUIT")
        urwid.connect_signal(button, 'click', self.exit_program)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    @staticmethod
    def exit_program(button):
        raise urwid.ExitMainLoop()

    def make_room(self):
        listbox_menu = self.menu()
        self.main.original_widget = listbox_menu

    def item_chosen(self, button, choice):
        """Can use this to create menu again.

        """

        # change the current room to choice
        # TODO: this should probably be a method of adventure,
        # such as getitem
        self.adventure.set_room_by_link_id(choice)
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

# sorting out urwid gui mess
adventure = Adventure.from_directory("rooms")
RoomUI(adventure).run()
