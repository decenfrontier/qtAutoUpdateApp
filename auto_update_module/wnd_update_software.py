import os
import shutil

from PySide2.QtCore import QObject, QThread, Signal
from PySide2.QtWidgets import QDialog
import zipfile

import requests

from qtAutoUpdateApp.auto_update_module.file_download_module import download_file
from . import update_image_rc
from .ui_winUpdate import Ui_Form
from .process import run_exe


class WndUpdateSoftware(QDialog, Ui_Form):
    sig_update_finish_restart = Signal()
    def __init__(self, parent=None, client_version="v0.1.0", get_update_info_req={}, protocal='https://', server_host_name=''):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('软件更新')
        self.resize(600, 360)

        self.get_update_info_req = get_update_info_req
        self.protocal = protocal
        self.server_host_name = server_host_name

        # 绑定按钮事件
        self.pushButton_azgx.clicked.connect(self.install_update)
        self.pushButton_tgbb.clicked.connect(self.close)
        self.pushButton_ok.clicked.connect(self.close)

        # 连接自定义信号槽
        self.thd_check_update = ThdCheckUpdate(self.get_update_info_req, protocal, server_host_name)
        self.thd_check_update.sig_get_download_info_finish.connect(lambda data:self.on_get_download_info(data))

        # 隐藏更新进度条和状态编辑框
        self.progressBar.hide()
        self.progressBar.setValue(0)
        self.progressBar.setRange(0, 100)
        self.label_zt.hide()
        self.pushButton_ok.hide()
        self.pushButton_azgx.setEnabled(False)
        self.pushButton_tgbb.setEnabled(False)
        # textEdit 禁止编辑
        self.textEdit.setReadOnly(True)
        self.textEdit.setText("正在检查更新...")

        self.client_version = client_version
        latest_version = "查询中..."
        self.label_2.setText(latest_version)
        self.label_bbh.setText(f'最新版本:{latest_version} 当前版本: {self.client_version}')
        self.download_path = "."
        self.patcher_path = "./patcher.zip"
        self.thd_check_update.start()

    def closeEvent(self, event):
        self.thd_check_update.quit()

    def on_get_download_info(self, data: dict):
        latest_version = data.get('latest_version', '')
        self.label_bbh.setText(f'最新版本:{latest_version} 当前版本: {self.client_version}')
        self.textEdit.setMarkdown(data.get('update_info'))
        self.patcher_download_url = data.get('patcher_download_url')

        if latest_version == self.client_version or latest_version == '':
            self.label_2.setText("你使用的是最新版本")
            self.pushButton_azgx.hide()
            self.pushButton_tgbb.hide()
            self.pushButton_ok.show()
            return

        self.pushButton_azgx.setEnabled(True)
        self.pushButton_tgbb.setEnabled(True)
        self.label_2.setText("发现新版本")

    def install_update(self):
        print('安装更新')
        self.progressBar.show()
        self.label_zt.show()
        self.label_zt.setText('更新中...')
        self.pushButton_azgx.setEnabled(False)
        self.pushButton_tgbb.setEnabled(False)

        self.thd_download_file = ThdDownloadFile(
            download_url=self.patcher_download_url,
            save_path=self.patcher_path,
            wnd=self,
            edt=self.label_zt,
            process_bar=self.progressBar,
        )
        self.thd_download_file.sig_download_finish.connect(self.on_download_file_finish)
        self.thd_download_file.start()

    def on_download_file_finish(self, download_result, save_path):
        if not download_result:
            self.label_zt.setText("下载更新失败")
            return
        patcher_zip_path = save_path
        extract_folder_path = "./patcher"
        print("正在创建解压目录...")
        # 如果存在的话先删除, 再创建新的patcher文件夹用于解压
        if os.path.exists(extract_folder_path):
            shutil.rmtree(extract_folder_path)
        os.makedirs(extract_folder_path)
        with zipfile.ZipFile(patcher_zip_path, 'r') as zf:
            zf.extractall(extract_folder_path)
        print("解压完成")
        print("1 关闭update窗口")
        self.close()
        print("2 启动launcher")
        run_exe("./launcher.exe")
        print("3 关闭main窗口")
        self.sig_update_finish_restart.emit()


class ThdCheckUpdate(QThread):
    # 检查更新线程
    sig_get_download_info_finish = Signal(dict)  # 定义信号在线程类中

    def __init__(self, get_update_info_req, protocal, server_host_name) -> None:
        super().__init__()
        self.get_update_info_req = get_update_info_req
        self.protocal = protocal
        self.server_host_name = server_host_name

    def run(self):
        print("开始检查更新")
        data = self.send_request_get_update_info()
        # 收到更新数据后通知updater窗口
        self.sig_get_download_info_finish.emit(data)

    def send_request_get_update_info(self):
        path = '/api/netauth/v1/get_update_info'
        body = self.get_update_info_req
        url = self.protocal + self.server_host_name + path
        response = requests.post(
            url, 
            json=body, 
            timeout=2,
            verify=False
        )
        if response.status_code != 200:
            return {}
        return response.json()


class ThdDownloadFile(QThread):
    # 下载文件线程
    sig_refresh_process_bar = Signal(int, str)  # 进度 提示文本
    sig_download_finish = Signal(bool, str)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.wnd = kwargs.get('wnd')
        self.download_url = kwargs.get('download_url')
        self.save_path = kwargs.get('save_path')
        self.edt = kwargs.get('edt')
        self.process_bar = kwargs.get('process_bar')
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
        except Exception as e:
            print(f"下载文件异常: {e}")
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