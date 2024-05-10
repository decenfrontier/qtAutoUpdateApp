import os
import sys

# 从命令行参数中读取版本号
version = sys.argv[1]

cur_file_path = os.path.dirname(__file__)
versionFilePath = os.path.join(cur_file_path, "version.py")
print(f"edit file {versionFilePath} output: version = {version}")
# 覆盖写出文件 version.py 中
with open(versionFilePath, 'w') as f:
    f.write(f'version = "{version}"')
