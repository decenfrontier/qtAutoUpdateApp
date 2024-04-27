import json
import os
import platform
import shutil
import sys

from PySide2 import QtCore
from PySide2.QtCore import QThread

from .zip_file_handle import zip解压2
from .file_download_module import 下载文件
from .auto_update_read_version_module import get_latest_version_download_url


def system_is_win():
    return platform.system().lower() == 'windows'


def system_is_linux():
    return platform.system().lower() == 'linux'


def system_is_mac():
    return platform.system().lower() == 'darwin'


def win_get_self_path():
    # 如果不处于编译状态反馈空
    try:
        编译后路径 = sys._MEIPASS
        return sys.argv[0]
    except Exception:
        return ""


def mac_get_self_path():
    # 如果不处于编译状态反馈空
    try:
        编译后路径 = sys._MEIPASS
    except Exception:
        编译后路径 = os.path.abspath(".")
        # 调试的
        # 编译后路径 = "/Users/chensuilong/Desktop/pythonproject/autotest/dist/my_app.app/Contents/MacOS"
    app目录 = 编译后路径[:编译后路径.rfind('/')]
    app目录 = app目录[:app目录.rfind('/')]
    父目录名称 = 编译后路径[编译后路径.rfind('/') + 1:]
    if 父目录名称 == "MacOS":
        return app目录
    else:
        return ""


def update_self_mac_app(资源压缩包, 应用名称="my_app.app"):
    # 资源压缩包 = "/Users/chensuilong/Desktop/pythonproject/autotest/dist/my_app.2.0.zip"
    # 应用名称 例如 my_app.app 这你的压缩包里面压缩的应用文件夹名称
    MacOs应用路径 = mac_get_self_path()
    if MacOs应用路径 != "":
        app目录父目录 = MacOs应用路径[:MacOs应用路径.rfind('/')]
        print(f"资源压缩包 {资源压缩包} app目录父目录{app目录父目录} MacOs应用路径{MacOs应用路径}")
        if MacOs应用路径 != "":
            zip解压2(资源压缩包, app目录父目录, [应用名称 + '/Contents/'])
            # 解压完成就压缩包
            os.remove(资源压缩包)
            MacOs应用路径 = os.path.join(app目录父目录, 应用名称)
            # QApplication.quit()
            应用名称 = 应用名称[:应用名称.rfind('.')]
            运行命令 = f"killall {应用名称} && open -n -a {MacOs应用路径}"
            os.system(运行命令)
            return True, MacOs应用路径
    else:
        print("非MacOS编译环境")
        return False, ""


def get_run_dir():
    """ PyInstaller 单文件的运行目录  """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.realpath(sys.argv[0]))
    else:
        return sys.path[0]


def init():
    # 构建时测试运行是否正常的
    传入参数 = sys.argv
    if len(传入参数) == 2:
        参数1 = 传入参数[1]
        if 参数1 == "test":
            print("app run success")
            # 写出文件
            with open(get_run_dir() + "/test.txt", "w") as f:
                f.write("app run success")
            sys.exit(0)

    # 如果在window系统中存在旧的文件则自动删除
    自身路径Window = win_get_self_path()
    if 自身路径Window == "":
        # print("非Window编译环境")
        return False, ""
    # 检查文件是否存在
    旧的文件名 = 自身路径Window + ".old.bak"
    if os.path.exists(旧的文件名):
        # 删除文件
        os.remove(旧的文件名)


def update_self_win_app(exe资源文件路径):
    # window更新方法
    # exe资源文件路径 = r"C:\Users\csuil\.virtualenvs\QtEsayDesigner\Scripts\dist\my_app1.0.exe"
    自身路径Window = win_get_self_path()
    if 自身路径Window == "":
        print("非Window编译环境")
        return False, ""
    文件名 = os.path.basename(自身路径Window)

    # 检查文件是否存在
    旧的文件名 = 自身路径Window + ".old.bak"
    if os.path.exists(旧的文件名):
        # 删除文件
        os.remove(旧的文件名)

    os.rename(自身路径Window, 旧的文件名)
    shutil.move(exe资源文件路径, 自身路径Window)
    # 删除文件 这步放到启动时检查删除就好
    # os.remove(自身路径Window + ".old.bak") 这个运行中是无法删除的

    # 结束自身运行 然后重启自己
    os.execv(自身路径Window, sys.argv)
    os.system(f"taskkill /f /im {文件名}")
    return True, ""


class DownloadFileThreadClass(QThread):
    刷新进度条 = QtCore.Signal(int, str)  # 进度 提示文本

    def __init__(self, *args, **kwargs):
        super(DownloadFileThreadClass, self).__init__()
        self.窗口 = kwargs.get('窗口')
        self.下载地址 = kwargs.get('下载地址')
        self.保存地址 = kwargs.get('保存地址')
        self.编辑框 = kwargs.get('编辑框')
        self.进度条 = kwargs.get('进度条')
        self.应用名称 = kwargs.get('应用名称')
        self.回调函数 = kwargs.get('回调函数')

        self.刷新进度条.connect(self.刷新界面)

        # 绑定线程开始事件
        self.started.connect(self.ui_开始)
        # 绑定线程结束事件
        self.finished.connect(self.ui_结束)

    def run(self):
        if self.下载地址 == None:
            print("请传入下载地址")
            return

        def 进度(进度百分比, 已下载大小, 文件大小, 下载速率, 剩余时间):
            信息 = f"文件大小 {文件大小}MB 速度 {下载速率}MB 剩余时间 {剩余时间}秒"
            self.刷新进度条.emit(进度百分比, 信息)

        try:
            下载结果 = 下载文件(self.下载地址, self.保存地址, 进度)
            self.下载结果 = True
        except:
            self.下载结果 = False

    def ui_开始(self):
        self.编辑框.setText(f'开始下载')

    def ui_结束(self):
        print("下载结果", self.下载结果)
        print("保存地址", self.保存地址)
        self.回调函数(self.下载结果, self.保存地址)
        self.编辑框.setText(f"下载完成 {self.保存地址}")

    def 刷新界面(self, 进度, 信息):
        if self.编辑框:
            self.编辑框.setText(str(信息))
        if self.进度条:
            self.进度条.setValue(int(进度))


class ThdCheckUpdate(QThread):
    def __init__(self, github_project_name="decenfroniter/qtAutoUpdateApp", callback_func=None):
        super(ThdCheckUpdate, self).__init__()
        self.github_project_name = github_project_name
        self.callback_func = callback_func

    def run(self):
        print("开始检查更新")
        data = get_latest_version_download_url(self.github_project_name)
        self.callback_func(data)
