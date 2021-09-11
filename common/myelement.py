# -*- coding: utf-8 -*-

from appium.webdriver.webdriver import WebElement as AppiumWebElement


class PositionProperty(object):
    NONE = 0
    NEAR = 1
    LEFT = 2
    RIGHT = 3
    ABOVE = 4
    UNDER = 5
    INSIDE = 6

    def __init__(self, rect=None, pos=NONE):
        if rect is None:
            rect = {}
        self._pos = pos
        self._rect = rect

    @property
    def rect(self):
        return self._rect

    @property
    def pos(self):
        return self._pos


class WebElement(AppiumWebElement):
    wait_duration = 60
    _position_property = PositionProperty()

    @property
    def position_property(self):
        return self._position_property

    def set_position_property(self, pos_pro):
        self._position_property = pos_pro

    def calc_distance(self, ref_rect, rect, position):
        return self.parent.calc_distance(ref_rect, rect, position)

    def check_string_type(self, string):
        return self.parent.check_string_type(string)

    def has_widget(self, string, pos_pro_list=None):
        return self.parent.has_widget(string, pos_pro_list)

    def find_element_by_string(self, string):
        return self.parent.find_element_by_string(string)

    def find_elements_by_string(self, string, timeout=wait_duration, interval=1):
        return self.parent.find_elements_by_string(string, timeout, interval)

    def get_position_property_of_element_by_visible_text(self, string, position):
        return self.parent.get_position_property_of_element_by_visible_text(string, position)

    def near(self, string):
        return self.parent.near(string)

    def above(self, string):
        return self.parent.above(string)

    def under(self, string):
        return self.parent.under(string)

    def left(self, string):
        return self.parent.left(string)

    def right(self, string):
        return self.parent.right(string)

    def inside(self, string):
        return self.parent.inside(string)
