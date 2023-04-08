"""A module for the panels that make up the game interface"""
import collections
import curses

import events

class TextPanel():
    """Displays and formats text in a curses window"""

    def __init__(self, window):
        self.window = window
        #The height within the window where the next line
        #of text should be drawn:
        self.next_line = 1 #1 not 0, to account for window border

    def display():
        """Called by the game loop. Should print appropriate text
        inside the panel.
        """
        raise NotImplementedError
    
    ## PRIVATE METHODS ##
    def _trim_message(self, message, more_indicator=None):
        """Trims, wraps and truncates a message to a list of lines that fit in the window
        
        Returns a tuple. The first part of the tuple is a deque of strings. If the message 
        is too long to fit in the window at once, the second part of the tuple will be the 
        remaining part of the message.
        """
        height, width = self.window.getmaxyx()
        #Account for border
        width -= 2
        height -= 2

        #Turn the message into an array of words, and reverse it so that
        #we can consume from the end
        message = message.split(' ')
        message.reverse()

        message_rows = collections.deque()
        #Leave space for a "==MORE==" message if necessary
        adjusted_height = height-1 if more_indicator is not None else height
        #Break the message into lines
        while len(message_rows) < (adjusted_height) and len(message) > 0:
            new_row = ""
            while len(message) > 0:
                #Put words into the current row's string
                #Break if putting another word in would overflow the width
                #Also break on a newline
                if len(new_row) + 1 + len(message[-1]) < width:
                    word = message.pop()
                    words = word.split('\n', 1)
                    new_row += " " + words[0]
                    if len(words) > 1:
                        for word in words[1:]:
                            message.append(word)
                        break
                elif new_row == "":
                    #Rather than choke forever on a string too long to print but too stubborn to die,
                    #if we haven't added any words at all this iteration, break the first word into 
                    #two words and try again.
                    stupid_long_word = message.pop()
                    first_part = stupid_long_word[:width-2] + '-'
                    second_part = stupid_long_word[width-2:]
                    message.append(second_part)
                    message.append(first_part)
                else:
                    break
            message_rows.append(new_row)

        #We should now have an array of strings, each of which represents a row of text
        #that will fit in the window. If there's any more of the message left, return it
        #as the second part of the tuple.
        remaining_text = None
        if len(message) > 0:
            message.reverse()
            remaining_text = " ".join(message)

        #Optionally put a message at the bottom of the window if there is more text
        if more_indicator is not None and remaining_text is not None:
            message_rows.append(more_indictaor.center(width-1))

        return (message_rows, remaining_text)

    def _display_message(self, message_rows):
        """Print the text line by line into the window"""
        while len(message_rows) > 0:
            self.window.addstr(self.next_line, 1, message_rows.popleft(), curses.A_BOLD)
            self.next_line += 1

    def _reset_line_position(self):
        """Move the next line back to the top of the window"""
        self.next_line = 1


class MessagePanel(TextPanel):
    """Displays game messages to the player"""

    def __init__(self, window):
        super(MessagePanel, self).__init__(window)
        self._message_queue = collections.deque()
        self.more_messages_string = "==MORE=="

        events.listen_to_event("print_message", self.add_message)

    def add_message(self, text):
        """Add a message to be displayed next turn"""
        self._message_queue.append(text)

    def display(self):
        """Display all messages in the queue in FIFO order, pausing to wait for keystrokes
        after each one
        """
        #Can't use the 'for in' syntax, since we want to pop
        while len(self._message_queue) > 0:
            self.window.border()
            message = self._message_queue.popleft()
            message_rows, remaining = self._trim_message(message)
            if remaining is not None:
                #Put any text that didn't fit back on the queue, but
                #it can go straight to the front, enjoying all the envious
                #looks that the rest of the text gives it.
                self._message_queue.appendleft(remaining)
            self._display_message(message_rows)
            self.window.getkey()
            self.window.clear()
            self._reset_line_position()
        self.window.refresh()

class ListMenu(TextPanel):
    """Displays a list of selectable options"""

    class ListMenuItem():
        """A selectable option in a ListMenu"""

        def __init__(self, text, action):
            self.text = text
            self.action = action

    def __init__(self, window, menu_list=None):
        super(ListMenu, self).__init__(window)
        self.active = False

        self.header = None
        self.menu_list = [] if menu_list is None else menu_list
        self.footer = None

        events.listen_to_event("print_list", self.set_list)

    def set_list(self, text_action_pairs, header = None, footer=None):
        """Wrap text and function pairs in ListMenuItems and set the current list
        to a list of those items.
        """
        self.menu_list = [ListMenu.ListMenuItem(text, action) for text, action in text_action_pairs]
        if header is not None and len(header) > 0:
            self.header, _ = self._trim_message(header)
        if footer is not None and len(footer) > 0:
            self.footer, _ = self._trim_message(footer)
        self.active = True

    def display(self):
        """Draw the list items to the screen"""
        if self.active:
            self.window.border()
            if self.header is not None:
                self._display_message(self.header)
            for idx, option in enumerate(self.menu_list):
                message = "{0}. {1}".format(idx, option.text)
                message_rows, _ = self._trim_message(message)
                self._display_message(message_rows)
            if self.footer is not None:
                self._display_message(self.footer)
            self.handle_key(self.window.getkey())
            self._reset_line_position()
            self.window.clear()
            self.active = False
            self.window.refresh()

    def handle_key(self, key):
        """Handle keyboard input for the menu"""
        number = None
        try:
            number = int(key)
        except ValueError:
            #If the key wasn't a number key, don't worry about it.
            pass

        if number is not None and 0 <= number < len(self.menu_list):
            self.menu_list[number].action()
        elif key in ["q", "KEY_ESC"]:
            pass
        else:
            self.handle_key(self.window.getkey())

