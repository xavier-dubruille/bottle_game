from color_master import EMPTY_COLOR, QUESTION_MARK


class Bottle:
    def __init__(self, bottle_index: int, init_state):
        self.index = bottle_index
        # self.state holds the colors (represented by a single char) contained in the bottle.
        # index 0 is the bottom (-1 the top). '_' is no color
        self.state = init_state
        self.need_to_be_reveiled = False

    @property
    def size(self):
        return len(self.state)

    @property
    def is_full(self):
        return self.state[-1] != EMPTY_COLOR

    @property
    def is_empty(self):
        return self.state[0] == EMPTY_COLOR

    @property
    def is_pure(self):
        # todo: could be improved by saving it insead of compute it each time
        return not self.is_empty and all(e == self.state[0] for e in self.state)

    @property
    def is_done(self):
        return self.is_empty or (self.is_full and self.is_pure)

    def is_full_known(self):
        return QUESTION_MARK not in self.state

    @property
    def deep_copy(self):
        return Bottle(self.index, [c for c in self.state])

    def __eq__(self, other):
        return self.index == other.index

    # Return if self can be poured into other_bottle
    def can_be_poured_into(self, other_bottle):
        if self.is_done or other_bottle.is_full or self == other_bottle:
            return False
        if other_bottle.is_empty:
            return True
        available, last_color = other_bottle.what_could_be_received()
        number_to_be_poured, color_to_be_poured = self.what_could_be_given()
        return last_color == color_to_be_poured and available >= number_to_be_poured

    @classmethod
    def create_from_str(cls, bootle_id, bottle_str):
        return cls(bootle_id, [c for c in bottle_str])

    def __repr__(self):
        return f"{self.index}:" + "".join(self.state)

    def __str__(self):
        return self.__repr__()

    def what_could_be_given(self, remove=False):
        color, index = self._last_color()
        current_index = index
        num_to_give = 1
        while True:
            current_index -= 1
            if current_index >= 0 and self.state[current_index] == color:
                num_to_give += 1
            else:
                break
        if remove:
            for i in range(index - num_to_give + 1, index + 1):
                self.state[i] = EMPTY_COLOR
            new_last_color, _ = self._last_color()
            self.need_to_be_reveiled = (new_last_color == QUESTION_MARK)

        return num_to_give, color

    def what_could_be_received(self):
        color, index = self._last_color()
        available_slots = len(self.state) - index - 1
        assert 0 <= available_slots <= len(self.state)
        return available_slots, color

    def pour_into(self, other_bottle):
        number, color = self.what_could_be_given(remove=True)
        other_bottle._fill(color, number)

    def _fill(self, color, number):
        previous_color, index = self._last_color()
        assert previous_color is None or color == previous_color  # assert compatible color
        assert index + number + 1 <= len(self.state)
        for i in range(number):
            self.state[index + i + 1] = color

    def _last_color(self):
        color = None
        index = -1
        for i, c in enumerate(self.state):
            if c != EMPTY_COLOR:
                index, color = i, c
            else:
                break
        return color, index

    def last_color_indices(self):
        # index *included* ==>  caa_ will return 1,2,a
        color_last, index = self._last_color()
        number, color = self.what_could_be_given()
        assert color_last == color
        first_index = index + 1 - number
        assert first_index >= 0
        return first_index, index, color
