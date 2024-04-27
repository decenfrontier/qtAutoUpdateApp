import os
import webbrowser

from PySide2.QtWidgets import QDialog

from .auto_update_func import DownloadFileThreadClass, system_is_win, system_is_mac, update_self_win_app, ThdCheckUpdate, update_self_mac_app

from . import update_image_rc
from . import ui_winUpdate


class WndUpdateSoftware(QDialog):
    def __init__(self, parent=None, github_project_name="decenfrontier/qtAutoUpdateApp", app_name="xxx.app", cur_version="1.0",
                 official_site="https://gamerobot.fun"):
        super().__init__(parent)
        self.ui = ui_winUpdate.Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle('软件更新')
        self.resize(600, 360)

        # 绑定按钮事件
        self.ui.pushButton_azgx.clicked.connect(self.install_update)
        self.ui.pushButton_gfwz.clicked.connect(self.open_official_site)
        self.ui.pushButton_tgbb.clicked.connect(self.close)
        self.ui.pushButton_ok.clicked.connect(self.close)

        # 隐藏更新进度条和状态编辑框
        self.ui.progressBar.hide()
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setRange(0, 100)
        self.ui.label_zt.hide()
        self.ui.pushButton_ok.hide()
        self.ui.pushButton_azgx.setEnabled(False)
        self.ui.pushButton_tgbb.setEnabled(False)
        # textEdit 禁止编辑
        self.ui.textEdit.setReadOnly(True)
        self.ui.textEdit.setText("正在检查更新...")

        self.app_name = app_name
        self.cur_version = cur_version
        self.official_site = official_site
        最新版本 = "查询中..."
        self.ui.label_2.setText(最新版本)
        self.ui.label_bbh.setText(f'最新版本:{最新版本} 当前版本: {self.cur_version}')
        self.下载文件夹路径 = os.path.expanduser('~/Downloads')
        if system_is_mac():
            self.压缩包路径 = os.path.abspath(self.下载文件夹路径 + f"/{self.app_name}.zip")
        if system_is_win():
            self.压缩包路径 = os.path.abspath(self.下载文件夹路径 + f"/{self.app_name}.exe")

        print('查询最新版本')
        self.thd_check_update = ThdCheckUpdate(github_project_name, self.检查更新回到回调函数)
        self.thd_check_update.start()

    def closeEvent(self, event):
        self.thd_check_update.quit()
        # self.hide()
        # if self.allow_close is False:
        #     event.ignore()

    def 检查更新回到回调函数(self, 数据):
        print("数据", 数据)
        最新版本 = 数据['版本号']
        self.ui.label_bbh.setText(f'最新版本:{最新版本} 当前版本: {self.cur_version}')
        self.ui.textEdit.setHtml(数据['更新内容'])
        self.mac下载地址 = 数据['mac下载地址']
        self.win下载地址 = 数据['win下载地址']

        if 最新版本 == self.cur_version or 最新版本 == "":
            self.ui.label_2.setText("你使用的是最新版本")
            self.ui.pushButton_azgx.hide()
            self.ui.pushButton_tgbb.hide()
            self.ui.pushButton_ok.show()
            return

        self.ui.pushButton_azgx.setEnabled(True)
        self.ui.pushButton_tgbb.setEnabled(True)
        self.ui.label_2.setText("发现新版本")

    def install_update(self):
        print('安装更新')
        self.ui.progressBar.show()
        self.ui.label_zt.show()
        self.ui.label_zt.setText('更新中...')
        self.ui.pushButton_azgx.setEnabled(False)
        self.ui.pushButton_tgbb.setEnabled(False)
        print('mac下载地址', self.mac下载地址)
        print('win下载地址', self.win下载地址)

        if system_is_mac():
            if self.mac下载地址 == "":
                self.ui.label_zt.setText("没有找到 ManOS 系统软件下载地址")
                return
            print('安装更新 mac', self.mac下载地址, self.压缩包路径)
            self.下载文件线程 = DownloadFileThreadClass(
                下载地址=self.mac下载地址,
                保存地址=self.压缩包路径,
                窗口=self,
                编辑框=self.ui.label_zt,
                进度条=self.ui.progressBar,
                应用名称=self.app_name,
                回调函数=self.下载完成,
            )
            self.下载文件线程.start()

        if system_is_win():
            if self.win下载地址 == "":
                self.ui.label_zt.setText("没有找到 windows 系统软件下载地址")
                return
            print('安装更新 win', self.win下载地址, self.压缩包路径)

            self.下载文件线程 = DownloadFileThreadClass(
                下载地址=self.win下载地址,
                保存地址=self.压缩包路径,
                窗口=self,
                编辑框=self.ui.label_zt,
                进度条=self.ui.progressBar,
                应用名称=self.app_name,
                回调函数=self.下载完成
            )
            self.下载文件线程.start()

    def 下载完成(self, 下载结果, 保存地址):
        if not 下载结果:
            self.ui.label_zt.setText("下载更新失败")
            return
        if system_is_mac():
            update_self_mac_app(
                资源压缩包=保存地址,
                应用名称=self.app_name
            )
        if system_is_win():
            exe资源文件路径 = 保存地址
            update_self_win_app(exe资源文件路径)

    def open_official_site(self):
        # 浏览器打开网址
        print('官方网址', self.official_site)
        webbrowser.open(self.official_site)