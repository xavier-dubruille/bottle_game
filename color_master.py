CONTINUE1 = 'z'
CONTINUE2 = 'y'
CONTINUE3 = 'x'
EMPTY_COLOR = '_'
QUESTION_MARK = '?'


class ColorMaster:
    def __init__(self):
        self._extra_color_index = 0
        self._color_letter = {
            'v': (40, 79, 1),
            'b': (91, 75, 136),
            'p': (82, 22, 164),
            'r': (175, 115, 248),
            'j': (31, 174, 246),
            'c': (214, 158, 25),
            's': (174, 195, 249),
            'e': (70, 54, 226),
            'm': (115, 18, 126),
            'h': (7, 146, 113),
            'o': (24, 107, 236),
            'n': (205, 80, 5),
            EMPTY_COLOR: (60, 24, 23),
            CONTINUE1: (86, 60, 58.7),
            CONTINUE2: (33.2, 149, 208),
            CONTINUE3: (113, 92, 90)
        }

    def get_matching_letter(self, color: list, tolerance=10):
        for c, v in self._color_letter.items():
            if (
                    (v[0] - tolerance) < color[0] < (v[0] + tolerance) and
                    (v[1] - tolerance) < color[1] < (v[1] + tolerance) and
                    (v[2] - tolerance) < color[2] < (v[2] + tolerance)
            ):
                return c

        new_color = str(self._extra_color_index)
        self._color_letter[new_color] = tuple(color)
        self._extra_color_index += 1

        return new_color
