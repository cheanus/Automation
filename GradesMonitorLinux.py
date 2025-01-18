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
from config import *

headers = {
    "accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif, "
        "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    ),
    "accept-encoding": "deflate, br",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "referer": "https://ecampus.nwpu.edu.cn/main.html",
    "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/103.0.0.0 Safari/537.36"
    ),
}
headers2 = headers.copy()
headers2["X-Requested-With"] = "XMLHttpRequest"

URL = (
    "https://uis.nwpu.edu.cn/cas/login?service=https%3A%2F%2Fecampus.nwpu.edu.cn"
    "%2F%3Fpath%3Dhttps%3A%2F%2Fecampus.nwpu.edu.cn"
)


def email_msg(title: str, content: str) -> None:
    # 设置email信息
    # 邮件内容设置
    message = MIMEText(content, "plain", "utf-8")
    # 邮件主题'
    message["Subject"] = title
    # 发送方信息
    message["From"] = sender
    # 接受方信息
    message["To"] = receivers[0]

    # 初始化邮箱服务器
    smtp_obj = smtplib.SMTP_SSL(mail_host, 465)
    # 登录到服务器
    smtp_obj.login(mail_user, mail_pass)
    # 发送
    smtp_obj.sendmail(sender, receivers, message.as_string())
    # 退出
    smtp_obj.quit()


def login():
    session = requests.session()
    is_cookies_valid = False  # cookies是否有效

    if os.path.isfile("cookies.json"):
        with open("cookies.json", "r", encoding="utf-8") as f:
            new_cookies = json.load(f)
        session.cookies.update(new_cookies)
        response = session.get(URL, headers=headers)
        response.encoding = "utf-8"
        if len(response.history) > 0:
            is_cookies_valid = True

    if not is_cookies_valid:
        #  在主页开始输入账号
        response = session.get(URL, headers=headers)
        response.encoding = "utf-8"
        str1 = re.search('var hmSiteId = "(.*?)"', response.text)
        new_cookies = {
            ("Hm_lvt_" + str1.group(1)): str(int(time.time())),
            ("Hm_lpvt_" + str1.group(1)): str(int(time.time())),
        }
        session.cookies.update(new_cookies)
        # RSA加密password
        URL_key = "https://uis.nwpu.edu.cn/cas/jwt/publicKey"
        public_key = session.get(URL_key, headers=headers2).text
        public_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key.encode())
        encrypted_password = rsa.encrypt(password.encode(), public_key)
        encrypted_password = "__RSA__" + base64.b64encode(encrypted_password).decode()

        execution = re.search('name="execution" value="(.*?)"', response.text)

        data = {
            "username": username,
            "password": encrypted_password,
        }
        response = session.post(
            "https://uis.nwpu.edu.cn/cas/mfa/detect", data=data, headers=headers2
        )
        state_code = json.loads(response.text)["data"]["state"]

        response = session.get(
            "https://uis.nwpu.edu.cn/cas/mfa/initByType/secureemail?state="
            + state_code,
            headers=headers2,
        )
        gid = json.loads(response.text)["data"]["gid"]

        data = {"gid": gid}
        session.post(
            "https://uis.nwpu.edu.cn/attest/api/guard/secureemail/send",
            json=data,
            headers=headers2,
        )

        # 获取邮件中的验证码

        conn = imaplib.IMAP4_SSL(host=r"imap.qq.com", port=993)
        code = conn.login(sender, mail_pass)

        for _ in range(3):
            time.sleep(12)
            conn.select()
            typ, data1 = conn.search(None, '(FROM "portal@nwpu.edu.cn")')
            try:
                typ, data2 = conn.fetch(data1[0].decode().split()[-1], "(RFC822)")
            except IndexError as e:
                continue
            msg = email.message_from_string(data2[0][1].decode("utf-8"))
            IDENTIFY_CODE = 0
            for part in msg.walk():
                if not part.is_multipart():
                    CONTENT = part.get_payload(decode=True).decode("utf-8")
                    if CONTENT.startswith("您正在进行验证身份"):
                        IDENTIFY_CODE = CONTENT[14:18]
                        conn.store(data1[0].decode().split()[-1], "+FLAGS", "\\Deleted")
                        conn.expunge()
        conn.close()
        conn.logout()

        # 已经得到验证码，提交
        data["code"] = IDENTIFY_CODE
        session.post(
            "https://uis.nwpu.edu.cn/attest/api/guard/secureemail/valid",
            json=data,
            headers=headers2,
        )

        data = {
            "username": username,
            "password": encrypted_password,
            "rememberMe": "true",
            "currentMenu": "1",
            "mfaState": state_code,
            "execution": execution.group(1),
            "_eventId": "submit",
            "geolocation": "",
            "submit": "稍等片刻……",
        }
        response = session.post(
            (
                "https://uis.nwpu.edu.cn/cas/login?service=https%3A%2F%2Fecampus.nwpu.edu.cn"
                "%2F%3Fpath%3Dhttps%3A%2F%2Fecampus.nwpu.edu.cn"
            ),
            data=data,
            headers=headers,
        )

    # 已经得到授权，保存cookies
    cookies = session.cookies.get_dict()
    with open("cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f)

    return session


def find_grades(session):
    # 查询成绩
    session.get("https://jwxt.nwpu.edu.cn/student/sso-login", headers=headers)
    response = session.get(
        "https://jwxt.nwpu.edu.cn/student/for-std/grade/sheet", headers=headers
    )
    online_code = re.search("semester-index/(.*)", response.url).group(1)
    response = session.get(
        "https://jwxt.nwpu.edu.cn/student/for-std/grade/sheet/semester-index/"
        + online_code,
        headers=headers,
    )
    semester = re.findall('<option value="(.+?)"', response.text)
    grades = []
    for sem in semester:
        response = session.get(
            (
                "https://jwxt.nwpu.edu.cn/student/for-std/grade/sheet/info/"
                + online_code
                + "?semester="
                + sem
            ),
            headers=headers2,
        )
        response = json.loads(response.text)["semesterId2studentGrades"][sem]
        for course in response:
            name = course["course"]["nameZh"]
            gaGrade = course["gaGrade"]
            GP = str(course["gp"])
            credit = course["course"]["credits"]
            grades.append(f"{name}, {gaGrade}, {GP}, {credit}")

    F_PATH = "grades.csv"
    if os.path.isfile(F_PATH):
        fo = open(F_PATH, "r+", encoding="utf-8")
        grades2 = fo.read().split("\n")
        new_grades = set(grades).symmetric_difference(set(grades2))
        if len(new_grades) != 0:
            response = session.get(
                (
                    "https://jwxt.nwpu.edu.cn/student/for-std/"
                    "student-portrait/getMyGpa?studentAssoc=" + online_code
                ),
                headers=headers,
            )
            GPA = str(json.loads(response.text)["stdGpaRankDto"]["gpa"])
            TITLE = [",".join(x.split(", ")[0:3]) for x in new_grades]
            TITLE = ";".join(TITLE)
            CONTENT = (
                "科目              成绩   绩点   学分\n"
                + "\n".join(new_grades)
                + f"\n成绩已更新，概要如上\n新的绩点诞生了：{GPA}\n继续加油~~~"
            )
            email_msg(TITLE, CONTENT)
            fo.close()
            fo = open(F_PATH, "w", encoding="utf-8")
            fo.write("\n".join(grades))
    else:
        fo = open(F_PATH, "w", encoding="utf-8")
        fo.write("\n".join(grades))
    fo.close()


def main():
    session = login()
    find_grades(session)


if __name__ == "__main__":
    main()
