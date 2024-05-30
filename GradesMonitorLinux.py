import os
import re
import rsa
import time
import json
import email
import base64
import imaplib
import smtplib
import requests
from email.mime.text import MIMEText


## 部署个人信息
# 设置服务器所需信息
# qq邮箱服务器地址
mail_host = 'smtp.qq.com'
# qq用户名
mail_user = '12345678'
# 密码(部分邮箱为授权码)
mail_pass = 'abcdefg'
# 邮件发送方邮箱地址
sender = '12345678@qq.com'
# 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
receivers = ['12345678@qq.com']
# 设置翱翔门户信息
# 账户
username = '2021000000'
# 密码
password = 'abcdefg'

def email_msg(title: str, content: str) -> None:

    # 设置email信息
    # 邮件内容设置
    message = MIMEText(content, 'plain', 'utf-8')
    # 邮件主题'
    message['Subject'] = title
    # 发送方信息
    message['From'] = sender
    # 接受方信息
    message['To'] = receivers[0]

    # 登录并发送邮件
    smtp_obj = smtplib.SMTP()
    # 连接到服务器
    smtp_obj.connect(mail_host, 25)
    # 登录到服务器
    smtp_obj.login(mail_user, mail_pass)
    # 发送
    smtp_obj.sendmail(sender, receivers, message.as_string())
    # 退出
    smtp_obj.quit()


headers = {
    'accept': ('text/html,application/xhtml+xml,application/xml;q=0.9,image/avif, '
        'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
    'accept-encoding': 'deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'referer': 'https://ecampus.nwpu.edu.cn/main.html',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/103.0.0.0 Safari/537.36')
}
headers2 = headers.copy()
headers2['X-Requested-With'] = 'XMLHttpRequest'

URL = ("https://uis.nwpu.edu.cn/cas/login?service=https%3A%2F%2Fecampus.nwpu.edu.cn"
       "%2F%3Fpath%3Dhttps%3A%2F%2Fecampus.nwpu.edu.cn")
session = requests.session()
if os.path.isfile('cookies.txt'):
    with open('cookies.txt', 'r', encoding='utf-8') as f:
        new_cookies = json.loads(f.read())
    session.cookies.update(new_cookies)
    response = session.get(URL, headers=headers)
    response.encoding = 'utf-8'
else:
    response = session.get(URL, headers=headers)
    response.encoding = 'utf-8'
    str1 = re.search('var hmSiteId = "(.*?)"', response.text)
    new_cookies = {
        ("Hm_lvt_" + str1.group(1)): str(int(time.time())),
        ("Hm_lpvt_" + str1.group(1)): str(int(time.time()))
    }
    session.cookies.update(new_cookies)
    # RSA加密password
    URL_key = 'https://uis.nwpu.edu.cn/cas/jwt/publicKey'
    public_key = session.get(URL_key, headers=headers2).text
    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key.encode())
    password = rsa.encrypt(password.encode(), public_key)
    password = "__RSA__" + base64.b64encode(password).decode()

