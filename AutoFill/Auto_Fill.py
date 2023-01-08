import re
import time
from requests import session, exceptions
from requests import utils


def auto_fill(account, password):
    url = "https://uis.nwpu.edu.cn/cas/login?service=https%3A%2F%2Fecampus.nwpu.edu.cn%2F%3Fpath%3Dhttps%3A%2F%2Fecampus.nwpu.edu.cn"
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'referer': 'https://ecampus.nwpu.edu.cn/main.html',
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    session1 = session()
    try:
        response = session1.get(url, headers=headers)
    except exceptions.ConnectionError as e:
        return -1
    response.encoding = 'utf-8'
    str1 = re.search('var hmSiteId = "(.*?)"', response.text)
    utils.add_dict_to_cookiejar(session1.cookies, {("Hm_lvt_" + str1.group(1)): str(int(time.time()))})
    utils.add_dict_to_cookiejar(session1.cookies, {("Hm_lpvt_" + str1.group(1)): str(int(time.time()))})
    execution = re.search('name="execution" value="(.*?)"', response.text)

    data = {
        'username': account,
        'password': password,
        'currentMenu': '1',
        'execution': execution.group(1),
        '_eventId': 'submit',
        'geolocation': '',
        'submit': 'One moment please...'
    }
    session1.post(url, data=data, headers=headers)  # received login coolie

    url = 'https://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/index.jsp'
    session1.get(url, headers=headers)
    cookie = 'JSESSIONID=' + session1.cookies.get_dict()['JSESSIONID']
    url = 'https://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Referer': 'https://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/index.jsp',
        'Host': 'yqtb.nwpu.edu.cn',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': cookie
    }
    headers2 = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Length': '196',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'yqtb.nwpu.edu.cn',
        'Origin': 'https://yqtb.nwpu.edu.cn',
        'Referer': 'https://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp',
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'cookie': cookie
    }

    response = session1.get(url, headers=headers)
    response.encoding = 'utf-8'
    match = re.search(r"url:'(.*?)'", response.text)
    name = re.search(r"姓名：(.*?)<", response.text)
    user = re.search(r"学号：(.*?)<", response.text)
    data = {
        'hsjc': '1',
        'xasymt': '1',
        'actionType': 'addRbxx',
        'userLoginId': user.group(1),
        'szcsbm': '1',
        'bdzt': '1',
        'szcsmc': '在学校',
        'sfyzz': '0',
        'sfqz': '0',
        'tbly': 'sso',
        'qtqksm': '',
        'ycqksm': '',
        'userType': '2',
        'userName': name.group(1),
    }
    url2 = r"https://yqtb.nwpu.edu.cn/wx/ry/" + match.group(1)
    response = session1.post(url2, data=data, headers=headers2)
    response.encoding = 'utf-8'
    if response.text[-3] != '1':
        return -2
