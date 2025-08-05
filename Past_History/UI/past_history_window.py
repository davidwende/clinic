# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'past_history_window.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QListView, QPlainTextEdit, QPushButton, QSizePolicy,
    QWidget)

class Ui_w_past_history(object):
    def setupUi(self, w_past_history):
        if not w_past_history.objectName():
            w_past_history.setObjectName(u"w_past_history")
        w_past_history.resize(851, 802)
        self.gridLayout = QGridLayout(w_past_history)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(w_past_history)
        self.groupBox.setObjectName(u"groupBox")
        font = QFont()
        font.setPointSize(12)
        self.groupBox.setFont(font)
        self.groupBox.setAlignment(Qt.AlignCenter)
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.cb_disabilities = QCheckBox(self.groupBox)
        self.cb_disabilities.setObjectName(u"cb_disabilities")

        self.gridLayout_2.addWidget(self.cb_disabilities, 6, 0, 1, 1)

        self.lb_patient = QLabel(self.groupBox)
        self.lb_patient.setObjectName(u"lb_patient")
        self.lb_patient.setFont(font)
        self.lb_patient.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.lb_patient, 0, 0, 1, 3)

        self.le_malignancy_details = QLineEdit(self.groupBox)
        self.le_malignancy_details.setObjectName(u"le_malignancy_details")

        self.gridLayout_2.addWidget(self.le_malignancy_details, 4, 2, 1, 1)

        self.cb_malignancies = QCheckBox(self.groupBox)
        self.cb_malignancies.setObjectName(u"cb_malignancies")

        self.gridLayout_2.addWidget(self.cb_malignancies, 3, 0, 1, 1)

        self.le_blood = QLineEdit(self.groupBox)
        self.le_blood.setObjectName(u"le_blood")

        self.gridLayout_2.addWidget(self.le_blood, 2, 1, 1, 2)

        self.lv_nac = QListView(self.groupBox)
        self.lv_nac.setObjectName(u"lv_nac")

        self.gridLayout_2.addWidget(self.lv_nac, 7, 1, 4, 1)

        self.le_nac = QLineEdit(self.groupBox)
        self.le_nac.setObjectName(u"le_nac")

        self.gridLayout_2.addWidget(self.le_nac, 8, 2, 1, 1)

        self.pb_del_ac = QPushButton(self.groupBox)
        self.pb_del_ac.setObjectName(u"pb_del_ac")

        self.gridLayout_2.addWidget(self.pb_del_ac, 14, 2, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cb_hypertension = QCheckBox(self.groupBox)
        self.cb_hypertension.setObjectName(u"cb_hypertension")

        self.horizontalLayout.addWidget(self.cb_hypertension)

        self.cb_diabetes = QCheckBox(self.groupBox)
        self.cb_diabetes.setObjectName(u"cb_diabetes")

        self.horizontalLayout.addWidget(self.cb_diabetes)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 3)

        self.cb_remission = QCheckBox(self.groupBox)
        self.cb_remission.setObjectName(u"cb_remission")

        self.gridLayout_2.addWidget(self.cb_remission, 5, 1, 1, 1)

        self.pb_add_ac = QPushButton(self.groupBox)
        self.pb_add_ac.setObjectName(u"pb_add_ac")

        self.gridLayout_2.addWidget(self.pb_add_ac, 13, 2, 1, 1)

        self.le_malignancy_date = QLineEdit(self.groupBox)
        self.le_malignancy_date.setObjectName(u"le_malignancy_date")

        self.gridLayout_2.addWidget(self.le_malignancy_date, 3, 2, 1, 1)

        self.le_disabilities = QLineEdit(self.groupBox)
        self.le_disabilities.setObjectName(u"le_disabilities")

        self.gridLayout_2.addWidget(self.le_disabilities, 6, 1, 1, 2)

        self.cb_nac = QComboBox(self.groupBox)
        self.cb_nac.setObjectName(u"cb_nac")

        self.gridLayout_2.addWidget(self.cb_nac, 7, 2, 1, 1)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 16, 0, 1, 1)

        self.le_ac = QLineEdit(self.groupBox)
        self.le_ac.setObjectName(u"le_ac")

        self.gridLayout_2.addWidget(self.le_ac, 12, 2, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 7, 0, 1, 1)

        self.lv_ac = QListView(self.groupBox)
        self.lv_ac.setObjectName(u"lv_ac")

        self.gridLayout_2.addWidget(self.lv_ac, 11, 1, 4, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 15, 0, 1, 1)

        self.cb_blood = QCheckBox(self.groupBox)
        self.cb_blood.setObjectName(u"cb_blood")

        self.gridLayout_2.addWidget(self.cb_blood, 2, 0, 1, 1)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 11, 0, 1, 1)

        self.pb_add_nac = QPushButton(self.groupBox)
        self.pb_add_nac.setObjectName(u"pb_add_nac")

        self.gridLayout_2.addWidget(self.pb_add_nac, 9, 2, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 4, 1, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 3, 1, 1, 1)

        self.pb_del_nac = QPushButton(self.groupBox)
        self.pb_del_nac.setObjectName(u"pb_del_nac")

        self.gridLayout_2.addWidget(self.pb_del_nac, 10, 2, 1, 1)

        self.cb_ac = QComboBox(self.groupBox)
        self.cb_ac.setObjectName(u"cb_ac")

        self.gridLayout_2.addWidget(self.cb_ac, 11, 2, 1, 1)

        self.plt_operations = QPlainTextEdit(self.groupBox)
        self.plt_operations.setObjectName(u"plt_operations")

        self.gridLayout_2.addWidget(self.plt_operations, 15, 1, 1, 2)

        self.plt_trauma = QPlainTextEdit(self.groupBox)
        self.plt_trauma.setObjectName(u"plt_trauma")

        self.gridLayout_2.addWidget(self.plt_trauma, 16, 1, 1, 2)


        self.gridLayout.addWidget(self.groupBox, 0, 1, 1, 2)

        self.pb_save = QPushButton(w_past_history)
        self.pb_save.setObjectName(u"pb_save")

        self.gridLayout.addWidget(self.pb_save, 1, 1, 1, 1)

        self.pb_cancel = QPushButton(w_past_history)
        self.pb_cancel.setObjectName(u"pb_cancel")

        self.gridLayout.addWidget(self.pb_cancel, 1, 2, 1, 1)


        self.retranslateUi(w_past_history)

        QMetaObject.connectSlotsByName(w_past_history)
    # setupUi

    def retranslateUi(self, w_past_history):
        w_past_history.setWindowTitle(QCoreApplication.translate("w_past_history", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("w_past_history", u"Past History", None))
        self.cb_disabilities.setText(QCoreApplication.translate("w_past_history", u"Disabilities", None))
        self.lb_patient.setText(QCoreApplication.translate("w_past_history", u"TextLabel", None))
        self.cb_malignancies.setText(QCoreApplication.translate("w_past_history", u"Malignancies", None))
        self.pb_del_ac.setText(QCoreApplication.translate("w_past_history", u"Delete AC Medication", None))
        self.cb_hypertension.setText(QCoreApplication.translate("w_past_history", u"Hypertension", None))
        self.cb_diabetes.setText(QCoreApplication.translate("w_past_history", u"Diabetes", None))
        self.cb_remission.setText(QCoreApplication.translate("w_past_history", u"Malignancy in Remission?", None))
        self.pb_add_ac.setText(QCoreApplication.translate("w_past_history", u"Add AC Medication", None))
        self.label_5.setText(QCoreApplication.translate("w_past_history", u"Trauma/Other", None))
        self.label_3.setText(QCoreApplication.translate("w_past_history", u"Medications NAC", None))
        self.label_4.setText(QCoreApplication.translate("w_past_history", u"Operations", None))
        self.cb_blood.setText(QCoreApplication.translate("w_past_history", u"Blood Disorders", None))
        self.label_6.setText(QCoreApplication.translate("w_past_history", u"Medications AC", None))
        self.pb_add_nac.setText(QCoreApplication.translate("w_past_history", u"Add NAC Medication", None))
        self.label_2.setText(QCoreApplication.translate("w_past_history", u"Details", None))
        self.label.setText(QCoreApplication.translate("w_past_history", u"Year of Onset", None))
        self.pb_del_nac.setText(QCoreApplication.translate("w_past_history", u"Delete NAC Medication", None))
        self.pb_save.setText(QCoreApplication.translate("w_past_history", u"Save", None))
        self.pb_cancel.setText(QCoreApplication.translate("w_past_history", u"Cancel", None))
    # retranslateUi

