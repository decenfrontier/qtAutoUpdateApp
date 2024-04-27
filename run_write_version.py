# -*- coding: utf-8 -*-
import os

# version读取环境变量, 然后写入到version.py中的version变量中
version = os.environ.get('version')
print("version:", version)

cur_file_path = os.path.dirname(__file__)
versionFilePath = os.path.join(cur_file_path, "version.py")
print("edit file {versionFilePath} output: version = {version}")
# 覆盖写出文件 version.py 中
with open(versionFilePath, 'w') as f:
    f.write(f'version = "{version}"')

