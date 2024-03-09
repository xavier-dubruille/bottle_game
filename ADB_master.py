import subprocess
from time import sleep


class ADBMaster:
    def __init__(self):
        # todo : handle adb server here ?
        pass

    def exe(self, cmd: str):
        adb_exe = r"C:\Users\it\Downloads\platform-tools_r35.0.0-windows\platform-tools\adb.exe"
        subprocess.run(f"{adb_exe} {cmd} ", shell=True)

    def get_screenshot(self, filename="cap.png"):
        # todo remove previous image of that name
        # todo create sdcard/tmp/
        self.exe(f"shell screencap -p /sdcard/tmp/{filename}")
        self.exe(f"pull /sdcard/tmp/{filename}")

        # todo check if succeded
        return filename

    def click_here(self, x, y):
        self.exe(f"shell input tap {x} {y}")

    def play_seq(self, moves_seq):
        LONG_WAIT = 2.8 # 2  works most of the time  and 3 works all the time
        SHORT_WAIT = LONG_WAIT / 2
        VERY_SHORT_WAIT = 0.2

        last_move = ()
        for p1, p2 in moves_seq:
            # Let's "click" on p1 then p2.
            # #### Thoughts on optimisations ####
            # This can be done quickly ... unless p1 or p2 are currently being used !
            #
            # The problem is that we can not only look at the last moves because it may be also the move before that
            # that can be still 'busy" ... as for now I'll make SHORT_WAIT half of the LONG_WAIT and only look at the
            # last move.
            #
            # We can make a small optimisation eather if it's p1 or p2 that is currently
            # being used (but i won't do it now) ..
            #
            # (I think that : once p1 and p2 are 'in a move' they are 'free to be used' (almost) simultaneously,
            # so I don't think we can make optimisation by making a distinction between previous p1's and previous p2's)

            to_sleep = LONG_WAIT if p1 in last_move or p2 in last_move else SHORT_WAIT
            sleep(to_sleep)

            self.exe(f"shell input tap {p1[0]} {p1[1]}")
            sleep(VERY_SHORT_WAIT)
            self.exe(f"shell input tap {p2[0]} {p2[1]}")

            last_move = (p1, p2)
