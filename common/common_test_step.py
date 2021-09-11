# -*- coding: utf-8 -*-

import datetime
import logging
import os
import unittest
from datetime import timedelta
from time import sleep

from PIL import Image
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from common.myelement import WebElement as MyElement
from common.mywebdriver import UnsupportedPlatformException
from common.mywebdriver import WebDriver


def test_step_info(func):
    def _func(*args, **kw):
        obj_ptr = args[0]
        obj_ptr.step = obj_ptr.step + 1
        logging.debug("test step %d %s", obj_ptr.step, func.__name__)
        result = func(*args, **kw)

        if obj_ptr.case_function_name is not None:
            # take screen shot after every step function
            # it will slow down the test and use much more storage space
            step_function_name = func.__name__
            screen_shot_name = obj_ptr.case_function_name + "/step " + str(
                obj_ptr.step) + " " + step_function_name + ".png"
            obj_ptr.driver.get_screenshot_as_file(screen_shot_name)

        return result

    return _func


class UnknownStringException(Exception):
    def __init__(self, value=None):
        self.value = value


class OutOfBoundException(Exception):
    def __init__(self, value=None):
        self.value = value


class WrongDirectionException(Exception):
    def __init__(self, value=None):
        self.value = value


class UnknownChoiceException(Exception):
    def __init__(self, value=None):
        self.value = value


class UnknownReferenceOptionError(Exception):
    def __init__(self, value=None):
        self.value = value


_YESTERDAY = 0b0001
_TOMORROW = 0b0010
_LASTWEEK = 0b0100
_NEXTWEEK = 0b1000


