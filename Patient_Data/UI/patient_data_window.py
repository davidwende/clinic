# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'patient_data_window.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QFormLayout,
    QGridLayout, QGroupBox, QLabel, QLineEdit,
    QPushButton, QRadioButton, QSizePolicy, QWidget)

class Ui_w_PatientData(object):
    def setupUi(self, w_PatientData):
        if not w_PatientData.objectName():
            w_PatientData.setObjectName(u"w_PatientData")
        w_PatientData.resize(407, 303)
        self.gridLayout = QGridLayout(w_PatientData)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pb_Cancel = QPushButton(w_PatientData)
        self.pb_Cancel.setObjectName(u"pb_Cancel")

        self.gridLayout.addWidget(self.pb_Cancel, 1, 1, 1, 1)

        self.pb_Save = QPushButton(w_PatientData)
        self.pb_Save.setObjectName(u"pb_Save")

        self.gridLayout.addWidget(self.pb_Save, 1, 0, 1, 1)

        self.groupBox = QGroupBox(w_PatientData)
        self.groupBox.setObjectName(u"groupBox")
        font = QFont()
        font.setPointSize(12)
        self.groupBox.setFont(font)
        self.groupBox.setAlignment(Qt.AlignCenter)
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.le_FirstName = QLineEdit(self.groupBox)
        self.le_FirstName.setObjectName(u"le_FirstName")

        self.gridLayout_2.addWidget(self.le_FirstName, 1, 2, 1, 1)

        self.cb_Referred = QComboBox(self.groupBox)
        self.cb_Referred.setObjectName(u"cb_Referred")

        self.gridLayout_2.addWidget(self.cb_Referred, 5, 2, 1, 1)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 3, 0, 1, 1)

        self.le_ID = QLineEdit(self.groupBox)
        self.le_ID.setObjectName(u"le_ID")

        self.gridLayout_2.addWidget(self.le_ID, 0, 2, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout_2 = QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.rb_Male = QRadioButton(self.groupBox_2)
        self.rb_Male.setObjectName(u"rb_Male")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.rb_Male)

        self.rb_Female = QRadioButton(self.groupBox_2)
        self.rb_Female.setObjectName(u"rb_Female")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.rb_Female)


        self.gridLayout_2.addWidget(self.groupBox_2, 4, 2, 1, 1)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_2.addWidget(self.label_7, 5, 0, 1, 1)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 4, 0, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 2, 0, 1, 1)

        self.de_dateEdit = QDateEdit(self.groupBox)
        self.de_dateEdit.setObjectName(u"de_dateEdit")
        self.de_dateEdit.setLocale(QLocale(QLocale.English, QLocale.Australia))

        self.gridLayout_2.addWidget(self.de_dateEdit, 3, 1, 1, 2)

        self.le_Surname = QLineEdit(self.groupBox)
        self.le_Surname.setObjectName(u"le_Surname")

        self.gridLayout_2.addWidget(self.le_Surname, 2, 2, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)


        self.retranslateUi(w_PatientData)

        QMetaObject.connectSlotsByName(w_PatientData)
    # setupUi

    def retranslateUi(self, w_PatientData):
        w_PatientData.setWindowTitle(QCoreApplication.translate("w_PatientData", u"Form", None))
        self.pb_Cancel.setText(QCoreApplication.translate("w_PatientData", u"Cancel", None))
        self.pb_Save.setText(QCoreApplication.translate("w_PatientData", u"Save", None))
        self.groupBox.setTitle(QCoreApplication.translate("w_PatientData", u"Patient Data", None))
        self.label_6.setText(QCoreApplication.translate("w_PatientData", u"DoB", None))
        self.label_3.setText(QCoreApplication.translate("w_PatientData", u"First Name", None))
        self.label_2.setText(QCoreApplication.translate("w_PatientData", u"ID Number", None))
        self.groupBox_2.setTitle("")
        self.rb_Male.setText(QCoreApplication.translate("w_PatientData", u"Male", None))
        self.rb_Female.setText(QCoreApplication.translate("w_PatientData", u"Female", None))
        self.label_7.setText(QCoreApplication.translate("w_PatientData", u"Referred", None))
        self.label_5.setText(QCoreApplication.translate("w_PatientData", u"Sex", None))
        self.label_4.setText(QCoreApplication.translate("w_PatientData", u"Surname", None))
    # retranslateUi

