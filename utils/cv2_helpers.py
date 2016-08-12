import cv2
import numpy as np


EVENT_KEY_ESCAPE = 1048603
EVENT_KEY_ENTER = 1048586
EVENT_KEY_CRTL = 1114083
EVENT_KEY_CTRL_C = 1310819


class MouseButtonAction(object):
    def __call__(self, action, x, y):
        getattr(self, '_handle_' + action)(x, y)

    def _handle_down(self, x, y):
        pass

    def _handle_move(self, x, y):
        pass

    def _handle_up(self, x, y):
        pass

    def _handle_stop(self, x, y):
        pass


def get_size(image):
    height, width, channels = image.shape
    return (width, height)


def reduce_keep_ratio(image, max_size):
    width, height = get_size(image)
    ratio = max(width/max_size[0], height/max_size[1])
    return cv2.resize(image, (int(width/ratio), int(height/ratio)))


def display_text_width(image, text, font, color, background_color, thickness,
                       margin, align_bottom_left=False, align_top_left=False):
    assert align_bottom_left or align_top_left

    i_w, i_h = get_size(image)
    max_right_position = i_w - margin

    font_size = 1
    (text_size, _) = cv2.getTextSize(text, font, font_size, thickness)
    while text_size[0] < max_right_position - margin * 2:
        font_size += 1
        (text_size, _) = cv2.getTextSize(text, font, font_size, thickness)
    font_size -= 1

    if align_bottom_left:
        position = (margin, i_h - margin)
    elif align_top_left:
        position = (margin, text_size[1] + margin)

    p_x, p_y = position
    s_x, s_y = text_size
    fill_points = rectangle_to_poly(rectangle_with_margin((p_x, p_y - s_y, s_x, s_y), margin))

    cv2.fillPoly(image, np.int32([np.array(fill_points)]), background_color)
    cv2.putText(image, text, position, font, font_size, color, thickness)


def rectangle_to_poly(rectangle):
    (x, y, w, h) = rectangle
    return [[x, y], [x, y + h], [x + w, y + h], [x + w, y]]


def rectangle_with_margin(rectangle, margin):
    (x, y, w, h) = rectangle
    return (x - margin, y - margin, w + 2*margin, h + 2*margin)
