import re
import json
import smtplib
import requests
from email.mime.text import MIMEText

## 部署个人信息
# 设置服务器所需信息
# qq邮箱服务器地址
mail_host = 'smtp.qq.com'
# qq用户名
mail_user = '***********'
# 密码(部分邮箱为授权码)
mail_pass = '****************'
# 邮件发送方邮箱地址
sender = '***@qq.com'
# 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
receivers = ['***@qq.com']
## 宿舍房间信息，参照APP-电费里的文字填写
# 校区
campus = '长安校区'
# 楼栋
building = '云天苑C座右'
# 房间
room = '云天苑C座右-1-128'
# 剩余电量提醒阈值
threshold = 20.0

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

URL = 'https://yktapp.nwpu.edu.cn/jfdt/charge/feeitem/getThirdData'
headers = {
    'Host': 'yktapp.nwpu.edu.cn',
    'Connection': 'keep-alive',
    'Content-Length': '102',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; ANG-AN00 Build/HUAWEIANG-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.105 Mobile Safari/537.36 SuperApp',
    'Origin': 'https://yktapp.nwpu.edu.cn',
    'X-Requested-With': 'com.lantu.MobileCampus.nwpu',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

# 查找宿舍对应代码
campus_code = '22' if campus == '长安校区' else '1'
data = {
    'type': 'select',
    'level': '1',
    'campus': campus_code,
    'feeitemid': '182'
}
response = requests.post(URL, data=data, headers=headers)
building_code = -1
for building_item in json.loads(response.text)['map']['data']:
    if building_item['name'] == building:
        building_code = building_item['value']
        break
data = {
    'type': 'select',
    'level': '2',
    'campus': campus_code,
    'building': building_code,
    'feeitemid': '182'
}
response = requests.post(URL, data=data, headers=headers)
room_code = -1
for room_item in json.loads(response.text)['map']['data']:
    if room_item['name'] == room:
        room_code = room_item['value']
        break
if building_code == -1 or room_code == -1:
    raise ValueError('未找到对应房间')

data = {
    'type': 'IEC',
    'level': '3',
    'campus': campus_code,
    'building': building_code,
    'room': room_code,
    'feeitemid': '182'
}
response = requests.post(URL, data=data, headers=headers)
remain = re.search(r'当前剩余电量\\":\\"(.*?)\\', response.text).groups()[0]
# print('当前电费为：'+remain)
if float(remain) < threshold:
    email_msg('宿舍电费提醒', '当前电费为：'+remain+'，请尽快缴费')
