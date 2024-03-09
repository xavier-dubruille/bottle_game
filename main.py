import time

from ADB_master import ADBMaster
from game_master import GameMaster

if __name__ == "__main__":
    game_master = GameMaster(ADBMaster())
    game_done = 0
    good = True
    while good:
        game_master.play_one_game()
        game_done += 1
        print(f"*** We've finished {game_done} game so far :) ****")
        time.sleep(5)
        game_master.continue_if_asked()
        time.sleep(2)