import requests
import time



def download_file(url, save_path, callback_func=None):
    if callback_func:
        start_time = time.time()
    print('开始下载:', url)
    r = requests.get(url, stream=True, verify=False)
    with open(save_path, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        # 获取百分比 并调用回调函数
        for chunk in r.iter_content(chunk_size=10 * 1024):
            if chunk:
                f.write(chunk)
                f.flush()
                if callback_func:
                    # 转化为百分比
                    进度百分比 = int(f.tell() * 100 / total_length)
                    已下载大小 = f.tell() / 1024 / 1024
                    文件大小MB = total_length / 1024 / 1024
                    下载速率MB = 已下载大小 / (time.time() - start_time)
                    # 获取剩余时间取秒
                    剩余时间 = (文件大小MB - 已下载大小) / 下载速率MB
                    剩余时间 = int(剩余时间)
                    # 所有数据保留两位小数
                    下载速率MB = round(下载速率MB, 2)
                    文件大小MB = round(文件大小MB, 2)
                    已下载大小 = round(已下载大小, 2)
                    进度百分比 = round(进度百分比, 2)
                    callback_func(进度百分比, 已下载大小, 文件大小MB, 下载速率MB, 剩余时间)
    return True
