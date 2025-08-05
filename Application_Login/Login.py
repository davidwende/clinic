import sys
from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw
from PySide6 import QtGui as qtg
from Config.config import users
import hashlib
from Application_Login.UI.LoginForm import Ui_w_LoginForm

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_user(username, password):
    if username in users:
        return users[username] == hash_password(password)
    return False


class LoginForm(qtw.QWidget, Ui_w_LoginForm):
    login_success = qtc.Signal()
    login_admin = qtc.Signal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pb_Cancel.clicked.connect(self.close)
        self.pb_OK.clicked.connect(self.process_login)
        self.le_Password.returnPressed.connect(self.process_login)

    @qtc.Slot()
    def process_login(self):
        if verify_user(self.le_UserName.text(), self.le_Password.text()):
            self.login_success.emit()
            if self.le_UserName.text() == "david":
                self.login_admin.emit()
            self.close()
        else:
            self.le_UserName.setText('')
            self.le_Password.setText('')
            self.lb_Message.setText("Login Incorrect")

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    window = LoginForm()
    window.show()

    sys.exit(app.exec())