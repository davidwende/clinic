# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'reports.ui'
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
    QLabel, QLineEdit, QPlainTextEdit, QPushButton,
    QSizePolicy, QWidget)

class Ui_w_PatientData(object):
    def setupUi(self, w_PatientData):
        if not w_PatientData.objectName():
            w_PatientData.setObjectName(u"w_PatientData")
        w_PatientData.resize(478, 400)
        self.gridLayout = QGridLayout(w_PatientData)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pb_Cancel = QPushButton(w_PatientData)
        self.pb_Cancel.setObjectName(u"pb_Cancel")

        self.gridLayout.addWidget(self.pb_Cancel, 1, 1, 1, 1)

        self.pb_Generate = QPushButton(w_PatientData)
        self.pb_Generate.setObjectName(u"pb_Generate")

        self.gridLayout.addWidget(self.pb_Generate, 1, 0, 1, 1)

        self.groupBox = QGroupBox(w_PatientData)
        self.groupBox.setObjectName(u"groupBox")
        font = QFont()
        font.setPointSize(12)
        self.groupBox.setFont(font)
        self.groupBox.setAlignment(Qt.AlignCenter)
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.lb_tz = QLabel(self.groupBox)
        self.lb_tz.setObjectName(u"lb_tz")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.lb_tz)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_3)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_4)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_7)

        self.lb_fname = QLabel(self.groupBox)
        self.lb_fname.setObjectName(u"lb_fname")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.lb_fname)

        self.lb_surname = QLabel(self.groupBox)
        self.lb_surname.setObjectName(u"lb_surname")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.lb_surname)

        self.lb_visit_date = QLabel(self.groupBox)
        self.lb_visit_date.setObjectName(u"lb_visit_date")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.lb_visit_date)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label)

        self.le_addressee = QLineEdit(self.groupBox)
        self.le_addressee.setObjectName(u"le_addressee")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.le_addressee)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label_5)

        self.te_info = QPlainTextEdit(self.groupBox)
        self.te_info.setObjectName(u"te_info")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.te_info)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)


        self.retranslateUi(w_PatientData)

        QMetaObject.connectSlotsByName(w_PatientData)
    # setupUi

    def retranslateUi(self, w_PatientData):
        w_PatientData.setWindowTitle(QCoreApplication.translate("w_PatientData", u"Form", None))
        self.pb_Cancel.setText(QCoreApplication.translate("w_PatientData", u"Cancel", None))
        self.pb_Generate.setText(QCoreApplication.translate("w_PatientData", u"Generate", None))
        self.groupBox.setTitle(QCoreApplication.translate("w_PatientData", u"Generate Summary", None))
        self.label_2.setText(QCoreApplication.translate("w_PatientData", u"ID Number", None))
        self.lb_tz.setText("")
        self.label_3.setText(QCoreApplication.translate("w_PatientData", u"First Name", None))
        self.label_4.setText(QCoreApplication.translate("w_PatientData", u"Surname", None))
        self.label_7.setText(QCoreApplication.translate("w_PatientData", u"Visit Date", None))
        self.lb_fname.setText("")
        self.lb_surname.setText("")
        self.lb_visit_date.setText("")
        self.label.setText(QCoreApplication.translate("w_PatientData", u"Addressee", None))
        self.label_5.setText(QCoreApplication.translate("w_PatientData", u"More Info", None))
    # retranslateUi

