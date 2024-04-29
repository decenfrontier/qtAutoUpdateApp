import os
import shutil

from PySide2.QtCore import QThread, Signal
from PySide2.QtWidgets import QDialog
import zipfile

from qtAutoUpdateApp.auto_update_module.auto_update_read_version_module import get_latest_version_download_url
from qtAutoUpdateApp.auto_update_module.file_download_module import download_file
import utils
from . import update_image_rc
from . import ui_winUpdate
from utils import *


class WndUpdateSoftware(QDialog):
    sig_update_finish_restart = Signal()
    def __init__(self, parent=None, github_project_name="decenfrontier/qtAutoUpdateApp", app_name="xxx.app", cur_version="1.0",
                 official_site="https://gamerobot.fun"):
        super().__init__(parent)
        self.ui = ui_winUpdate.Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle('软件更新')
        self.resize(600, 360)

        # 绑定按钮事件
        self.ui.pushButton_azgx.clicked.connect(self.install_update)
        self.ui.pushButton_tgbb.clicked.connect(self.close)
        self.ui.pushButton_ok.clicked.connect(self.close)

        # 连接自定义信号槽
        self.thd_check_update = ThdCheckUpdate(github_project_name)
        self.thd_check_update.sig_get_download_info_finish.connect(lambda data:self.on_get_download_info(data))

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
        latest_version = "查询中..."
        self.ui.label_2.setText(latest_version)
        self.ui.label_bbh.setText(f'最新版本:{latest_version} 当前版本: {self.cur_version}')
        self.download_path = "."
        self.patcher_path = "./patcher.zip"
        self.thd_check_update.start()

    def closeEvent(self, event):
        self.thd_check_update.quit()

    def on_get_download_info(self, data):
        latest_version = data['version']
        self.ui.label_bbh.setText(f'最新版本:{latest_version} 当前版本: {self.cur_version}')
        self.ui.textEdit.setHtml(data['update_content'])
        self.patcher_download_url = data['patcher_download_url']

        if latest_version == self.cur_version or latest_version == "":
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

        self.thd_download_file = ThdDownloadFile(
            download_url=self.patcher_download_url,
            save_path=self.patcher_path,
            wnd=self,
            edt=self.ui.label_zt,
            process_bar=self.ui.progressBar,
            app_name=self.app_name,
        )
        self.thd_download_file.sig_download_finish.connect(self.on_download_file_finish)
        self.thd_download_file.start()

    def on_download_file_finish(self, download_result, save_path):
        if not download_result:
            self.ui.label_zt.setText("下载更新失败")
            return
        patcher_zip_path = save_path
        extract_folder_path = "./patcher"
        log.info("正在创建解压目录...")
        # 如果存在的话先删除, 再创建新的patcher文件夹用于解压
        if os.path.exists(extract_folder_path):
            shutil.rmtree(extract_folder_path)
        os.makedirs(extract_folder_path)
        with zipfile.ZipFile(patcher_zip_path, 'r') as zf:
            zf.extractall(extract_folder_path)
        log.info("解压完成")
        log.info("1 关闭update窗口")
        self.close()
        log.info("2 启动launcher")
        utils.run_exe("./launcher.exe")
        log.info("3 关闭main窗口")
        self.sig_update_finish_restart.emit()


class ThdCheckUpdate(QThread):
    # 检查更新线程
    sig_get_download_info_finish = Signal(dict)  # 定义信号在线程类中
    def __init__(self, github_project_name="decenfroniter/qtAutoUpdateApp"):
        super().__init__()
        self.github_project_name = github_project_name

    def run(self):
        print("开始检查更新")
        data = get_latest_version_download_url(self.github_project_name)
        self.sig_get_download_info_finish.emit(data)
        # self.callback_func(data)  # 这里不能回调, 用别的线程更新页面数据会报错


class ThdDownloadFile(QThread):
    # 下载文件线程
    sig_refresh_process_bar = Signal(int, str)  # 进度 提示文本
    sig_download_finish = Signal(str, str)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.wnd = kwargs.get('wnd')
        self.download_url = kwargs.get('download_url')
        self.save_path = kwargs.get('save_path')
        self.edt = kwargs.get('edt')
        self.process_bar = kwargs.get('process_bar')
        self.app_name = kwargs.get('app_name')
        self.sig_refresh_process_bar.connect(self.refresh_ui)

    def run(self):
        self.edt.setText(f'开始下载')
        if self.download_url == None:
            print("请传入下载地址")
            return

        def callback(progress_percent, already_download_size, file_size, download_rate, time_left):
            info = f"文件大小 {file_size}MB, 速度 {download_rate}MB/s, 剩余时间 {time_left}秒"
            self.sig_refresh_process_bar.emit(progress_percent, info)

        try:
            download_file(self.download_url, self.save_path, callback)
            self.download_result = True
        except:
            self.download_result = False

        print("下载结果:", self.download_result)
        print("保存地址:", self.save_path)
        self.edt.setText(f"下载完成 {self.save_path}")
        self.sig_download_finish.emit(self.download_result, self.save_path)

    def refresh_ui(self, progress_percent, info):
        if self.edt:
            self.edt.setText(str(info))
        if self.process_bar:
            self.process_bar.setValue(int(progress_percent))