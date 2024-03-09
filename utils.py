from typing import List

from bottle import Bottle
from color_master import QUESTION_MARK


def reveal_unknowns(state_current: str, state_init: str):
    assert len(state_init) == len(state_current)
    upgraded_current = []
    for i in range(len(state_current)):
        new_color = state_init[i] if state_current[i] == QUESTION_MARK else state_current[i]
        upgraded_current.append(new_color)
    return "".join(upgraded_current)


def update_absolute_init(absolute_init_ptr: List, current_bottles_state: str, discovered_bottle_id: int):
    absolute_init = absolute_init_ptr[0]
    bottle_str_state = current_bottles_state.split('-')[discovered_bottle_id]
    discovered_bottle = Bottle(discovered_bottle_id, bottle_str_state)
    start_index, end_index, color = discovered_bottle.last_color_indices()
    init_state_list = absolute_init.split("-")
    init_state_of_discovered_bottle = init_state_list[discovered_bottle_id]
    new_bottle_init_state = list(init_state_of_discovered_bottle)
    for i in range(start_index, end_index + 1):
        assert new_bottle_init_state[i] == QUESTION_MARK
        new_bottle_init_state[i] = color
    init_state_list[discovered_bottle_id] = "".join(new_bottle_init_state)
    absolute_init_ptr[0] = "-".join(init_state_list)