if len(response.history) == 0:
    #  没有重定向到主页，开始输入账号
    execution = re.search('name="execution" value="(.*?)"', response.text)

    URL = 'https://uis.nwpu.edu.cn/cas/mfa/detect'
    data = {
        'username': username,
        'password': password,
    }
    response = session.post(URL, data=data, headers=headers2)
    state_code = json.loads(response.text)['data']['state']

    URL = 'https://uis.nwpu.edu.cn/cas/mfa/initByType/secureemail?state=' + state_code
    response = session.get(URL, headers=headers2)
    gid = json.loads(response.text)['data']['gid']

    URL = 'https://uis.nwpu.edu.cn/attest/api/guard/secureemail/send'
    data = {'gid': gid}
    headers3 = headers2.copy()
    headers3['Content-Type'] = 'application/json; charset=UTF-8'
    session.post(URL, data=json.dumps(data), headers=headers3)

    # 获取邮件中的验证码

    conn = imaplib.IMAP4_SSL(host=r'imap.qq.com', port=993)
    code = conn.login(sender, mail_pass)

    for _ in range(3):
        time.sleep(12)
        conn.select()
        typ, data1 = conn.search(None, '(FROM "portal@nwpu.edu.cn")')
        try:
            typ, data2 = conn.fetch(data1[0].decode().split()[-1], '(RFC822)')
        except IndexError as e:
            continue
        msg = email.message_from_string(data2[0][1].decode('utf-8'))
        IDENTIFY_CODE = 0
        for part in msg.walk():
            if not part.is_multipart():
                CONTENT = part.get_payload(decode=True).decode('utf-8')
                if CONTENT.startswith('您正在进行验证身份'):
                    IDENTIFY_CODE = CONTENT[14:18]
                    conn.store(data1[0].decode().split()
                            [-1], "+FLAGS", "\\Deleted")
                    conn.expunge()
    conn.close()
    conn.logout()

    # 已经得到验证码，提交

    URL = 'https://uis.nwpu.edu.cn/attest/api/guard/secureemail/valid'
    data['code'] = IDENTIFY_CODE
    session.post(URL, data=json.dumps(data), headers=headers3)

    URL = ("https://uis.nwpu.edu.cn/cas/login?service=https%3A%2F%2Fecampus.nwpu.edu.cn"
            "%2F%3Fpath%3Dhttps%3A%2F%2Fecampus.nwpu.edu.cn")
    data = {
        'username': username,
        'password': password,
        'rememberMe': 'true',
        'currentMenu': '1',
        'mfaState': state_code,
        'execution': execution.group(1),
        '_eventId': 'submit',
        'geolocation': '',
        'submit': '稍等片刻……',
    }
    response = session.post(URL, data=data, headers=headers)

# 已经得到授权，保存cookies
cookies = json.dumps(session.cookies.get_dict())
with open('cookies.txt', 'w', encoding='utf-8') as f:
    f.write(cookies)

# 查询成绩
URL = 'https://jwxt.nwpu.edu.cn/student/sso-login'
session.get(URL, headers=headers)
URL = 'https://jwxt.nwpu.edu.cn/student/for-std/grade/sheet'
response = session.get(URL, headers=headers)
online_code = re.search('semester-index/(.*)', response.url).group(1)
response = session.get(
    'https://jwxt.nwpu.edu.cn/student/for-std/grade/sheet/semester-index/'+online_code, headers=headers)
semester = re.findall('<option value="(.+?)"', response.text)
grades = []
for sem in semester:
    URL = 'https://jwxt.nwpu.edu.cn/student/for-std/grade/sheet/info/'+online_code+'?semester='+sem
    response = session.get(URL, headers=headers2)
    response = json.loads(response.text)['semesterId2studentGrades'][sem]
    for course in response:
        name = course['course']['nameZh']
        gaGrade = course['gaGrade']
        GP = str(course['gp'])
        credit = course['course']['credits']
        grades.append(f'{name}, {gaGrade}, {GP}, {credit}')

F_PATH = 'grades.txt'
if os.path.isfile(F_PATH):
    fo = open(F_PATH, "r+", encoding='utf-8')
    grades2 = fo.read().split('\n')
    new_grades = set(grades).symmetric_difference(set(grades2))
    if len(new_grades) != 0:
        response = session.get(
            ('https://jwxt.nwpu.edu.cn/student/for-std/'
             'student-portrait/getMyGpa?studentAssoc='+online_code),
            headers=headers)
        GPA = str(json.loads(response.text)['stdGpaRankDto']['gpa'])
        TITLE = [','.join(x.split(', ')[0:3]) for x in new_grades]
        TITLE = ';'.join(TITLE)
        CONTENT = "科目              成绩   绩点   学分\n" + \
                  "\n".join(new_grades) + \
                  f"\n成绩已更新，概要如上\n新的绩点诞生了：{GPA}\n继续加油~~~"
        email_msg(TITLE, CONTENT)
        fo.close()
        fo = open(F_PATH, "w", encoding='utf-8')
        fo.write('\n'.join(grades))
else:
    fo = open(F_PATH, "w", encoding='utf-8')
    fo.write('\n'.join(grades))
fo.close()
