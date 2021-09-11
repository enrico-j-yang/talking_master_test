# -*- coding: utf-8 -*-


import logging
import os
import threading

try:
    import Queue as queue
except ImportError:
    import queue

from aip import AipSpeech

from common.common_test_step import CommonTestStep
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='talking_master.log',
                    filemode='w')
#################################################################################################
# 定义一个StreamHandler，将WARN级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.WARN)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


#################################################################################################


def init_phone_common_test_step(test_step_queue, test_step, desired_caps, server_port=4723):
    try:
        # test_step = CommonTestStep()
        test_step.init_appium(desired_caps, server_port)
        test_step_queue.put({'server_port': server_port, 'test_step': test_step})
    except WebDriverException as e:
        logging.error("WebDriverException")
        logging.error(e)
        exit(-1)


def init_speaker_common_test_step(test_step_queue, test_step, desired_caps, server_port=4723):
    try:
        # test_step = CommonTestStep()
        test_step.init_appium(desired_caps, server_port)
        test_step_queue.put({'server_port': server_port, 'test_step': test_step})
    except WebDriverException as e:
        logging.error("WebDriverException")
        logging.error(e)
        exit(-1)


def before_all(context):
    APP_ID = '10806843'  # Enter your Baidu AIP app id
    API_KEY = '0Fkof84e2GRZBeTj5ChGKudC'  # Enter your Baidu AIP api key
    SECRET_KEY = '8XcykRm4NcyIDIDTboOi06D8jY1ci1nr'  # Enter your Baidu AIP secret key
    context.client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    try:
        os.mkdir("screenshots")
    except FileExistsError:
        pass

    try:
        os.mkdir("tts_audio_files")
    except FileExistsError:
        pass

    pass


def after_all(context):
    pass


def before_feature(context, feature):
    test_step_queue = queue.Queue()
    context.phoneTestStep = None
    context.phoneTestStep = CommonTestStep()
    options = Options()

    options.add_experimental_option("androidProcess", "com.tencent.mm:tools")

    phone_desired_caps = {'automationName': 'UiAutomator2',
                          'platformName': 'Android',
                          'platformVersion': '6.0',
                          'deviceName': 'Android Phone',
                          'systemPort': 8021,
                          'chromeOptions': options.to_capabilities(),
                          'appPackage': 'com.tencent.mm',
                          'appActivity': '.ui.LauncherUI',
                          'autoLaunch': False,
                          'unicodeKeyboard': True,
                          'resetKeyboard': True,
                          'autoGrantPermissions': True,
                          'newCommandTimeout': 120,
                          'udid': 'bbf221417d93'}
    # phone_desired_caps['app'] = PATH(
    #    '../../../apps/Assistant_v0.5.0_production.apk'
    # )
    # phone_desired_caps['appPackage'] = 'com.android.calculator2'
    # phone_desired_caps['appActivity'] = '.Calculator'

    # context.phoneTestStep.init_appium(phone_desired_caps, 4723)
    thread_phone = threading.Thread(target=init_phone_common_test_step,
                                    args=(test_step_queue, context.phoneTestStep, phone_desired_caps, 4723))

    context.speakerTestStep = None
    context.speakerTestStep = CommonTestStep()

    speaker_desired_caps = {'automationName': 'UiAutomator2',
                            'platformName': 'Android',
                            'platformVersion': '7.0',
                            'deviceName': 'Android Phone',
                            'systemPort': 8022,
                            'appPackage': 'com.android.calculator2',
                            'appActivity': '.Calculator',
                            'autoLaunch': False,
                            'unicodeKeyboard': True,
                            'resetKeyboard': True,
                            'autoGrantPermissions': True,
                            'newCommandTimeout': 120,
                            'udid': 'EJL4C17718001588'}
    # speaker_desired_caps['app'] = PATH(
    #    '../../../apps/Assistant_v0.5.0_production.apk'
    # )

    # context.speakerTestStep.init_appium(speaker_desired_caps, 4823)
    thread_speaker = threading.Thread(target=init_speaker_common_test_step,
                                      args=(test_step_queue, context.speakerTestStep, speaker_desired_caps, 4823))

    thread_phone.start()
    thread_speaker.start()
    thread_phone.join()
    thread_speaker.join()

    '''
    qsize = test_step_queue.qsize()
    for i in range(qsize):
        data = test_step_queue.get()
        if data['server_port'] == 4723:
            context.phoneTestStep = data['test_step']
        elif data['server_port'] == 4823:
            context.speakerTestStep = data['test_step']
        else:
            logging.error("queue number error")
    '''


def after_feature(context, feature):
    context.phoneTestStep.deinit_appium()
    context.speakerTestStep.deinit_appium()


def before_scenario(context, scenario):
    pass


def after_scenario(context, scenario):
    context.phoneTestStep.driver.get_screenshot_as_file('screenshot.png')

    try:
        os.remove('screenshots/Case:' + str(scenario.name) + '.png')
    except Exception as e:
        pass
    os.rename('screenshot.png', 'Case:' + str(scenario.name) + '.png')
    os.system("mv \'Case:" + str(scenario.name) + ".png\' screenshots/")
    if scenario.name.find(u"安装") < 0:
        context.phoneTestStep.driver.close_app()


def before_step(context, step):
    pass


def after_step(context, step):
    if step.status == "failed":
        context.phoneTestStep.driver.get_screenshot_as_file('screenshot.png')

        try:
            os.remove('screenshots/Step:' + str(step.name) + '.png')
        except Exception as e:
            pass
        os.rename('screenshot.png', 'Step:' + str(step.name) + '.png')
        os.system("mv Step:" + str(step.name) + ".png screenshots/")