class CommonTestStep(unittest.TestCase):
    wait_duration = 30

    def __init__(self):
        super(CommonTestStep, self).__init__()
        self.step = 0
        self.tap_duration = 200
        self.long_tap_duration = 1000
        self.swipe_duration = 500
        self._udid = None

    def __capture_element(self, what):
        begin = what.location
        size = what.size
        start_x = begin['x']
        start_y = begin['y']
        end_x = start_x + size['width']
        end_y = start_y + size['height']
        name = str(start_x) + '_' + str(start_y) + '_' + '_' + str(end_x) + '_' + str(end_y)
        box = (start_x, start_y, end_x, end_y)
        self.driver.get_screenshot_as_file('./' + 'full_screen.png')
        image = Image.open('./' + 'full_screen.png')  # tmp是临时文件夹
        new_image = image.crop(box)
        name = './' + name + '.png'
        new_image.save(name)
        os.popen('rm ./full_screen.png')
        return name, size

    @staticmethod
    def __pil_image_similarity(file_path_src, file_path_dst):
        import math
        import operator

        image1 = Image.open(file_path_src)
        image2 = Image.open(file_path_dst)

        #    image1 = get_thumbnail(img1)
        #    image2 = get_thumbnail(img2)

        h1 = image1.histogram()
        h2 = image2.histogram()

        rms = math.sqrt(operator.sub(operator.add, list(map(lambda a, b: (a - b) ** 2, h1, h2))) / len(h1))
        return rms

    @staticmethod
    def __add_resolution_to_file_name(filename, resolution):
        os.path.splitext(filename)
        ref_image_true_name = os.path.splitext(filename)[0]
        logging.debug("ref_image_true_name:%s", ref_image_true_name)
        ref_image_ext_name = os.path.splitext(filename)[1]
        logging.debug("ref_image_ext_name:%s", ref_image_ext_name)

        ref_image_height = resolution['height']
        logging.debug("ref_image_height:%s", ref_image_height)

        ref_image_width = resolution['width']
        logging.debug("ref_image_width:%s", ref_image_width)

        added_file_name = ref_image_true_name + '_' + str(ref_image_width) + '_' + str(
            ref_image_height) + ref_image_ext_name
        logging.debug("added_file_name:%s", added_file_name)

        return added_file_name

    # noinspection PyGlobalUndefined
    def _find_day_widget_by_nearby_date(self, list_view, target_date, ref_option):
        global primary_date_string, secondary_date_string, day_widget
        if self.platformName == 'Android':
            primary_date_string = "//android.widget.CheckedTextView"
            secondary_date_string = "//android.widget.TextView"

        if ref_option & _YESTERDAY == _YESTERDAY:
            yesterday_widget = list_view.has_widget(
                "//*[@text='" + str((target_date - datetime.timedelta(days=1)).day) + "']")
        elif ref_option & _TOMORROW == _TOMORROW:
            tomorrow_widget = list_view.has_widget(
                "//*[@text='" + str((target_date + datetime.timedelta(days=1)).day) + "']")
        elif ref_option & _LASTWEEK == _LASTWEEK:
            last_week_widget = list_view.has_widget(
                "//*[@text='" + str((target_date - datetime.timedelta(days=7)).day) + "']")
        elif ref_option & _NEXTWEEK == _NEXTWEEK:
            next_week_widget = list_view.has_widget(
                "//*[@text='" + str((target_date + datetime.timedelta(days=7)).day) + "']")
        else:
            logging.error("Unknown reference option %s", str(ref_option))
            raise UnknownReferenceOptionError

        if ref_option == _YESTERDAY | _TOMORROW | _LASTWEEK | _NEXTWEEK:
            try:
                day_widget = list_view.has_widget(primary_date_string,
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.right(str((target_date - datetime.timedelta(days=1)).day)) +
                                                  self.left(str((target_date + datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))
            except NoSuchElementException:
                day_widget = list_view.has_widget(secondary_date_string,
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.right(str((target_date - datetime.timedelta(days=1)).day)) +
                                                  self.left(str((target_date + datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))

        elif ref_option == _YESTERDAY | _TOMORROW | _LASTWEEK:
            try:
                day_widget = list_view.has_widget(primary_date_string,
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.right(str((target_date - datetime.timedelta(days=1)).day)) +
                                                  self.left(str((target_date + datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))
            except NoSuchElementException:
                day_widget = list_view.has_widget(secondary_date_string,
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.right(str((target_date - datetime.timedelta(days=1)).day)) +
                                                  self.left(str((target_date + datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))

        elif ref_option == _YESTERDAY | _TOMORROW | _NEXTWEEK:
            try:
                day_widget = list_view.has_widget(primary_date_string,
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.right(str((target_date - datetime.timedelta(days=1)).day)) +
                                                  self.left(str((target_date + datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))
            except NoSuchElementException:
                day_widget = list_view.has_widget(secondary_date_string,
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.right(str((target_date - datetime.timedelta(days=1)).day)) +
                                                  self.left(str((target_date + datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))

        elif ref_option == _TOMORROW | _LASTWEEK | _NEXTWEEK:
            try:
                day_widget = list_view.has_widget(primary_date_string,
                                                  self.left(str((target_date + datetime.timedelta(days=1)).day)) +
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.under("六"))
            except NoSuchElementException:
                day_widget = list_view.has_widget(secondary_date_string,
                                                  self.left(str((target_date + datetime.timedelta(days=1)).day)) +
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.under("六"))

        elif ref_option == _YESTERDAY | _LASTWEEK | _NEXTWEEK:
            try:
                day_widget = list_view.has_widget(primary_date_string,
                                                  self.right(str((target_date - datetime.timedelta(days=1)).day)) +
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.under("六"))
            except NoSuchElementException:
                day_widget = list_view.has_widget(secondary_date_string,
                                                  self.right(str((target_date - datetime.timedelta(days=1)).day)) +
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.under("六"))

        elif ref_option == _YESTERDAY | _LASTWEEK:
            try:
                day_widget = list_view.has_widget(primary_date_string,
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.right(str((target_date - datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))
            except NoSuchElementException:
                day_widget = list_view.has_widget(secondary_date_string,
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.right(str((target_date - datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))

        elif ref_option == _YESTERDAY | _NEXTWEEK:
            try:
                day_widget = list_view.has_widget(primary_date_string,
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.right(str((target_date - datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))
            except NoSuchElementException:
                day_widget = list_view.has_widget(secondary_date_string,
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.right(str((target_date - datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))

        elif ref_option == _TOMORROW | _LASTWEEK:
            try:
                day_widget = list_view.has_widget(primary_date_string,
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.left(str((target_date + datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))
            except NoSuchElementException:
                day_widget = list_view.has_widget(secondary_date_string,
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.left(str((target_date + datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))

        elif ref_option == _TOMORROW | _NEXTWEEK:
            try:
                day_widget = list_view.has_widget(primary_date_string,
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.left(str((target_date + datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))
            except NoSuchElementException:
                day_widget = list_view.has_widget(secondary_date_string,
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.left(str((target_date + datetime.timedelta(days=1)).day)) +
                                                  self.under("六"))

        elif ref_option == _LASTWEEK:
            try:
                day_widget = list_view.has_widget(primary_date_string,
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.under("六"))
            except NoSuchElementException:
                day_widget = list_view.has_widget(secondary_date_string,
                                                  self.under(str((target_date - datetime.timedelta(days=7)).day)) +
                                                  self.under("六"))

        elif ref_option == _NEXTWEEK:
            try:
                day_widget = list_view.has_widget(primary_date_string,
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.under("六"))
            except NoSuchElementException:
                day_widget = list_view.has_widget(secondary_date_string,
                                                  self.above(str((target_date + datetime.timedelta(days=7)).day)) +
                                                  self.under("六"))
        return day_widget

    def _swipe_to_destination_half_by_half(self, start_element, end_element, destination_side="top2bottom",
                                           one_step=False):
        if destination_side == "top2top":
            start_x = start_element.location.get('x') + start_element.size['width'] / 2
            start_y = start_element.location.get('y')
            end_x = start_element.location.get('x') + start_element.size['width'] / 2
            end_y = end_element.location.get('y')
        elif destination_side == "top2bottom":
            start_x = start_element.location.get('x') + start_element.size['width'] / 2
            start_y = start_element.location.get('y')
            end_x = start_element.location.get('x') + start_element.size['width'] / 2
            end_y = end_element.location.get('y') + end_element.size['height']
        elif destination_side == "bottom2top":
            start_x = start_element.location.get('x') + start_element.size['width'] / 2
            start_y = start_element.location.get('y') + start_element.size['height']
            end_x = start_element.location.get('x') + start_element.size['width'] / 2
            end_y = end_element.location.get('y')
        elif destination_side == "bottom2bottom":
            start_x = start_element.location.get('x') + start_element.size['width'] / 2
            start_y = start_element.location.get('y') + start_element.size['height']
            end_x = start_element.location.get('x') + start_element.size['width'] / 2
            end_y = end_element.location.get('y') + end_element.size['height']
        else:
            start_x = -1
            start_y = -1
            end_x = -1
            end_y = -1

        window_size = self.driver.get_window_size()
        window_max_x = window_size['width']
        window_max_y = window_size['height']
        window_min_x = 0
        window_min_y = 0

        if start_x == window_min_x:
            start_x = 1
        elif start_x == window_max_x:
            start_x = window_max_x - 1

        if end_x == window_min_x:
            end_x = 1
        elif end_x == window_max_x:
            end_x = window_max_x - 1

        if start_y == window_min_y:
            start_y = 1
        elif start_y == window_max_y:
            start_y = window_max_y - 1

        if end_y == window_min_y:
            end_y = 1
        elif end_y == window_max_y:
            end_y = window_max_y - 1

        if not start_y == end_y:
            if not one_step:
                while abs(start_y - end_y) > 100:
                    logging.debug("swipe:%d, %d", start_y, end_y)
                    self.driver.swipe(start_x, start_y, start_x, (start_y + end_y) / 2)
                    start_y = (start_y + end_y) / 2

            logging.debug("final swipe:%d, %d", start_y, end_y)
            self.driver.swipe(start_x, start_y, start_x, end_y)

            return True
        else:
            return False

    @test_step_info
    def tap_date_in_calendar(self, des_date):
        global destination_day
        logging.debug("des_date:%s", des_date)
        logging.debug("des_date.isoweekday():%d", des_date.isoweekday())

        current_date_bar = self.driver.find_element_by_string('年')
        current_date_bar_text = current_date_bar.text
        year = current_date_bar_text[0:current_date_bar_text.index(u"年")]
        month = current_date_bar_text[current_date_bar_text.index(u"年") + 1:current_date_bar_text.index(u"月")]
        current_date = des_date.replace(day=1).replace(year=int(year)).replace(month=int(month))
        logging.debug("current_date:%s", current_date)

        list_view = self.driver.find_element_by_string("com.ziipin.homeinn:id/date_list")

        try:
            destination_month = self.driver.find_element_by_string(str(des_date.year) + "年" + str(des_date.month) + "月")

        except NoSuchElementException:
            if des_date.month != current_date.month:
                # swipe up calendar certain times according to month count from today
                if (des_date.year - current_date.year) * 12 + des_date.month - current_date.month > 0:
                    next_month_date = current_date
                    for i in range((des_date.year - current_date.year) * 12 + des_date.month - current_date.month):
                        # find next month bar and swipe it to the top, otherwise swipe calendar from bottom to top
                        next_month_date = (next_month_date.replace(day=1) + timedelta(days=32)).replace(day=1)
                        logging.debug("next_month_date:%s", next_month_date)
                        try:
                            next_month = self.driver.find_element_by_string(
                                str(next_month_date.year) + "年" + str(next_month_date.month) + "月")
                        except NoSuchElementException:
                            logging.debug(
                                "self. _swipe_to_destination_half_by_half(list_view, list_view, 'bottom2top')")
                            self._swipe_to_destination_half_by_half(list_view, list_view, "bottom2top")
                        else:
                            self.driver.drag_and_drop(next_month, current_date_bar)
                            next_month = self.driver.find_element_by_string(
                                str(next_month_date.year) + "年" + str(next_month_date.month) + "月")
                            logging.debug(
                                "self. _swipe_to_destination_half_by_half(next_month, list_view, 'top2top')")
                            self._swipe_to_destination_half_by_half(next_month, list_view, "top2top")

                    destination_month = self.driver.find_element_by_string(
                        str(des_date.year) + "年" + str(des_date.month) + "月")
                    logging.debug("self. _swipe_to_destination_half_by_half(destination_month, list_view, 'top2top')")
                    self._swipe_to_destination_half_by_half(destination_month, list_view, "top2top")

                else:
                    previous_month_date = current_date
                    logging.debug("self. _swipe_to_destination_half_by_half(current_date_bar, list_view, 'top2bottom')")
                    self._swipe_to_destination_half_by_half(current_date_bar, list_view, "bottom2bottom")
                    for i in range((current_date.year - des_date.year) * 12 + current_date.month - des_date.month):
                        # find previous month bar after swiping current month bar to the bottom
                        # swipe calendar from top to bottom
                        previous_month_date = (previous_month_date.replace(day=1) - timedelta(days=1)).replace(day=1)
                        logging.debug("previous_month_date:%s", previous_month_date)
                        try:
                            previous_month = self.driver.find_element_by_string(
                                str(previous_month_date.year) + "年" + str(previous_month_date.month) + "月")
                        except NoSuchElementException:
                            self._swipe_to_destination_half_by_half(list_view, list_view, "top2bottom")
                            logging.debug(
                                "self. _swipe_to_destination_half_by_half(list_view, list_view, 'top2bottom')")
                        else:
                            self.driver.drag_and_drop(previous_month, current_date_bar)
                            previous_month = self.driver.find_element_by_string(
                                str(previous_month_date.year) + "年" + str(previous_month_date.month) + "月")
                            logging.debug(
                                "self. _swipe_to_destination_half_by_half(previous_month, list_view, 'top2top')")
                            self._swipe_to_destination_half_by_half(previous_month, list_view, "top2top")
        else:
            # swipe up the calendar until destination month text bar reach the top of calendar
            logging.debug("self.driver.drag_and_drop(destination_month, current_date_bar)")
            self.driver.drag_and_drop(destination_month, current_date_bar)
            logging.debug("self. _swipe_to_destination_half_by_half(destination_month, list_view, 'top2top')")
            destination_month = self.driver.find_element_by_string(str(des_date.year) + "年" + str(des_date.month) + "月")
            self._swipe_to_destination_half_by_half(destination_month, list_view, "top2top")

        try:
            destination_day = self.driver.find_element_by_string(
                "//*[@text='" + str(des_date.year) + "年" + str(des_date.month) + "月']\
            /parent::*//*[@text='" + str(des_date.day) + "']")
        except NoSuchElementException:
            if des_date.isoweekday() != 6 and des_date.isoweekday() != 7:
                if 7 < des_date.day < (((des_date.replace(day=1) + timedelta(days=32)).replace(day=1)
                                        - datetime.timedelta(days=1)).day - 7):
                    logging.info("It's work day")
                    destination_day = self._find_day_widget_by_nearby_date(
                        list_view, des_date, _YESTERDAY | _TOMORROW | _LASTWEEK | _NEXTWEEK)
                elif des_date.day <= 7:
                    if des_date.day == 1:
                        logging.info("It's work day at 1st")
                        destination_day = self._find_day_widget_by_nearby_date(
                            list_view, des_date, _TOMORROW | _NEXTWEEK)
                    else:
                        logging.info("It's work day in first week")
                        destination_day = self._find_day_widget_by_nearby_date(
                            list_view, des_date, _YESTERDAY | _TOMORROW | _NEXTWEEK)
                else:
                    if des_date.day == ((des_date.replace(day=1) + timedelta(days=32)).replace(day=1)
                                        - datetime.timedelta(days=1)).day:
                        logging.info("It's work day at last day")
                        destination_day = self._find_day_widget_by_nearby_date(
                            list_view, des_date, _YESTERDAY | _LASTWEEK)
                    else:
                        logging.info("It's work day in last week")
                        destination_day = self._find_day_widget_by_nearby_date(
                            list_view, des_date, _YESTERDAY | _TOMORROW | _LASTWEEK)
            elif des_date.isoweekday() == 6:
                if 7 < des_date.day < ((des_date.replace(day=1) + timedelta(days=32)).replace(day=1)
                                       - datetime.timedelta(days=1)).day - 7:
                    logging.info("It's saturday")
                    destination_day = self._find_day_widget_by_nearby_date(
                        list_view, des_date, _YESTERDAY | _LASTWEEK | _NEXTWEEK)
                elif des_date.day <= 7:
                    if des_date.day == 1:
                        logging.info("It's saturday on 1st")
                        destination_day = self._find_day_widget_by_nearby_date(
                            list_view, des_date, _NEXTWEEK)
                    else:
                        logging.info("It's saturday in first week")
                        destination_day = self._find_day_widget_by_nearby_date(
                            list_view, des_date, _YESTERDAY | _NEXTWEEK)
                else:
                    logging.info("It's saturday in last week")
                    destination_day = self._find_day_widget_by_nearby_date(
                        list_view, des_date, _YESTERDAY | _LASTWEEK)
            elif des_date.isoweekday() == 7:
                if 7 < des_date.day < ((des_date.replace(day=1) + timedelta(days=32)).replace(day=1)
                                       - datetime.timedelta(days=1)).day - 7:
                    logging.info("It's sunday")
                    destination_day = self._find_day_widget_by_nearby_date(
                        list_view, des_date, _TOMORROW | _LASTWEEK | _NEXTWEEK)
                elif des_date.day <= 7:
                    logging.info("It's sunday in first week")
                    destination_day = self._find_day_widget_by_nearby_date(
                        list_view, des_date, _TOMORROW | _NEXTWEEK)
                else:
                    if des_date.day == ((des_date.replace(day=1) + timedelta(days=32)).replace(day=1)
                                        - datetime.timedelta(days=1)).day:
                        logging.info("It's sunday at last day")
                        destination_day = self._find_day_widget_by_nearby_date(list_view, des_date, _LASTWEEK)
                    else:
                        logging.info("It's sunday in last week")
                        destination_day = self._find_day_widget_by_nearby_date(
                            list_view, des_date, _TOMORROW | _LASTWEEK)

        self.touchAction.press(destination_day).release().perform()

    def take_screen_shot_at_every_step(self, case_function_name):
        self.case_function_name = case_function_name
        if case_function_name is not None:
            os.popen("rm -rf " + self.case_function_name)
            os.popen("mkdir " + self.case_function_name)

    def init_appium(self, desired_caps, server_port=4723, case_function_name=None):
        self.take_screen_shot_at_every_step(case_function_name)

        self.platformName = desired_caps['platformName']
        self._udid = desired_caps['udid']
        self.driver = WebDriver('http://localhost:' + str(server_port) + '/wd/hub', desired_caps)

        try:
            self.touchAction = TouchAction(self.driver)

            self.wait = WebDriverWait(self.driver, CommonTestStep.wait_duration, 1)
        except Exception as e:
            logging.error(e)
            self.driver.quit()

    def deinit_appium(self, screen_shot_file=None):
        if self.platformName == 'Android':
            self.ime = self.driver.active_ime_engine
            logging.debug("self.ime is %s", self.ime)
            if self.ime == u"io.appium.android.ime/.UnicodeIME":
                # switch to non-appium ime in order to avoid send_keys random error for numbers and english
                # characters.
                # please be noticed that ime must be switch appium unicode ime for inputting Chinese character
                imes = self.driver.available_ime_engines
                for i in [1, len(imes)]:
                    if imes[i - 1] != u"io.appium.android.ime/.UnicodeIME":
                        self.driver.activate_ime_engine(imes[i - 1])
                        self.ime = imes[i - 1]
                        logging.debug("self.ime is %s", self.ime)

        if screen_shot_file is not None:
            screen_shot_name = "./" + screen_shot_file + ".png"
            sleep(1)
            self.driver.get_screenshot_as_file(screen_shot_name)
        self.driver.quit()

    def tap_button_if_exist(self, string):
        try:
            button = self.driver.find_element_by_string(string)
            self.touchAction.tap(button).perform()
            self.last_tapped_widget = button
            logging.debug("%s button exists", string)
        except NoSuchElementException:
            logging.debug("%s button not exist", string)

    def near(self, string):
        return self.driver.near(string)

    def above(self, string):
        return self.driver.above(string)

    def under(self, string):
        return self.driver.under(string)

    def left(self, string):
        return self.driver.left(string)

    def right(self, string):
        return self.driver.right(string)

    def inside(self, string):
        return self.driver.inside(string)

    @test_step_info
    def wait_window(self, window, timeout=wait_duration, interval=1):
        if self.platformName == 'Android':
            return self.driver.wait_activity(window, timeout, interval)
        elif self.platformName == 'iOS':
            wait = WebDriverWait(self.driver, timeout, interval)
            wait.until(lambda dr: dr.find_element_by_string(window).is_displayed())
            return self.driver.find_element_by_string(window)
        else:
            raise UnsupportedPlatformException

    # function wait for act activity and check it show up or not within duration specified by parameter timeout
    # checking interval is specified by parameter interval
    @test_step_info
    def wait_and_check_window_show_up(self, window, timeout=wait_duration, interval=1):
        if self.platformName == 'Android':
            if self.driver.wait_activity(window, timeout, interval):
                logging.debug("*****" + window + " OK*****")
            else:
                logging.error("*****wait for " + window + " time out*****")

            self.assertTrue(window == self.driver.current_activity)
        elif self.platformName == 'iOS':
            wait = WebDriverWait(self.driver, timeout, interval)
            wait.until(lambda dr: dr.find_element_by_string(window).is_displayed())
            return self.driver.find_element_by_string(window)
        else:
            raise UnsupportedPlatformException

    @test_step_info
    def has_widget(self, string, pos_pro_list=None):
        return self.driver.has_widget(string, pos_pro_list)

    @test_step_info
    def has_widgets(self, string, pos_pro_list=None):
        return self.driver.has_widgets(string, pos_pro_list)

    @test_step_info
    def wait_widget_webview(self, string, timeout=wait_duration, interval=0.5):
        try:
            wait = WebDriverWait(self.driver, timeout, interval)
            wait.until(lambda dr: dr.find_element_by_accessibility_id(string).is_displayed())
        except TimeoutException as e:
            raise TimeoutException

    @test_step_info
    def wait_widget(self, string, timeout=wait_duration, interval=0.5, retry=False):
        if retry:
            wait = WebDriverWait(self.driver, timeout, interval)
            try:
                wait.until(lambda dr: dr.find_element_by_string(string).is_displayed())
            except TimeoutException:
                try:
                    self.driver.has_widget('抱歉，暂无相关结果')
                except NoSuchElementException:
                    try:
                        self.driver.has_widget('您的网络好像不太给力，请稍后再试')
                    except Exception as e:
                        logging.error(e)
                        raise TimeoutException
                    else:
                        try:
                            retry_widget = self.driver.has_widget('点击重试')
                        except NoSuchElementException:
                            self.tap_widget(self.last_tapped_widget)
                        else:
                            self.tap_widget(retry_widget)

                        wait.until(lambda dr: dr.find_element_by_string(string).is_displayed())
                else:
                    logging.error("No result, may be network error.")
                    raise TimeoutException
            else:
                return True

        else:
            wait = WebDriverWait(self.driver, timeout, interval)
            try:
                wait.until(lambda dr: dr.find_element_by_string(string).is_displayed())
            except TimeoutException:
                raise TimeoutException
            except Exception as e:
                raise e
            else:
                return True

    @test_step_info
    def wait_widget_disappear_and_get_text(self, string, timeout=wait_duration, interval=0.5):
        wait = WebDriverWait(self.driver, timeout, interval)
        text = self.driver.find_element_by_string(string).text
        try:
            wait.until_not(lambda dr: dr.find_element_by_string(string).is_displayed())
        except TimeoutException:
            raise TimeoutException
        except Exception as e:
            raise e
        else:
            return text

    @test_step_info
    def current_window(self):
        if self.platformName == 'Android':
            return self.driver.current_activity

    @test_step_info
    def current_app(self, app):
        if self.platformName == 'Android':
            current_activity = os.popen("adb shell dumpsys window w | grep mFocusedApp | awk '{printf $5}'").read()
            logging.debug("current_activity:%s", current_activity)
            return not (current_activity.find(app) == -1)

    @test_step_info
    def launch_app_if_installed(self, package, activity):
        el = self.driver.is_app_installed(package)
        self.assertTrue(el)
        el = self.driver.start_activity(package, activity)
        self.assertTrue(el)

    @test_step_info
    def input_textbox(self, string, text):
        textbox = self.driver.find_element_by_string(string)

        # if self.platformName == 'Android':
        #    # switch to non-appium ime in order to avoid send_keys random error for numbers and english characters
        #    # please be noticed that ime must be switch appium unicode ime for inputting Chinese character
        #    logging.debug("ime is %s", self.driver.active_ime_engine)
        #    self.driver.activate_ime_engine(self.ime)
        #    logging.debug("ime is %s", self.driver.active_ime_engine)

        textbox.clear()

        # self.touchAction.press(textbox, self.tap_duration).release().perform()
        textbox.send_keys(text)

    @test_step_info
    def input_secure_textbox(self, string, text):
        textbox = self.driver.find_element_by_string(string)

        if self.platformName == 'Android':
            # switch to non-appium ime in order to avoid send_keys random error for numbers and english characters
            # please be noticed that ime must be switch appium unicode ime for inputting Chinese character
            logging.debug("ime is %s", self.driver.active_ime_engine)
            self.driver.activate_ime_engine(self.ime)
            logging.debug("ime is %s", self.driver.active_ime_engine)

        self.touchAction.press(textbox, self.tap_duration).release().perform()
        # because send_keys miss first character, so here come one blank as to avoid this problem
        textbox.send_keys(text)

    @test_step_info
    def input_textbox_uft8(self, string, text, pinyin=None):
        textbox = self.driver.find_element_by_string(string)

        if self.platformName == 'Android':
            logging.debug("ime is %s", self.driver.active_ime_engine)
            self.driver.activate_ime_engine(u"io.appium.android.ime/.UnicodeIME")
            logging.debug("ime is %s", self.driver.active_ime_engine)

        self.touchAction.press(textbox, self.tap_duration).release().perform()

        if self.platformName == 'iOS':
            try:
                self.driver.find_element_by_string("//UIAKey[@label='Pinyin-Plane']")
            except NoSuchElementException:
                next_key_board = self.driver.find_element_by_string("//UIAButton[@label='Next keyboard']")
                self.touchAction.press(next_key_board, self.tap_duration).release().perform()
                self.driver.find_element_by_string("//UIATableCell[contains(@label, '简体拼音')]").click()
            except Exception as e:
                logging.error(e)
                logging.error("Unknown exception captured")

            if pinyin is not None:
                textbox.send_keys(pinyin)
                destination = self.driver.find_element_by_string(
                    "//UIACollectionCell[contains(@label, '" + text + "')]")
                self.touchAction.press(destination, self.tap_duration).release().perform()

        elif self.platformName == 'Android':
            textbox.send_keys(text)

        if self.platformName == 'Android':
            self.driver.activate_ime_engine(self.ime)
            logging.debug("ime is %s", self.driver.active_ime_engine)

    @test_step_info
    def tap_button(self, string):
        if isinstance(string, str):
            widget = self.driver.find_element_by_string(string)
            self.touchAction.tap(widget).perform()
            self.last_tapped_widget = widget
        elif isinstance(string, MyElement):
            self.touchAction.tap(string).perform()
            self.last_tapped_widget = string
        else:
            logging.error("string class is: %s", string.__class__.__name__)
            raise Exception

    @test_step_info
    def tap_widget(self, string):
        if isinstance(string, str):
            self.wait_widget(string)
            widget = self.driver.find_element_by_string(string)
            self.touchAction.tap(widget).perform()
            self.last_tapped_widget = widget
        elif isinstance(string, MyElement):
            self.touchAction.tap(string).perform()
            self.last_tapped_widget = string
        else:
            logging.error("string class is: %s", string.__class__.__name__)
            raise Exception

    @test_step_info
    def tap_widget_webview(self, string):
        self.wait_widget_webview(string)
        widget = self.driver.find_element_by_accessibility_id(string)
        self.touchAction.tap(widget).perform()
        self.last_tapped_widget = widget

    @test_step_info
    def click_widget(self, string):
        if isinstance(string, str):
            self.wait_widget(string)
            widget = self.driver.find_element_by_string(string)
            widget.click()
            self.last_tapped_widget = widget
        elif isinstance(string, MyElement):
            string.click()
            self.last_tapped_widget = string
        else:
            logging.error("string class is: %s", string.__class__.__name__)
            raise Exception

    @test_step_info
    def tap_permission_widget(self, choice="accept"):
        if choice == "accept":
            if self.platformName == 'Android':
                # in order to close permission widget, here is script to ensure script can deal with MIUI and Huawei
                # system permission widget
                self.tap_button_if_exist("//android.widget.Button[@text='允许']")
                self.tap_button_if_exist("com.huawei.systemmanager:id/btn_allow")
            elif self.platformName == 'iOS':
                try:
                    self.driver.switch_to_alert().accept()
                except Exception as e:
                    logging.error(e)
                    logging.info("no alert exist")
            else:
                raise UnsupportedPlatformException

        elif choice == "deny":
            if self.platformName == 'Android':
                # in order to close permission widget, here is script to ensure script can deal with MIUI and Huawei
                # system permission widget
                self.tap_button_if_exist("//android.widget.Button[@text='拒绝']")
                self.tap_button_if_exist("com.huawei.systemmanager:id/btn_forbbid")
            elif self.platformName == 'iOS':
                self.driver.switch_to_alert().deny()
            else:
                raise UnsupportedPlatformException
        else:
            logging.error("Unknown choice %s", str(choice))
            raise UnknownChoiceException

    @test_step_info
    def tap_button_sibling_widget(self, button_string, widget_string):
        self.wait_widget(widget_string)
        widget = self.driver.find_element_by_string(widget_string)

        if WebDriver.check_string_type(button_string) == "id":
            logging.debug("string is id")
            button = widget.parent.find_element_by_id(button_string)
        elif WebDriver.check_string_type(button_string) == "xpath":
            logging.debug("string is xpath")
            button = widget.parent.find_element_by_xpath(button_string)
        else:
            logging.error("string is unknown")
            raise UnknownStringException

        self.assertTrue(button)
        self.touchAction.tap(button).perform()
        self.last_tapped_widget = button

    @test_step_info
    def long_tap_widget(self, string, x=0, y=0, duration=1000):
        self.wait_widget(string)
        widget = self.driver.find_element_by_string(string)
        size = widget.size
        if x == "middle":
            x = size["width"] / 2

        if y == "middle":
            y = size["height"] / 2

        if x == 0 and y == 0:
            size = widget.size
            x = size["width"] / 2
            y = size["height"] / 2

        if duration == 1000:
            duration = self.long_tap_duration

        self.touchAction.long_press(widget, x, y, duration).release().perform()
        self.last_tapped_widget = widget

    @test_step_info
    def tap_widget_if_image_alike(self, string, ref_image_name, after_image_name=None):
        self.wait_widget(string)
        star_btn = self.driver.find_element_by_string(string)
        element_image_name, element_image_size = self.__capture_element(star_btn)
        logging.debug("elementImageSize:%s", element_image_size)
        added_file_name = self.__add_resolution_to_file_name(ref_image_name, element_image_size)

        if self.__pil_image_similarity(added_file_name, element_image_name) == 0:
            self.touchAction.tap(star_btn).perform()
            self.last_tapped_widget = star_btn
        else:
            logging.debug("image not alike")
            self.assertTrue(0)

        if after_image_name is not None:
            element_image_name, element_image_size = self.__capture_element(star_btn)
            added_file_name = self.__add_resolution_to_file_name(after_image_name, element_image_size)
            similarity = self.__pil_image_similarity(added_file_name, element_image_name)
            self.assertEqual(0, similarity)

    @test_step_info
    def check_widget_if_image_alike(self, string, ref_image_name):
        self.wait_widget(string)
        star_btn = self.driver.find_element_by_string(string)
        element_image_name, element_image_size = self.__capture_element(star_btn)
        logging.debug("elementImageSize:%s", element_image_size)
        added_file_name = self.__add_resolution_to_file_name(ref_image_name, element_image_size)

        if self.__pil_image_similarity(added_file_name, element_image_name) == 0:
            self.touchAction.press(star_btn).release().perform()
        else:
            logging.debug("image not alike")
            self.assertTrue(0)

    @test_step_info
    def swipe_widget(self, string, start_x=0, start_y=0, end_x=0, end_y=0, duration=500):
        self.wait_widget(string)
        widget = self.driver.find_element_by_string(string)
        size = widget.size
        logging.debug("size %d %d", size["width"], size["height"])
        if start_x == "middle":
            start_x = size["width"] / 2

        if start_y == "middle":
            start_y = size["height"] / 2

        if end_x == "middle":
            end_x = size["width"] / 2

        if end_y == "middle":
            end_y = size["height"] / 2
        logging.debug("start_x:%d start_y:%d end_x:%d end_y:%d", start_x, start_y, end_x, end_y)

        lx = widget.location.get('x')
        ly = widget.location.get('y')
        logging.debug("location x:%d location y:%d", ly, ly)
        window_size = self.driver.get_window_size()
        logging.debug("window size %d %d", window_size["width"], window_size["height"])
        if (start_x > size['width'] or start_x < 0
                or start_y > size['height'] or start_y < 0
                or end_x > size['width'] or end_x < 0
                or end_y > size['height'] or end_y < 0
                or start_x + lx > window_size['width']
                or start_y + ly > window_size['height']
                or end_x + lx > window_size['width']
                or end_y + ly > window_size['height']):
            logging.error("Out of bound exception")
            raise OutOfBoundException

        if duration == 500:
            duration = self.swipe_duration
        self.driver.swipe(start_x + lx, start_y + ly, end_x + lx, end_y + ly, duration)

    @test_step_info
    def swipe_widget_by_direction(self, string, direction, duration=500):
        self.wait_widget(string)
        widget = self.driver.find_element_by_string(string)
        # if self.platformName == 'Android':
        size = widget.size
        logging.debug("size %s %s", size["width"], size["height"])
        lx = widget.location.get('x')
        ly = widget.location.get('y')
        logging.debug("location x:%s location y:%s", lx, ly)
        window_size = self.driver.get_window_size()
        logging.debug("window size %s %s", window_size["width"], window_size["height"])

        if (size['width'] / 2 + lx > window_size['width']
                or size['height'] / 2 + ly > window_size['height']):
            logging.error("Out of bound exception")
            raise OutOfBoundException

        if duration == 500:
            duration = self.swipe_duration

        if direction == "up":
            self.driver.swipe(size['width'] / 2 + lx, size['height'] - 1 + ly
                              , size['width'] / 2 + lx, 1 + ly, duration)
        elif direction == "down":
            self.driver.swipe(size['width'] / 2 + lx, 1 + ly
                              , size['width'] / 2 + lx, size['height'] - 1 + ly, duration)
        elif direction == "left":
            self.driver.swipe(size['width'] - 1 + lx, size['height'] / 2 + ly
                              , 1 + lx, size['height'] / 2 + ly, duration)
        elif direction == "right":
            self.driver.swipe(1 + lx, size['height'] / 2 + ly
                              , size['width'] - 1 + lx, size['height'] / 2 + ly, duration)
        else:
            logging.error("Wrong direction %s", str(direction))
            raise WrongDirectionException

    @test_step_info
    def swipe_by_direction(self, direction, duration=500):
        # if self.platformName == 'Android':
        window_size = self.driver.get_window_size()
        logging.debug("window size %s %s", window_size["width"], window_size["height"])
        lx = window_size["width"]
        ly = window_size["height"]

        if duration == 500:
            duration = self.swipe_duration

        if direction == "up":
            self.driver.swipe(lx / 2, ly - 1, lx / 2, 1, duration)
        elif direction == "down":
            self.driver.swipe(lx / 2, 1, lx / 2, ly - 1, duration)
        elif direction == "left":
            self.driver.swipe(lx - 1, ly / 2, 1, ly / 2, duration)
        elif direction == "right":
            self.driver.swipe(1, ly / 2, lx - 1, ly / 2, duration)
        else:
            logging.error("Wrong direction %s", str(direction))
            raise WrongDirectionException

    @test_step_info
    def swipe_up_and_retry(self, tips, button_string):
        self.swipe_by_direction("up")
        self.driver.has_widget(tips)
        retry_widget = self.driver.has_widget(button_string)
        self.tap_widget(retry_widget)

    @test_step_info
    def pinch_widget(self, string, percentage=200, steps=50):
        self.wait_widget(string)
        widget = self.driver.find_element_by_string(string)

        self.driver.pinch(widget, percentage, steps)

    @test_step_info
    def find_toast(self, message, timeout, poll_frequency):
        message = '//*[@text=\'{}\']'.format(message)
        element = WebDriverWait(self.driver, timeout, poll_frequency).until(
            expected_conditions.presence_of_element_located((By.XPATH, message)))
        logging.debug(element)

    @property
    def udid(self):
        return self._udid
