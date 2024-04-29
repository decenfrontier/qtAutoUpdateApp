import re

import requests


def get_latest_version_download_url(project_name, token=""):
    # 通过访问最新的页面 获取版本号和下载地址和更新内容
    # https://github.com/decenfroniter/qtAutoUpdateApp/releases/latest
    # 镜像地址也可以自己造一个 https://quiet-boat-a038.duolabmeng.workers.dev/
    #https://github.com/decenfroniter/qoq/releases/expanded_assets/v0.1.5
    if token:
        url = f"https://user:{token}@mirror.ghproxy.com/https://github.com/{project_name}/releases/latest"
    else:
        url = f"https://mirror.ghproxy.com/https://github.com/{project_name}/releases/latest"
    jsondata = requests.get(url)
    return get_resp_info(jsondata.text, project_name)


def get_resp_info(resp, project_name):
    # 获取版本号
    # <a href="/decenfroniter/qtAutoUpdateApp" class="no-underline flex-grow-0">
    # <h1 class="h3 lh-condensed mb-1 pr-4 flex-grow-1">
    version = resp.find('<span class="ml-1">')
    version = resp[version + len('<span class="ml-1">'):]
    version = version[:version.find('</span>')].strip()
    print(version)

    # 获取更新内容
    # <div data-pjax="true" data-test-selector="body-content" data-view-component="true" class="markdown-body my-3"><h1>自动更新程序</h1>
    # <ul>
    # <li>更新了自动构建</li>
    # <li>自动获取版本</li>
    # <li>自动下载</li>
    # <li>自动替换</li>
    # </ul></div>
    # </div>
    update_content = resp.find(
        '<div data-pjax="true" data-test-selector="body-content" data-view-component="true" class="markdown-body my-3">')
    update_content = resp[update_content + len(
        '<div data-pjax="true" data-test-selector="body-content" data-view-component="true" class="markdown-body my-3">'):]
    update_content = update_content[:update_content.find('</div>')]
    print(update_content)

    # 获取下载地址列表
    #             <a href="/decenfroniter/qtAutoUpdateApp/releases/download/0.0.4/my_app_MacOS.zip" rel="nofollow" data-skip-pjax>
    #               <span class="px-1 text-bold">my_app_MacOS.zip</span>
    #
    #             </a>
    download_url_list = []
    patcher_download_url = ""
    installer_download_url = ""
    # https://github.com/decenfroniter/qoq/releases/expanded_assets/v0.1.5
    url = f"https://ghproxy.com/https://github.com/{project_name}/releases/expanded_assets/{version}"
    expanded_assets_url_resp = requests.get(url).text

    pattern = re.compile( r'class="Truncate-text text-bold">(.*?)</span>' )
    result = pattern.findall(expanded_assets_url_resp)
    # print(result)
    for item in result:
        # print(item)
        download_url = f"https://ghproxy.com/https://github.com/{project_name}/releases/download/{version}/{item}"
        if item.find('Source code') != -1:  # 跳过源代码
            continue
        download_url_list.append({item: download_url})
        if item.find('patcher') != -1:
            patcher_download_url = download_url
        if item.find('installer') != -1:
            installer_download_url = download_url
    print(download_url_list)

    # 获取发布时间
    # <relative-time datetime="2022-07-22T17:32:41Z" class="no-wrap"></relative-time>
    release_time = expanded_assets_url_resp.find('<relative-time datetime="')
    release_time = expanded_assets_url_resp[release_time + len('<relative-time datetime="'):]
    release_time = release_time[:release_time.find('"')]
    # 去掉 t z
    release_time = release_time.replace("T", " ").replace("Z", "")

    # 版本号大于20个字符就清空
    if len(version) > 20:
        version = ""
        release_time = ""
        update_content = ""

    return {
        "version": version,
        "download_url_list": download_url_list,
        "update_content": update_content,
        "release_time": release_time,
        "patcher_download_url": patcher_download_url,
        "installer_download_url": installer_download_url,
    }


# 测试
if __name__ == '__main__':
    # data = get_latest_version_download_url("InkTimeRecord/TTime")  # 开源
    data = get_latest_version_download_url("decenfroniter/yt", token='')  # 私有
    print(data)
    # data = 解析网页信息("")
    # print(data)
    # data = 获取最新版本号和下载地址("decenfroniter/qtAutoUpdateApp")
    # print(data)
