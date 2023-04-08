"""A module for handling keyboard input"""
import events

def handle_key(key):
    if key in ["y", "7"]:
        events.trigger_event("player_move", x_dir=-1, y_dir=-1)
    if key in ["KEY_UP", "k", "8"]:
        events.trigger_event("player_move", x_dir=0, y_dir=-1)
    if key in ["u", "9"]:
        events.trigger_event("player_move", x_dir=1, y_dir=-1)
    if key in ["KEY_LEFT", "h", "4"]:
        events.trigger_event("player_move", x_dir=-1, y_dir=0)
    if key in ["KEY_RIGHT", "l", "6"]:
        events.trigger_event("player_move", x_dir=+1, y_dir=0)
    if key in ["b", "1"]:
        events.trigger_event("player_move", x_dir=-1, y_dir=1)
    if key in ["KEY_DOWN", "j", "2"]:
        events.trigger_event("player_move", x_dir=0, y_dir=1)
    if key in ["n", "3"]:
        events.trigger_event("player_move", x_dir=1, y_dir=1)
    if key in ['i']:
        events.trigger_event("player_display_inventory")
    if key in ['d']:
        events.trigger_event("player_drop_inventory")
    if key in ['>', '<']:
        events.trigger_event("player_use_portal")
