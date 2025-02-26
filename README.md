# Automation
学生党的自动化脚本，适用于西工大
## Fetures
- 使用邮箱IMAP协议通过MFA验证，从而实现自动模拟登录。
- 登录完毕后自动删除邮箱中的验证码邮件，避免邮件堆积。
- 实现Cookie持久化，减少验证登录次数。
## 部署
首先安装Python依赖：
```bash
pip install -r requirements.txt
```

然后复制配置文件模板：
```bash
cp config.example.py config.py
```

修改`config.py`中的配置信息，如邮箱、翱翔门户等。

目前脚本**暂仅支持qq邮箱**。打开qq邮箱的IMAP协议、获取授权码的步骤如下：  
1. 打开[网页版qq邮箱](https://mail.qq.com)
2. 找到设置-账户-IMAP/SMTP服务，开启服务
3. 点击下方的生成授权码

所有的脚本若要实现定时运行，有以下方法：
1. Windows平台：利用“定时任务计划”实现定时运行，缺点是复杂且不太稳定
2. Linux平台：使用crontab命令实现定时运行，参考我的博客链接：[随笔：利用云服务器+脚本实现自动“健康填报”](https://caveallegory.cn/2022/07/%e9%9a%8f%e7%ac%94%ef%bc%9a%e5%88%a9%e7%94%a8%e4%ba%91%e6%9c%8d%e5%8a%a1%e5%99%a8%e8%84%9a%e6%9c%ac%e5%ae%9e%e7%8e%b0%e8%87%aa%e5%8a%a8%e5%81%a5%e5%ba%b7%e5%a1%ab%e6%8a%a5/)
3. GitHub Actions：克隆本项目，使用GitHub Actions实现定时运行
4. WSL2：在Windows平台上安装WSL2，利用Linux的crontab命令实现定时运行
## 1. GradesMonitorLinux
### 简介
成绩实时监控系统，知成绩快人一步

支持学校：西北工业大学

实现功能：在自己所设定的频率下扫描教务系统的成绩，一旦发现更新，立即发送邮件通知你
### 原理
1. 访问翱翔门户，如有已保存的cookie，则提前加载它们。
如有登录阶段，则输入账号密码。
如有MFA阶段，选择翱翔门户邮箱验证方式，通过IMAP协议得到邮件中的验证码，完成MFA，结束模拟登录并保存cookie。
2. 登录教务系统，搜集成绩信息，并与本地存档相比较（如没有存档则新建）。
如有新成绩，则发送新邮件并更新本地存档。

## 2. NoticeElectricity
宿舍电费低时发送缴费提醒邮件
