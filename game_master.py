import time
from typing import List

from bottle import Bottle
from game import Game
from image_analyser import ImageAnalyser
from snaptshot import Snapshot
from utils import reveal_unknowns, update_absolute_init


class GameMaster():
    def __init__(self, adb_master):
        self._adb_master = adb_master

    def continue_if_asked(self, filename=None):
        filename = filename or self._adb_master.get_screenshot('continue')
        img_analyser = ImageAnalyser.create_from_path(filename)
        if img_analyser._is_it_continue1():
            self._adb_master.click_here(450, 1993)
        elif img_analyser._is_it_continue2():
            self._adb_master.click_here(500, 1800)
        elif img_analyser._is_it_continue3():
            self._adb_master.click_here(500, 1980)
    def click_reset_game(self):
        self._adb_master.click_here(300, 200)

    def play_one_game(self):
        filename = self._adb_master.get_screenshot()

        img_analyser = ImageAnalyser.guess_and_create_from_path(filename)

        if img_analyser.is_known_ahead_style:
            self._play_one_game_ahead_style(img_analyser)
        else:
            self._play_one_game_with_unknown(img_analyser)

    def _play_one_game_ahead_style(self, img_analyser):
        # i.e. when we first compute the solution, then we play it

        init_state = img_analyser.read_bottles_state()
        print(f"The init state is {init_state}")

        # game = Game.create_test_game()
        game = Game.create_game(init_state)
        result, status = game.play_it()
        assert status == Game.WON

        seq = img_analyser.indexes2positions(result.done_moves)
        self._adb_master.play_seq(seq)

    def _play_one_game_with_unknown(self, img_analyser: ImageAnalyser, absolute_init_game: List[str] = None):
        current_init_state = img_analyser.read_bottles_state()
        if absolute_init_game:
            current_init_state = reveal_unknowns(current_init_state, absolute_init_game[0])
        else:
            absolute_init_game = [current_init_state]

        print(f"The init state for this 'game'"
              f" (note, if reveal has been done, then we start new game) is {current_init_state}")

        game = Game.create_game(current_init_state)

        # try to find "a" correct sequence : 3 cases:
        #     1. deadend; need restart this game
        #     2. winning/done
        #     3. revealing a new color
        snap, status = game.play_it()

        if status == Game.DEAD_END:  # we don't care about 'seq', it's useless
            self.click_reset_game()
            time.sleep(2)
            # let's restart a new game
            filename = self._adb_master.get_screenshot()

            # 0. Create a new img_analyser with the new screenshot
            new_img_analyser = ImageAnalyser.create_from_path(path=filename, disposition=img_analyser.disposition)
            return self._play_one_game_with_unknown(new_img_analyser, absolute_init_game)

        seq = snap.done_moves
        # if we're here: we need to play the sequence
        seq_pos = img_analyser.indexes2positions(seq)
        self._adb_master.play_seq(seq_pos)

        if status == Game.WON:
            return game  # todo: right now, i don't know what could be useful to return

        if status == Game.NEW_COLOR:
            time.sleep(2)
            filename = self._adb_master.get_screenshot()

            # 0. Create a new img_analyser with the new screenshot
            new_img_analyser = ImageAnalyser.create_from_path(path=filename, disposition=img_analyser.disposition)

            # 1. update absolute_init
            discovered_bottle_id = seq[-1][0]  # this should work also: snap.bottle_that_need_to_be_reveiled.index
            update_absolute_init(absolute_init_game, new_img_analyser.read_bottles_state(), discovered_bottle_id)

            # then, let's play (almost) like it was the first time
            return self._play_one_game_with_unknown(new_img_analyser, absolute_init_game)
