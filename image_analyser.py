import cv2
import numpy as np

from color_master import ColorMaster, CONTINUE1, CONTINUE2, QUESTION_MARK, EMPTY_COLOR, CONTINUE3
from properties import DEBUG_ANALYSER

DISPOSITION_7_7 = "7-7"
DISPOSITION_6_5 = "6-5"


class Properties:

    def __init__(self, disposition=DISPOSITION_7_7):
        # global
        self.bottle_size = 4  # how many color per bottle
        self.color_size_x = 105  # pixels size in x for a color block (i.e. bottle height / bottle_size)
        self.color_size_y = 95  # pixels size in y for a color block (i.e. bottle width)
        self.color_block_security_ratio = 0.9  # used to not use the full block to determine the color
        self.extra_security_left = 20  # Don't use the first xxx px on the left (to avoid artifacts )

        # line 1
        self.line1_how_many_bottle = 7
        self.line1_first_top_x = 60  # first bottle
        self.line1_first_top_y = 750  # first bottle
        self.line1_dist_bottle_x = 142  # between the top-left of two bottle side by side

        # line 2
        self.line2_how_many_bottle = 7  # (note: only the 'usable' bottles)
        self.line2_first_top_x = 40  # first bottle
        self.line2_first_top_y = 1368  # first bottle
        self.line2_dist_bottle_x = 128  # between the top-left of two bottle side by side

        if disposition == DISPOSITION_6_5:
            self.set_for_6_5()
        if disposition == DISPOSITION_7_7:
            self.set_for_7_7()

    def set_for_7_7(self):
        # the default values are based on this case, so, there is nothing do be done
        pass

    def set_for_6_5(self):
        self.line1_how_many_bottle = 6
        self.line2_how_many_bottle = 5

        self.line2_first_top_x = 60
        self.line1_dist_bottle_x = 170
        self.line2_dist_bottle_x = 170


class ImageAnalyser:
    """
    It's like a wrapper around a given image.
    (if there are bottle on the immage): it can read bottle colors or positions
    (note: it should be immutable )
    """

    def __init__(self, image, disposition=DISPOSITION_7_7):
        assert image is not None
        self.disposition = disposition
        self._color_master = ColorMaster()
        self._image = image
        self._bottles_state: str = ''
        self._properties = Properties(disposition)
        self._bottles_positions = []  # will be filled (side effect... not good ?) when color state will be read

    @classmethod
    def create_from_path(cls, path="cap.png", disposition=DISPOSITION_7_7):
        image = cv2.imread(path)
        return ImageAnalyser(image, disposition)

    @classmethod
    def guess_and_create_from_path(cls, path="cap.png"):
        image = cv2.imread(path)

        six_five = ImageAnalyser(image, DISPOSITION_6_5)
        six_five.read_bottles_state()
        if six_five.is_valid_bottle_state():
            return six_five

        seven_seven = ImageAnalyser(image, DISPOSITION_7_7)
        seven_seven.read_bottles_state()
        if seven_seven.is_valid_bottle_state():
            return seven_seven

        print(f"The image '{path}' couldn't be interpreted as a bottle assortment")
        return None

    @property
    def is_known_ahead_style(self):
        return QUESTION_MARK not in self._bottles_state

    def _is_it_continue1(self):
        # not the best way (it would be better to read the text)
        selection = self._image[1985:2002, 425:670]
        mean_color = np.mean(selection, axis=(0, 1))
        matching_color = self._color_master.get_matching_letter(mean_color, tolerance=5)
        # print(mean_color)
        return matching_color == CONTINUE1

    def _is_it_continue2(self):
        # not the best way (it would be better to read the text)
        selection = self._image[1766:1826, 384:702]
        mean_color = np.mean(selection, axis=(0, 1))
        matching_color = self._color_master.get_matching_letter(mean_color, tolerance=5)
        print(mean_color)
        return matching_color == CONTINUE2

    def _is_it_continue3(self):
        # not the best way (it would be better to read the text)
        selection = self._image[1953:1993, 460:618]
        mean_color = np.mean(selection, axis=(0, 1))
        matching_color = self._color_master.get_matching_letter(mean_color, tolerance=5)
        print(mean_color)
        return matching_color == CONTINUE3

    def build_bottle_string(self, top_x, top_y):
        cur_x = int(top_x)
        cur_y = int(top_y)
        security_ratio = self._properties.color_block_security_ratio
        size_x = int(self._properties.color_size_x * security_ratio)
        size_y = int(self._properties.color_size_y * security_ratio)
        shift_y = int(self._properties.color_size_y * (1 - security_ratio))
        extra_secu = self._properties.extra_security_left

        color_letter = []

        for i in range(self._properties.bottle_size):
            x1, x2 = cur_x + extra_secu, cur_x + size_x
            y1, y2 = cur_y, cur_y + size_y
            selection = self._image[y1:y2, x1:x2]
            couleur_maj = np.mean(selection, axis=(0, 1))
            matching_color = self._color_master.get_matching_letter(couleur_maj)
            color_letter.append(matching_color)
            if DEBUG_ANALYSER:
                print(f"Rectangle ({x1}, {y1}) - ({x2}, {y2}) : "
                      f"Couleur majoritaire: {couleur_maj}, ce qui donne '{matching_color}' ")
                cv2.imshow("Selection", selection)
                cv2.waitKey(0)
            cur_y += (size_y + shift_y)
            if DEBUG_ANALYSER:
                cv2.destroyAllWindows()

        color_letter.reverse()

        # if not empty: will replace the first 'empty' color by a question mark
        # (note: i'm sure we can write it a cleaner way !)
        if not all(c == EMPTY_COLOR for c in color_letter):
            for i in range(len(color_letter)):
                if color_letter[i] != EMPTY_COLOR:
                    break
                color_letter[i] = QUESTION_MARK

        return "".join(color_letter)

    def read_bottles_state(self) -> str:

        if self._bottles_state:
            return self._bottles_state

        p = self._properties

        top_x = p.line1_first_top_x
        top_y = p.line1_first_top_y
        bottles_str = []

        for i in range(p.line1_how_many_bottle):
            single_bottle = self.build_bottle_string(top_x, top_y)
            self._add_bootle(i, top_x, top_y)
            top_x += p.line1_dist_bottle_x
            bottles_str.append(single_bottle)

        top_x = p.line2_first_top_x
        top_y = p.line2_first_top_y
        for i in range(p.line2_how_many_bottle):
            single_bottle = self.build_bottle_string(top_x, top_y)
            self._add_bootle(i + p.line1_how_many_bottle, top_x, top_y)
            top_x += p.line2_dist_bottle_x
            bottles_str.append(single_bottle)

        self._bottles_state = "-".join(bottles_str)
        return self._bottles_state

    # def guess_properties(self):
    #     # based on the image, may be deducted ...
    #     # as for now, i'll have set of hardcoded default values:
    #     prop = Properties()
    #     prop.set_for_6_5()
    #     return prop

    def indexes2positions(self, done_moves):
        real_moves = []
        for p1, p2 in done_moves:
            real_p1 = self._bottles_positions[p1]
            real_p2 = self._bottles_positions[p2]
            real_moves.append((real_p1, real_p2))
        return real_moves

    def _add_bootle(self, i, top_x, top_y):
        p = self._properties
        position = (top_x + p.color_size_x / 1, top_y + p.color_size_y * p.bottle_size / 2)
        self._bottles_positions.append(position)
        # todo assert it's the right i

    def is_valid_bottle_state(self):
        return not any(c.isdigit() for c in self._bottles_state)
