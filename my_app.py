import json
import sys

from PySide6.QtWidgets import QWidget, QLabel, QTextEdit, QVBoxLayout, QApplication, QMainWindow, QPushButton

import version
import auto_update_module

PROJECT_NAME = "duolabmeng6/qtAutoUpdateApp"
APP_NAME = "my_app.app"
CUR_VERSION = version.version
OFFICIAL_SITE = "https://github.com/duolabmeng6/qtAutoUpdateApp"


class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.init_ui()

    def 按钮_检查更新点击(self):
        # 弹出窗口
        self.winUpdate = auto_update_module.WndUpdateSoftware(github_project_name=PROJECT_NAME,
                                                              app_name=APP_NAME,
                                                              cur_version=CUR_VERSION,
                                                              official_site=OFFICIAL_SITE)
        self.winUpdate.show()

    def init_ui(self):
        self.resize(400, 300)
        self.setWindowTitle(f"自动更新的程序演示")
        self.show()
        # 创建容器
        self.main_widget = QWidget()

        self.btn_check_update = QPushButton(self.main_widget)
        self.btn_check_update.clicked.connect(self.按钮_检查更新点击)
        self.btn_check_update.resize(160, 100)
        self.btn_check_update.setText(f'检查更新')
        self.btn_check_update.show()

        self.label = QLabel(self.main_widget)
        self.label.setText(f'当前版本:{CUR_VERSION}')
        self.label.resize(160, 100)
        self.label.show()

        self.label2 = QLabel(self.main_widget)
        self.label2.setText(f'最新版本:查询中')
        self.label2.resize(160, 100)
        self.label2.show()

        # 编辑框
        self.textEdit = QTextEdit(self.main_widget)
        self.textEdit.resize(400, 150)
        self.textEdit.show()

        # 创建布局容器并应用
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.addWidget(self.btn_check_update)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.textEdit, 1)
        self.setCentralWidget(self.main_widget)

        self.thd_check_update = auto_update_module.ThdCheckUpdate(
            PROJECT_NAME, self.callback_check_update)
        self.thd_check_update.start()

    def callback_check_update(self, 数据):
        print("数据", 数据)
        最新版本 = 数据['版本号']
        self.label2.setText(f'最新版本:{最新版本}')
        self.textEdit.setText(json.dumps(数据, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    auto_update_module.init()

    app = QApplication(sys.argv)
    win = Main()
    sys.exit(app.exec())
