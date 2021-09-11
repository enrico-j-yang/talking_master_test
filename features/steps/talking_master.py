# -*- coding: utf-8 -*-


import base64
import logging
import os
import time
from subprocess import Popen, PIPE

from behave import *

cwd = os.getcwd()


@given(u'应用已登录微信')
def step_impl(context):
    pass


@then(u'微信显示首页')
def step_impl(context):
    el = context.phoneTestStep.wait_window(".ui.LauncherUI")
    assert el


@when(u'用户打开微信')
def step_impl(context):
    package = context.phoneTestStep.driver.current_package
    if package != 'io.aiui.car':
        process = Popen(
            ['adb', '-s', context.phoneTestStep.udid, 'shell', 'am', 'start', '-n', 'com.tencent.mm/.ui.LauncherUI'],
            stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        if stdout.find(b'Starting') < 0:
            assert False
    else:
        assert False


@when(u'用户点击【{tap}】页面')
def step_impl(context, tap):
    context.phoneTestStep.tap_widget(tap)


@then(u'微信显示发现页面')
def step_impl(context):
    el = context.phoneTestStep.has_widget(u"小程序")
    assert el


@when(u'用户点击【{widget}】控件')
def step_impl(context, widget):
    context.phoneTestStep.tap_widget(widget)


@then(u'微信显示小程序页面')
def step_impl(context):
    el = context.phoneTestStep.wait_window(".plugin.appbrand.ui.AppBrandLauncherUI", timeout=5)
    assert el


@when(u'用户点击搜索')
def step_impl(context):
    context.phoneTestStep.tap_widget('com.tencent.mm:id/he')


@then(u'微信显示小程序搜索页面')
def step_impl(context):
    el = context.phoneTestStep.wait_window(".plugin.appbrand.ui.AppBrandSearchUI", timeout=5)
    assert el


@when(u'用户输入【{widget}】并搜索')
def step_impl(context, widget):
    context.phoneTestStep.wait_widget('com.tencent.mm:id/ht', timeout=5)
    context.phoneTestStep.input_textbox('com.tencent.mm:id/ht', widget)
    context.phoneTestStep.driver.press_keycode(66)
    context.phoneTestStep.driver.press_keycode(66)


@then(u'微信显示【{widget}】小程序列表项')
def step_impl(context, widget):
    el = context.phoneTestStep.has_widget(widget)
    assert el


@when(u'用户点击【{widget}】小程序')
def step_impl(context, widget):
    context.phoneTestStep.tap_widget(widget)


@then(u'小程序显示【{widget}】按钮')
def step_impl(context, widget):
    context.phoneTestStep.wait_widget_webview(widget)


@when(u'用户点击小程序【{widget}】按钮')
def step_impl(context, widget):
    context.phoneTestStep.tap_widget(widget)


@then(u'小程序显示【{widget}】提示')
def step_impl(context, widget):
    context.phoneTestStep.wait_widget_webview(widget)


@when(u'用户下划微信页面')
def step_impl(context):
    context.phoneTestStep.wait_widget(u'微信', timeout=5)
    list_widget = context.phoneTestStep.has_widget('com.tencent.mm:id/c5q')
    tap_widget = context.phoneTestStep.has_widget(u'发现')
    context.phoneTestStep._swipe_to_destination_half_by_half(list_widget, tap_widget, 'top2top', one_step=True)


@when(u'TTS手机获取小程序【{widget}】提示下的文本')
def step_impl(context, widget):
    # widgets = context.phoneTestStep.has_widgets('//android.view.View', context.phoneTestStep._under(widget))
    widgets = context.phoneTestStep.driver.find_elements_by_xpath('//android.view.View')
    for widget in widgets:
        text = widget.get_attribute("contentDescription")
        logging.debug(text)
        logging.debug(len(text))
        if len(text) > 10:
            context.talking_text = text
            break


@then(u'TTS手机获取成功')
def step_impl(context):
    context.talking_text = context.talking_text.replace(u'\r\n', '')
    # context.talking_text = context.talking_text.replace(u'\n', '')
    context.talking_text = context.talking_text.replace(u'、', '')
    # context.talking_text = context.talking_text.replace(u'？', '')
    context.talking_text = context.talking_text.replace(u'，', '')
    # context.talking_text = context.talking_text.replace(u'；', '')
    # context.talking_text = context.talking_text.replace(u'。', '')
    logging.debug(context.talking_text)
    context.talking_file = (context.talking_text[0:4]) + '.mp3'

    # check whether audio file exists in tts_audio_files folder
    # if exist, use it as cache to push into speaker phone
    data = None
    if not os.path.isfile(cwd + '/tts_audio_files/' + context.talking_file):
        result = context.client.synthesis(context.talking_text, 'zh', 1, {'vol': 10, 'spd': 10, 'per': 1})
        if not isinstance(result, dict):
            with open(cwd + '/tts_audio_files/' + context.talking_file, 'wb') as f:
                f.write(result)
                data = result
    else:
        with open(cwd + '/tts_audio_files/' + context.talking_file, 'rb') as f:
            data = f.read()

    # check whether audio file exists in speaker phone
    # if exists, use it as cache to play
    process = Popen(
        ['adb', '-s', context.speakerTestStep.udid, 'shell', 'ls', u'/sdcard/' + context.talking_file],
        stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    logging.debug(stdout)
    logging.debug(stderr)

    if stderr.__len__() > 0:
        base64data = (base64.b64encode(data)).decode()
        context.speakerTestStep.driver.push_file('/sdcard/' + context.talking_file, base64data)


@when(u'小程序显示【{widget}】提示')
def step_impl(context, widget):
    context.phoneTestStep.wait_widget_webview(widget, timeout=10, interval=0.1)


@when(u'小程序显示倒计时结束')
def step_impl(context):
    widgets = context.phoneTestStep.driver.find_elements_by_xpath('//android.view.View')
    text = '1'
    for widget in widgets:
        text = widget.get_attribute("contentDescription")
        logging.debug(text)
        logging.debug(len(text))
        if len(text) > 0:
            break

    logging.debug("sleep " + text + "s")
    if int(text) >= 2:
        time.sleep(int(text) - 2)


@then(u'TTS手机播放文本')
def step_impl(context):
    logging.info(
        'adb -s ' + context.phoneTestStep.udid + ' shell am start -a android.intent.action.VIEW -d file://sdcard/' + context.talking_file)
    process = Popen(
        ['adb', '-s', context.speakerTestStep.udid, 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d',
         'file://sdcard/' + context.talking_file],
        stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    logging.debug(stdout)
    logging.debug(stderr)


@then(u'小程序显示口技得分')
def step_impl(context):
    context.phoneTestStep.wait_widget_webview(u'口技得分')
    # try:
    #    context.phoneTestStep.wait_widget_webview(u'点击抽奖', timeout=3, interval=0.1)
    # except TimeoutException:
    #    pass
    # else:
    #    context.phoneTestStep.tap_widget(u'点击抽奖')


@when(u'用户截图记录得分')
def step_impl(context):
    context.phoneTestStep.driver.get_screenshot_as_file('screenshot.png')

    try:
        os.remove('screenshots/Step:用户截图记录得分.png')
    except Exception as e:
        pass
    os.rename('screenshot.png', 'Step:用户截图记录得分.png')
    os.system("mv Step:用户截图记录得分.png screenshots/")


@then(u'截图成功')
def step_impl(context):
    pass


@when(u'用户返回')
def step_impl(context):
    context.phoneTestStep.driver.press_keycode(4)


@then(u'小程序显示【{widget}】结果')
def step_impl(context, widget):
    context.phoneTestStep.wait_widget_webview(widget, timeout=10, interval=0.1)


@when(u'用户截图记录评估得分')
def step_impl(context):
    context.phoneTestStep.driver.get_screenshot_as_file('screenshot.png')

    try:
        os.remove('screenshots/Step:用户截图记录得分.png')
    except Exception as e:
        pass
    os.rename('screenshot.png', 'Step:用户截图记录得分.png')
    os.system("mv Step:用户截图记录得分.png screenshots/")


@when(u'用户进入【{little_program}】小程序')
def step_impl(context, little_program):
    context.execute_steps('''
        #当      用户点击【发现】页面
        #那么    微信显示发现页面

        #当      用户点击【小程序】控件
        #那么    微信显示小程序页面

        #当      用户点击搜索
        #那么    微信显示小程序搜索页面

        #当      用户输入【口技比拼】并搜索
        #那么    微信显示【口技比拼】小程序列表项

        #当      用户点击【口技比拼】小程序
        当      用户下划微信页面

        当      用户点击【口技比拼】小程序
        ''')


@when(u'用户开始一次个人比拼')
def step_impl(context):
    context.execute_steps('''
        当      用户点击小程序【开始比拼】按钮
        那么    小程序显示【请阅读题目】提示

        当      TTS手机获取小程序【请阅读题目】提示下的文本
        那么    TTS手机获取成功

        当      小程序显示倒计时结束
        那么    TTS手机播放文本
        ''')


@when(u'用户重复【{times}】次个人比拼和得分截图')
def step_impl(context, times):
    context.execute_steps('''
        当      用户开始一次个人比拼
        那么    小程序显示口技得分
        而且    小程序显示【再来一次】按钮

        当      用户截图记录得分
        那么    截图成功

        当      用户返回
        那么    小程序显示【开始比拼】按钮
        而且    小程序显示【口技评估】按钮

        当      用户点击小程序【口技评估】按钮
        那么    小程序显示【口技评估得分】结果

        当      用户截图记录评估得分
        那么    截图成功

        当      用户返回
        ''')