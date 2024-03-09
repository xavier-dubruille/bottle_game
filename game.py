from hash_handler import HashHandler
from properties import DEBUG_GAME
from snaptshot import Snapshot


class Game:
    NEW_COLOR = "New_color"
    WON = "Won"
    DEAD_END = "Dead_end"

    def __init__(self, snapshot: Snapshot, hash_handler):
        self.possibilities = [snapshot]
        self._hash_handler = hash_handler

    @classmethod
    def create_game(cls, init_state):
        hash_handler = HashHandler()
        snap = Snapshot.create_from_str(init_state, hash_handler)
        return Game(snap, hash_handler)

    @classmethod
    def create_test_game_simple(cls):
        init_state = "abc-bca-bca-___-___"
        return cls.create_game(init_state)

    @classmethod
    def create_test_game(cls):
        # level 181 (difficile)
        # init_state = "hbch-iosp-mbaj-vrir-psba-mavi-rjvs-prho-maci-pvoo-bjmc-shcj-____-____"
        init_state = "hcbh-psoi-jabm-rirv-absp-ivam-svjr-ohrp-icam-oovp-cmjb-jchs-____-____"
        return cls.create_game(init_state)

    # return the last generated snapshot or None is no snapshot were generated
    # note: the last generated snapshot will be the one that will be played next time
    def play_one(self):
        s = self.possibilities.pop()
        last_snap = None
        for snap in s.generate_next_snapshots():
            self.possibilities.append(snap)
            last_snap = snap
        return last_snap

    def play_it(self):
        # Play all the possibilities until it find a solution or try all possibilities
        while True:
            if len(self.possibilities) == 0:  # should be frequent if we are in a game containing unkowns, otherwize, it should happen
                # print("I don't know how we did it, "
                #       "but it seems that there's no possibilities left (maybe it was impossible ?)")
                return None, Game.DEAD_END
            if DEBUG_GAME:
                print(f"Let's play one more turn. We have still {len(self.possibilities)} possibilities to try "
                      f"and the next possibility/snapshot is: {self.possibilities[-1]}")
            snap = self.play_one()

            if snap and snap.is_a_winning_snap:
                print(f"Congrats! snapshot is: {snap}")
                print(f" and the list of moves is: {snap.done_moves}")
                return snap, Game.WON
            if snap and snap.bottle_that_need_to_be_reveiled:  # should never occur if we are in a situation where everything is known in advanced
                return snap, Game.NEW_COLOR