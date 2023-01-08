from json import dumps, loads
from os import system
from os.path import isfile
from PyQt5 import QtWidgets, QtGui
import sys
import main_win
import policy
from cryptocode import encrypt, decrypt
import Auto_Fill
import datetime


class FirstWindow(QtWidgets.QWidget, main_win.Ui_Form):

    def __init__(self):
        super(FirstWindow, self).__init__()
        self.setupUi(self)
        self.save_button.clicked.connect(self.account_save)
        self.check_button.clicked.connect(self.checkout)
        self.auto_on.clicked.connect(self.plan_on)
        self.auto_off.clicked.connect(self.plan_off)
        self.policy_button.clicked.connect(self.policy_win)
        self.resize(900, 700)
        self.show()
        self.policyWindow = PolicyWindow()
        with open('appdata.txt', 'r') as file:
            is_accepted = loads(file.read())['is_accepted']
        if not is_accepted:
            self.policyWindow.show()
            self.save_button.setEnabled(False)
            self.check_button.setEnabled(False)
            self.auto_on.setEnabled(False)
            self.auto_off.setEnabled(False)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.policyWindow.close()
        super(FirstWindow, self).closeEvent(a0)

    def account_save(self):
        account = self.account_lineEdit.text()
        password = self.password_lineEdit.text()
        if account == '' or password == '':
            self.account_reminder.setText('空字符')
            return
        with open('appdata.txt', 'r+') as file:
            str_encode = encrypt(account + '\n' + password, 'oa8f782hfu8h2c70710ch0uhuacsagowq8')
            appdata = loads(file.read())
            appdata['account'] = str_encode
        with open('appdata.txt', 'w') as file:
            file.write(dumps(appdata))
            self.account_reminder.setText('已保存')

    def checkout(self):
        with open('appdata.txt', 'r') as file:
            appdata = loads(file.read())
        if appdata['account'] == '':
            self.account_reminder.setText('本地无账号信息')
            return
        account, password = decrypt(appdata['account'], 'oa8f782hfu8h2c70710ch0uhuacsagowq8').split('\n')
        code = Auto_Fill.auto_fill(account, password)
        if code is None:
            with open('appdata.txt', 'w') as file:
                appdata['done_date'] = datetime.datetime.now().day
                file.write(dumps(appdata))
            self.account_reminder.setText('填报成功')
        elif code == -1:
            self.account_reminder.setText('网络错误')
        elif code == -2:
            self.account_reminder.setText('填报失败')

    def plan_on(self):
        with open('auto_cmd.bat', 'w') as file:
            file.write('cd /d ' + sys.argv[0] + "/../\n" + sys.argv[0] + ' -e')
        with open('automation.vbs', 'w') as file:
            file.write('set ws=WScript.CreateObject("WScript.Shell")\n'
                       'ws.Run "' + sys.argv[0] + '/../auto_cmd.bat",0')
        system('schtasks /create /tn "AutoFill" /tr ' + sys.argv[0] + r'/../automation.vbs /sc minute /mo 30 /f')
        self.account_reminder.setText('已设置定时任务')

    def plan_off(self):
        system('schtasks /delete /tn "AutoFill" /f')
        self.account_reminder.setText('已删除定时任务')

    def policy_win(self):
        self.policyWindow.show()


class PolicyWindow(QtWidgets.QWidget, policy.Ui_Form):

    def __init__(self):
        super(PolicyWindow, self).__init__()
        self.setupUi(self)
        self.accept_box.clicked.connect(self.change_allow)
        self.resize(800, 600)

    def show(self) -> None:
        super(PolicyWindow, self).show()
        with open('appdata.txt', 'r') as file:
            appdata = loads(file.read())
        self.accept_box.setChecked(appdata['is_accepted'])

    def change_allow(self):
        with open('appdata.txt', 'r') as file:
            appdata = loads(file.read())
        appdata['is_accepted'] = self.accept_box.isChecked()
        with open('appdata.txt', 'w') as file:
            file.write(dumps(appdata))
        if self.accept_box.isChecked():
            firstWindow.save_button.setEnabled(True)
            firstWindow.check_button.setEnabled(True)
            firstWindow.auto_on.setEnabled(True)
            firstWindow.auto_off.setEnabled(True)
        else:
            firstWindow.save_button.setEnabled(False)
            firstWindow.check_button.setEnabled(False)
            firstWindow.auto_on.setEnabled(False)
            firstWindow.auto_off.setEnabled(False)


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '-e':
        with open('appdata.txt', 'r') as file:
            appdata = loads(file.read())
        if appdata['account'] == '' or appdata['done_date'] == datetime.datetime.now().day \
                or datetime.datetime.now().hour <= 2:
            sys.exit()
        account, password = decrypt(appdata['account'], 'oa8f782hfu8h2c70710ch0uhuacsagowq8').split('\n')
        code = Auto_Fill.auto_fill(account, password)
        if code is None:
            with open('appdata.txt', 'w') as file:
                appdata['done_date'] = datetime.datetime.now().day
                file.write(dumps(appdata))
        sys.exit()

    if not isfile('appdata.txt'):
        with open('appdata.txt', 'w') as file:
            appdata = dumps({'account': '', 'is_accepted': False, 'done_date': 0})
            file.write(appdata)

    app = QtWidgets.QApplication(sys.argv)
    firstWindow = FirstWindow()
    sys.exit(app.exec())
