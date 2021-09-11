# -*- coding: utf-8 -*-

import logging
from collections import OrderedDict

from appium import webdriver
from selenium.common.exceptions import NoSuchElementException

from common.myelement import PositionProperty
from common.myelement import WebElement as MyElement


class UnsupportedPlatformException:
    pass


class WebDriver(webdriver.Remote):
    def __init__(self, command_executor='http://127.0.0.1:4444/wd/hub',
                 desired_capabilities=None, browser_profile=None, proxy=None, keep_alive=False):

        super(WebDriver, self).__init__(command_executor, desired_capabilities, browser_profile, proxy, keep_alive)
        self.platformName = desired_capabilities['platformName']

    def create_web_element(self, element_id):
        """
        Creates a web element with the specified element_id.
        Overrides method in Selenium WebDriver in order to always give them
        Appium WebElement
        """
        return MyElement(self, element_id)

    def has_widget(self, string, pos_pro_list=None):
        logging.debug("has_widget searching string is " + string)
        if pos_pro_list is None:
            return self.find_element_by_string(string)
        else:
            logging.debug("position property list %d", len(pos_pro_list))
            candidates = self.find_elements_by_string(string)
            logging.debug("candidates %s", str(candidates))
            # qualified_candidates = candidates
            rect_distance_dic = {}
            for ref_pos in pos_pro_list:
                logging.debug("ref_pos.pos:%d", ref_pos.pos)
                logging.debug("ref_pos.pos:%s", str(ref_pos.rect))
                rect_distance_dic.clear()
                # candidates = qualified_candidates
                logging.debug("candidates count %s", len(candidates))
                # qualified_candidates = []
                for element in candidates:
                    can_rect = {'left_side': element.location.get('x'),
                                'top_side': element.location.get('y'),
                                'right_side': element.location.get('x') + element.size['width'],
                                'bottom_side': element.location.get('y') + element.size['height']}
                    logging.debug("candidate %s rect: %s", element.text, str(can_rect))
                    distance = self.calc_distance(ref_pos.rect, can_rect, ref_pos.pos)
                    if distance is not None:
                        logging.debug("candidate %s distance:%s", element.text, str(distance))
                        rect_distance_dic[distance] = element
                        # qualified_candidates.append(element)
                        logging.debug("add element %s", element.text)
                        logging.debug("rect_distance_dic %s", str(rect_distance_dic))
                        # logging.debug("qualified_candidates %s", str(qualified_candidates))

            # assert len(rect_distance_dic)==len(qualified_candidates)

            if len(rect_distance_dic.items()) == 0:
                raise NoSuchElementException
            else:
                order_dict = OrderedDict(sorted(rect_distance_dic.items(), key=lambda t: t[0]))
                # logging.debug("return %s %s", str(rect_distance_dic.values()[0]), str(qualified_candidates[0]))
                it = iter(order_dict.values())
                el = next(it)
                return el

    def has_widgets(self, string, pos_pro_list=None):
        logging.debug("has_widget searching string is " + string)
        if pos_pro_list is None:
            return self.find_elements_by_string(string)
        else:
            logging.debug("position property list %d", len(pos_pro_list))
            candidates = self.find_elements_by_string(string)
            logging.debug("candidates %s", str(candidates))
            qualified_candidates = candidates
            rect_distance_dic = {}
            for ref_pos in pos_pro_list:
                logging.debug("ref_pos.pos:%d", ref_pos.pos)
                logging.debug("ref_pos.pos:%s", str(ref_pos.rect))
                rect_distance_dic.clear()
                candidates = qualified_candidates
                logging.debug("candidates count %s", len(candidates))
                qualified_candidates = []
                for element in candidates:
                    can_rect = {'left_side': element.location.get('x'),
                                'top_side': element.location.get('y'),
                                'right_side': element.location.get('x') + element.size['width'],
                                'bottom_side': element.location.get('y') + element.size['height']}
                    logging.debug("candidate %s rect: %s", element.text, str(can_rect))
                    distance = self.calc_distance(ref_pos.rect, can_rect, ref_pos.pos)
                    logging.debug("candidate %s distance:%s", element.text, str(distance))
                    if distance is not None:
                        rect_distance_dic[distance] = element
                        qualified_candidates.append(element)
                        logging.debug("add element %s", element.text)
                        logging.debug("rect_distance_dic %s", str(rect_distance_dic))
                        logging.debug("qualified_candidates %s", str(qualified_candidates))

            # assert len(rect_distance_dic)==len(qualified_candidates)

            if len(rect_distance_dic.items()) == 0:
                raise NoSuchElementException
            else:
                order_dict = OrderedDict(sorted(rect_distance_dic.items(), key=lambda t: t[0]))
                # logging.debug("return %s %s", str(rect_distance_dic.values()[0]), str(qualified_candidates[0]))
                it = iter(order_dict.values())
                return it

    def find_element_by_string(self, string):
        logging.debug("find_element_by_string: " + string)
        if self.check_string_type(string) == "id":
            logging.debug("string is id")
            element = self.find_element_by_id(string)
        elif self.check_string_type(string) == "xpath":
            logging.debug("string is xpath")
            element = self.find_element_by_xpath(string)
        else:
            element = self.find_element_by_visible_text(string)
        return element

    def find_elements_by_string(self, string):
        logging.debug("find_elements_by_string: " + string)
        # logging.debug("element is %s", element)
        if self.check_string_type(string) == "id":
            logging.debug("string is id")
            elements = self.find_elements_by_id(string)
        elif self.check_string_type(string) == "xpath":
            logging.debug("string is xpath")
            elements = self.find_elements_by_xpath(string)
        else:
            elements = self.find_elements_by_visible_text(string)

        logging.debug("elements is " + str(elements))
        return elements

    def find_element_by_visible_text(self, text):
        try:
            logging.debug("using find_element_by_accessibility_id")
            element = self.find_element_by_accessibility_id(text)
            if element is None:
                raise NoSuchElementException

        except NoSuchElementException:
            if self.platformName == 'Android':
                try:
                    logging.debug("using find_element_by_xpath with identical text property")
                    element = self.find_element_by_xpath("//*[@text='" + text + "']")
                    if element is None:
                        raise NoSuchElementException
                except NoSuchElementException:
                    logging.debug("using find_element_by_xpath with partial text property")
                    element = self.find_element_by_xpath("//*[contains(@text, '" + text + "')]")
                    if element is None:
                        raise NoSuchElementException
            elif self.platformName == 'iOS':
                try:
                    logging.debug("using find_element_by_xpath with identical label property")
                    element = self.find_element_by_xpath("//*[@label='" + text + "']")
                    if element is None:
                        raise NoSuchElementException
                except NoSuchElementException:
                    try:
                        logging.debug("using find_element_by_xpath with identical name property")
                        element = self.find_element_by_xpath("//*[@name='" + text + "']")
                        if element is None:
                            raise NoSuchElementException
                    except NoSuchElementException:
                        try:
                            logging.debug("using find_element_by_xpath with partial label property")
                            element = self.find_element_by_xpath("//*[contains(@label, '" + text + "')]")
                            if element is None:
                                raise NoSuchElementException
                        except NoSuchElementException:
                            logging.debug("using find_element_by_xpath with partial name property")
                            element = self.find_element_by_xpath("//*[contains(@name, '" + text + "')]")
                            if element is None:
                                raise NoSuchElementException
            else:
                raise UnsupportedPlatformException
        return element

    def find_elements_by_visible_text(self, text):
        try:
            logging.debug("using find_elements_by_accessibility_id")
            elements = self.find_elements_by_accessibility_id(text)
            if len(elements) == 0:
                raise NoSuchElementException
        except NoSuchElementException:
            if self.platformName == 'Android':
                logging.debug("using find_elements_by_xpath with partial text property")
                elements = self.find_elements_by_xpath("//*[contains(@text, '" + text + "')]")
                if len(elements) == 0:
                    raise NoSuchElementException
            elif self.platformName == 'iOS':
                try:
                    logging.debug("using find_elements_by_xpath with partial label property")
                    elements = self.find_elements_by_xpath("//*[contains(@label, '" + text + "')]")
                    if len(elements) == 0:
                        raise NoSuchElementException
                except NoSuchElementException:
                    logging.debug("using find_elements_by_xpath with partial name property")
                    elements = self.find_elements_by_xpath("//*[contains(@name, '" + text + "')]")
                    if len(elements) == 0:
                        raise NoSuchElementException
            else:
                raise UnsupportedPlatformException
        return elements

    def get_position_property_of_element_by_visible_text(self, string, position):
        logging.debug("get_position_property_of_element_by_visible_text:%s", string)
        element = self.find_element_by_visible_text(string)

        rect = {'left_side': element.location.get('x'),
                'top_side': element.location.get('y'),
                'right_side': element.location.get('x') + element.size['width'],
                'bottom_side': element.location.get('y') + element.size['height']}
        logging.debug("rect:" + str(rect))
        pos_pro = PositionProperty(rect, position)
        # element.set_position_property(posPro)
        return pos_pro

    def near(self, string):
        if isinstance(string, str):
            pos_pro = self.get_position_property_of_element_by_visible_text(string, PositionProperty.NEAR)
        elif isinstance(string, MyElement):
            rect = {'left_side': string.location.get('x'),
                    'top_side': string.location.get('y'),
                    'right_side': string.location.get('x') + string.size['width'],
                    'bottom_side': string.location.get('y') + string.size['height']}
            logging.info("rect:" + str(rect))
            pos_pro = PositionProperty(rect, PositionProperty.NEAR)
        else:
            logging.error("string class is: %s", string.__class__.__name__)
            raise Exception
        pos_pro_list = (pos_pro,)
        return pos_pro_list

    def above(self, string):
        if isinstance(string, str):
            pos_pro = self.get_position_property_of_element_by_visible_text(string, PositionProperty.ABOVE)
        elif isinstance(string, MyElement):
            rect = {'left_side': string.location.get('x'),
                    'top_side': string.location.get('y'),
                    'right_side': string.location.get('x') + string.size['width'],
                    'bottom_side': string.location.get('y') + string.size['height']}
            logging.info("rect:" + str(rect))
            pos_pro = PositionProperty(rect, PositionProperty.ABOVE)
        else:
            logging.error("string class is: %s", string.__class__.__name__)
            raise Exception

        pos_pro_list = (pos_pro,)
        return pos_pro_list

    def under(self, string):
        if isinstance(string, str):
            pos_pro = self.get_position_property_of_element_by_visible_text(string, PositionProperty.UNDER)
        elif isinstance(string, MyElement):
            rect = {'left_side': string.location.get('x'),
                    'top_side': string.location.get('y'),
                    'right_side': string.location.get('x') + string.size['width'],
                    'bottom_side': string.location.get('y') + string.size['height']}
            logging.debug("rect:" + str(rect))
            pos_pro = PositionProperty(rect, PositionProperty.UNDER)
        else:
            logging.error("string class is: %s", string.__class__.__name__)
            raise Exception
        pos_pro_list = (pos_pro,)
        return pos_pro_list

    def left(self, string):
        if isinstance(string, str):
            pos_pro = self.get_position_property_of_element_by_visible_text(string, PositionProperty.LEFT)
        elif isinstance(string, MyElement):
            rect = {'left_side': string.location.get('x'),
                    'top_side': string.location.get('y'),
                    'right_side': string.location.get('x') + string.size['width'],
                    'bottom_side': string.location.get('y') + string.size['height']}
            logging.info("rect:" + str(rect))
            pos_pro = PositionProperty(rect, PositionProperty.LEFT)
        else:
            logging.error("string class is: %s", string.__class__.__name__)
            raise Exception
        pos_pro_list = (pos_pro,)
        return pos_pro_list

    def right(self, string):
        if isinstance(string, str):
            pos_pro = self.get_position_property_of_element_by_visible_text(string, PositionProperty.RIGHT)
        elif isinstance(string, MyElement):
            rect = {'left_side': string.location.get('x'),
                    'top_side': string.location.get('y'),
                    'right_side': string.location.get('x') + string.size['width'],
                    'bottom_side': string.location.get('y') + string.size['height']}
            logging.debug("rect:" + str(rect))
            pos_pro = PositionProperty(rect, PositionProperty.RIGHT)
        else:
            logging.error("string class is: %s", string.__class__.__name__)
            raise Exception
        pos_pro_list = (pos_pro,)
        return pos_pro_list

    def inside(self, string):
        if isinstance(string, str):
            pos_pro = self.get_position_property_of_element_by_visible_text(string, PositionProperty.INSIDE)
        elif isinstance(string, MyElement):
            rect = {'left_side': string.location.get('x'),
                    'top_side': string.location.get('y'),
                    'right_side': string.location.get('x') + string.size['width'],
                    'bottom_side': string.location.get('y') + string.size['height']}
            logging.info("rect:" + str(rect))
            pos_pro = PositionProperty(rect, PositionProperty.INSIDE)
        else:
            logging.error("string class is: %s", string.__class__.__name__)
            raise Exception

        pos_pro_list = (pos_pro,)
        return pos_pro_list

    @staticmethod
    def check_string_type(string):
        logging.debug("string is " + string)

        try:
            # id string?
            pos = string.index(":id/")
            logging.debug("pos is " + str(pos))
        except Exception as e:
            try:
                # xpath string?
                pos = string.index("//")
                logging.debug("pos is " + str(pos))
            except Exception as e:
                return "unknown"
            else:
                if pos == 0:
                    return "xpath"
        else:
            return "id"

    @staticmethod
    def calc_distance(ref_rect, rect, position):
        # 判断两个矩形的距离
        logging.debug(str(
            ("ref_rect: ", ref_rect['left_side'], ref_rect['right_side'], ref_rect['top_side'],
             ref_rect['bottom_side'])))
        logging.debug(str(("rect: ", rect['left_side'], rect['right_side'], rect['top_side'], rect['bottom_side'])))

        # 假如矩形1的中心大于矩形2的左边，小于矩形2的右边，大于矩形2的上边，小于矩形2的下边
        # 那么定义矩形1在矩形2之内，否则为在之外
        if position == PositionProperty.NEAR:
            logging.debug(
                "(rect['left_side']+rect['right_side'])/2: " + str((rect['left_side'] + rect['right_side']) / 2))
            logging.debug(
                "(rect['top_side']+rect['bottom_side'])/2: " + str((rect['top_side'] + rect['bottom_side']) / 2))
            logging.debug("(ref_rect['left_side']+ref_rect['right_side'])/2: " + str(
                (ref_rect['left_side'] + ref_rect['right_side']) / 2))
            logging.debug("(ref_rect['top_side']+ref_rect['bottom_side'])/2: " + str(
                (ref_rect['top_side'] + ref_rect['bottom_side']) / 2))

            if (((rect['left_side'] + rect['right_side']) / 2 < ref_rect['left_side'] and rect['right_side'] < (
                    ref_rect['left_side'] + ref_rect['right_side']) / 2) or
                    ((rect['left_side'] + rect['right_side']) / 2 > ref_rect['right_side'] and rect['left_side'] > (
                            ref_rect['left_side'] + ref_rect['right_side']) / 2) or
                    ((rect['top_side'] + rect['bottom_side']) / 2 < ref_rect['top_side'] and rect['bottom_side'] < (
                            ref_rect['top_side'] + ref_rect['bottom_side']) / 2) or
                    ((rect['top_side'] + rect['bottom_side']) / 2 > ref_rect['bottom_side'] and rect['top_side'] > (
                            ref_rect['top_side'] + ref_rect['bottom_side']) / 2)):
                x_dist = abs(
                    (rect['top_side'] + rect['bottom_side']) / 2 - (ref_rect['top_side'] + ref_rect['bottom_side']) / 2)
                y_dist = abs(
                    (rect['top_side'] + rect['bottom_side']) / 2 - (ref_rect['top_side'] + ref_rect['bottom_side']) / 2)
                dist = (x_dist ** 2 + y_dist ** 2) ** 0.5
            else:
                dist = None

            logging.debug("dist: " + str(dist))

            return dist
        elif position == PositionProperty.LEFT:
            logging.debug(
                "(rect['left_side']+rect['right_side'])/2: " + str((rect['left_side'] + rect['right_side']) / 2))

            if ((rect['left_side'] + rect['right_side']) / 2 < ref_rect['left_side'] and rect['right_side'] < (
                    ref_rect['left_side'] + ref_rect['right_side']) / 2):
                x_dist = abs(
                    (rect['top_side'] + rect['bottom_side']) / 2 - (ref_rect['top_side'] + ref_rect['bottom_side']) / 2)
            else:
                x_dist = None

            logging.debug("x_dist: " + str(x_dist))

            dist = x_dist

            return dist
        elif position == PositionProperty.RIGHT:
            logging.debug(
                "(rect['left_side']+rect['right_side'])/2: " + str((rect['left_side'] + rect['right_side']) / 2))

            if ((rect['left_side'] + rect['right_side']) / 2 > ref_rect['right_side'] and rect['left_side'] > (
                    ref_rect['left_side'] + ref_rect['right_side']) / 2):
                x_dist = abs(
                    (rect['top_side'] + rect['bottom_side']) / 2 - (ref_rect['top_side'] + ref_rect['bottom_side']) / 2)
            else:
                x_dist = None

            logging.debug("x_dist: " + str(x_dist))

            dist = x_dist
            return dist
        elif position == PositionProperty.ABOVE:
            logging.debug(
                "(rect['top_side']+rect['bottom_side'])/2: " + str((rect['top_side'] + rect['bottom_side']) / 2))

            if ((rect['top_side'] + rect['bottom_side']) / 2 < ref_rect['top_side'] and rect['bottom_side'] < (
                    ref_rect['top_side'] + ref_rect['bottom_side']) / 2):
                y_dist = abs(
                    (rect['top_side'] + rect['bottom_side']) / 2 - (ref_rect['top_side'] + ref_rect['bottom_side']) / 2)
            else:
                y_dist = None

            logging.debug("y_dist: " + str(y_dist))

            dist = y_dist
            return dist
        elif position == PositionProperty.UNDER:
            logging.debug(
                "(rect['top_side']+rect['bottom_side'])/2: " + str((rect['top_side'] + rect['bottom_side']) / 2))

            if ((rect['top_side'] + rect['bottom_side']) / 2 > ref_rect['bottom_side'] and rect['top_side'] > (
                    ref_rect['top_side'] + ref_rect['bottom_side']) / 2):
                y_dist = abs(
                    (rect['top_side'] + rect['bottom_side']) / 2 - (ref_rect['top_side'] + ref_rect['bottom_side']) / 2)
            else:
                y_dist = None

            logging.debug("y_dist: " + str(y_dist))

            dist = y_dist
            return dist
        # 假如矩形1的中心大于矩形2的左边，小于矩形2的右边，大于矩形2的上边，小于矩形2的下边
        # 那么定义矩形1在矩形2之内
        elif position == PositionProperty.INSIDE:
            logging.debug(
                "(rect['left_side']+rect['right_side'])/2: " + str((rect['left_side'] + rect['right_side']) / 2))
            logging.debug(
                "(rect['top_side']+rect['bottom_side'])/2: " + str((rect['top_side'] + rect['bottom_side']) / 2))

            if (ref_rect['left_side'] <= (rect['left_side'] + rect['right_side']) / 2 <= ref_rect['right_side'] and
                    ref_rect['top_side'] <= (rect['top_side'] + rect['bottom_side']) / 2 <= ref_rect['bottom_side']):
                x_dist = abs(
                    (rect['top_side'] + rect['bottom_side']) / 2 - (ref_rect['top_side'] + ref_rect['bottom_side']) / 2)
                y_dist = abs(
                    (rect['top_side'] + rect['bottom_side']) / 2 - (ref_rect['top_side'] + ref_rect['bottom_side']) / 2)
                dist = (x_dist ** 2 + y_dist ** 2) ** 0.5
            else:
                dist = None

            logging.debug("dist: " + str(dist))

            return dist
