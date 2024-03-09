from typing import List

from bottle import Bottle
from hash_handler import HashHandler
from properties import DEBUG_GAME


class Snapshot:
    """ a state of the game at a given time (should be immutable ...)"""
    def __init__(self, init_bottles: List[Bottle], hash_handler: HashHandler, done_moves=None, previous_snap=None):
        self.bottles = init_bottles
        self._hash_handler = hash_handler
        self.done_moves = done_moves or []
        self.has_already_generate = False
        self.previous_snaps = previous_snap or []

        # will be not None if there is a bottle with unknows color that is aligible for reveil
        # (i.e. the empty color is at the top )
        # will contain the bottle that are in the situation
        self.bottle_that_need_to_be_reveiled = None

    @staticmethod
    def create_from_str(init_state: str, hash_handler: HashHandler):
        init_bottles = []
        for i, b in enumerate(init_state.split("-")):
            init_bottles.append(Bottle.create_from_str(i, b))

        # TODO : assert all the bottle has the same size
        # TODO: can it transformed in to a tuple first ?
        return Snapshot(init_bottles, hash_handler)

    @property
    def is_full_known(self):
        return all(b.is_full_known for b in self.bottles)

    # Equivalent snapshots are supposed to have the same hash
    @property
    def hash(self):
        # todo: return tuple instead of a big string ?
        bottles_str = ["".join(b.state) for b in self.bottles]
        # do not sort if there is question mark because ??v could be different from an other "??v"
        if self.is_full_known:
            bottles_str.sort()
        return "-".join(bottles_str)

    def __str__(self):
        return f"{len(self.done_moves)} Moves => {"-".join(["".join(b.state) for b in self.bottles])}"

    @property
    def is_a_winning_snap(self):
        return all(e.is_done for e in self.bottles)

    # Return the list of possible Snapshot that could be made from this one;
    # Return [] if no more generations are possible.
    # If a "free move" is found, it's returned (alone) right away
    def generate_next_snapshots(self):
        if self.has_already_generate:  # i.e. if this snapshot has already been used to generate children
            return []
        self.has_already_generate = True

        next_snapshots = []

        not_filled_bottles = filter(lambda b: not b.is_full, self.bottles)
        for bottle in not_filled_bottles:
            possible_bottle_candidates = [b for b in self.bottles if b.can_be_poured_into(bottle)]
            for other_bottle in possible_bottle_candidates:
                new_snap = self.deep_copy
                new_snap.make_move(bottle.index, other_bottle.index, self)
                if not self._hash_handler.is_it_really_new(new_snap):
                    continue
                if bottle.is_pure:
                    return [new_snap]
                else:
                    next_snapshots.append(new_snap)

        # todo: order them to prioritize those that empty a bottle and un-prioritize those that fills an empty one
        # ex: 3 point if it empty a bottle, 2 point if it create a pure bottle, 0 if it use an empty bottle, 1 otherwise
        return next_snapshots

    @property
    def deep_copy(self):
        new_bottles_state = [b.deep_copy for b in self.bottles]
        new_moves = [m for m in self.done_moves]
        previous_snaps = [s for s in self.previous_snaps]
        return Snapshot(new_bottles_state, self._hash_handler, new_moves, previous_snaps)

    # PRE: the move HAS to be possible
    def make_move(self, bottle_index: int, other_bottle_index: int, previous_snap):
        self.add_move_in_history((other_bottle_index, bottle_index))
        if DEBUG_GAME:
            self.save_previous_snap(previous_snap)
        # Todo (esthetics): Use __item__() instead ?
        bottle = self.bottles[bottle_index]
        other_bottle = self.bottles[other_bottle_index]
        other_bottle.pour_into(bottle)
        if other_bottle.need_to_be_reveiled:
            self.bottle_that_need_to_be_reveiled = other_bottle

    def add_move_in_history(self, move):
        self.done_moves.append(move)

    def save_previous_snap(self, previous_snap):
        self.previous_snaps.append(previous_snap)
