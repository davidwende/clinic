# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LoginForm.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QWidget)
import Icons_rc

class Ui_w_LoginForm(object):
    def setupUi(self, w_LoginForm):
        if not w_LoginForm.objectName():
            w_LoginForm.setObjectName(u"w_LoginForm")
        w_LoginForm.resize(521, 276)
        font = QFont()
        font.setPointSize(12)
        w_LoginForm.setFont(font)
        self.gridLayout = QGridLayout(w_LoginForm)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pb_Cancel = QPushButton(w_LoginForm)
        self.pb_Cancel.setObjectName(u"pb_Cancel")
        icon = QIcon()
        icon.addFile(u":/Buttons/delete-button.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pb_Cancel.setIcon(icon)

        self.gridLayout.addWidget(self.pb_Cancel, 1, 1, 1, 1)

        self.groupBox = QGroupBox(w_LoginForm)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setAlignment(Qt.AlignCenter)
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.le_UserName = QLineEdit(self.groupBox)
        self.le_UserName.setObjectName(u"le_UserName")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.le_UserName)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.le_Password = QLineEdit(self.groupBox)
        self.le_Password.setObjectName(u"le_Password")
        self.le_Password.setEchoMode(QLineEdit.Password)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.le_Password)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.formLayout.setItem(2, QFormLayout.SpanningRole, self.verticalSpacer)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)

        self.pb_OK = QPushButton(w_LoginForm)
        self.pb_OK.setObjectName(u"pb_OK")
        icon1 = QIcon()
        icon1.addFile(u":/Buttons/check.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pb_OK.setIcon(icon1)

        self.gridLayout.addWidget(self.pb_OK, 1, 0, 1, 1)

        self.lb_Message = QLabel(w_LoginForm)
        self.lb_Message.setObjectName(u"lb_Message")

        self.gridLayout.addWidget(self.lb_Message, 2, 0, 1, 1)

        QWidget.setTabOrder(self.le_UserName, self.le_Password)
        QWidget.setTabOrder(self.le_Password, self.pb_OK)
        QWidget.setTabOrder(self.pb_OK, self.pb_Cancel)

        self.retranslateUi(w_LoginForm)

        QMetaObject.connectSlotsByName(w_LoginForm)
    # setupUi

    def retranslateUi(self, w_LoginForm):
        w_LoginForm.setWindowTitle(QCoreApplication.translate("w_LoginForm", u"Sample_Application", None))
        self.pb_Cancel.setText(QCoreApplication.translate("w_LoginForm", u"Cancel", None))
        self.groupBox.setTitle(QCoreApplication.translate("w_LoginForm", u"Welcome Please Login", None))
        self.label.setText(QCoreApplication.translate("w_LoginForm", u"User Name", None))
        self.label_2.setText(QCoreApplication.translate("w_LoginForm", u"Password", None))
        self.pb_OK.setText(QCoreApplication.translate("w_LoginForm", u"OK", None))
        self.lb_Message.setText(QCoreApplication.translate("w_LoginForm", u"Message", None))
    # retranslateUi

