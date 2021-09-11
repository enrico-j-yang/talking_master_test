# 口技比拼小程序脚本

## 环境配置

### 安装Node.js

MacOS安装
>brew install node

### 安装Appium

Appium本身基于Node.js，因此可以通过安装Node.js后使用npm安装，建议使用淘宝源提高速度

> npm install -g appium --registry=http://registry.npm.taobao.org

另外也可以下载带控件检查工具的UI工具[Appium-Desktop](https://github.com/appium/appium-desktop/releases)

### 安装Python3

测试脚本由python编写，为避免版本兼容问题，请安装python3版本

Windows平台请到https://www.python.org/downloads/ 下载安装3.6版本

MacOS平台可以通过brew install python3安装

### 安装pip包管理工具

[pip](https://pip.pypa.io/en/stable/installing/)包管理工具可以比较方便地安装python各种模块

### 安装behave

测试脚本使用python下的BDD工具behave编写，只是运行脚本，可以通过pip安装behave 1.2.5版本。

>pip install behave

由于1.2.5版本在Pycharm环境下调试有bug。测试人员修改调试脚本，需要取github上behave最新代码进行安装。

>pip install git+https://github.com/behave/behave

### 安装Appium Python客户端

>pip install Appium-Python-Client

## 脚本设置

在features目录environment.py脚本中填写测试机的安卓版本
```
desired_caps['platformVersion'] = '7.0'
```
填写被测安卓应用的包名与启动Activity
```
desired_caps['appPackage'] = 'com.android.calculator2'
desired_caps['appActivity'] = '.Calculator'
```
## 运行脚本

### 运行全部场景（用例）
>behave --no-logcapture --no-capture -k

### 以标签名批量运行场景（用例）

>behave --no-logcapture --no-capture -k -t tagname

其中tagname为标签名字，大小写敏感

## 脚本发送数据确认

运行完测试脚本后，talking_master.log的日志文件，日志的等级请修改environment.py的日志设置的level
```
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='appium_python_client.log',
                    filemode='w')
```
level可以选择ERROR,WARNING,INFO,DEBUG