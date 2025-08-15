# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_form.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDateEdit, QFormLayout,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QListView, QMainWindow,
    QMenu, QMenuBar, QPushButton, QRadioButton,
    QSizePolicy, QStatusBar, QVBoxLayout, QWidget)

class Ui_w_MainWindow(object):
    def setupUi(self, w_MainWindow):
        if not w_MainWindow.objectName():
            w_MainWindow.setObjectName(u"w_MainWindow")
        w_MainWindow.resize(965, 530)
        self.actionQuit = QAction(w_MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        self.actionSomething = QAction(w_MainWindow)
        self.actionSomething.setObjectName(u"actionSomething")
        self.actionVisit_Summary = QAction(w_MainWindow)
        self.actionVisit_Summary.setObjectName(u"actionVisit_Summary")
        self.actionSomething_Else = QAction(w_MainWindow)
        self.actionSomething_Else.setObjectName(u"actionSomething_Else")
        self.centralwidget = QWidget(w_MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pb_PastHistory = QPushButton(self.centralwidget)
        self.pb_PastHistory.setObjectName(u"pb_PastHistory")
        self.pb_PastHistory.setMinimumSize(QSize(0, 30))

        self.gridLayout.addWidget(self.pb_PastHistory, 3, 0, 1, 1)

        self.pb_blood = QPushButton(self.centralwidget)
        self.pb_blood.setObjectName(u"pb_blood")
        self.pb_blood.setMinimumSize(QSize(0, 30))

        self.gridLayout.addWidget(self.pb_blood, 3, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lv_patients = QListView(self.groupBox)
        self.lv_patients.setObjectName(u"lv_patients")
        font = QFont()
        font.setFamilies([u"Monospace"])
        self.lv_patients.setFont(font)

        self.verticalLayout.addWidget(self.lv_patients)

        self.pb_refresh = QPushButton(self.groupBox)
        self.pb_refresh.setObjectName(u"pb_refresh")

        self.verticalLayout.addWidget(self.pb_refresh)

        self.groupBox_3 = QGroupBox(self.groupBox)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.lb_total_pat = QLabel(self.groupBox_3)
        self.lb_total_pat.setObjectName(u"lb_total_pat")
        self.lb_total_pat.setGeometry(QRect(3, 0, 111, 20))
        self.le_total_pat = QLineEdit(self.groupBox_3)
        self.le_total_pat.setObjectName(u"le_total_pat")
        self.le_total_pat.setGeometry(QRect(130, 0, 113, 25))
        self.lb_total_visits = QLabel(self.groupBox_3)
        self.lb_total_visits.setObjectName(u"lb_total_visits")
        self.lb_total_visits.setGeometry(QRect(250, 0, 111, 20))
        self.le_total_visits = QLineEdit(self.groupBox_3)
        self.le_total_visits.setObjectName(u"le_total_visits")
        self.le_total_visits.setGeometry(QRect(370, 0, 113, 25))

        self.groupBox_5 = QGroupBox(self.groupBox)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.lb_total_procedures = QLabel(self.groupBox_5)
        self.lb_total_procedures.setObjectName(u"lb_total_procedures")
        self.lb_total_procedures.setGeometry(QRect(3, 0, 111, 20))
        self.le_total_procedures = QLineEdit(self.groupBox_5)
        self.le_total_procedures.setObjectName(u"le_total_procedures")
        self.le_total_procedures.setGeometry(QRect(130, 0, 113, 25))

        self.groupBox_4 = QGroupBox(self.groupBox)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.lb_from_date = QLabel(self.groupBox_4)
        self.lb_from_date.setObjectName(u"lb_from_date")
        self.lb_from_date.setGeometry(QRect(20, 0, 71, 20))
        self.de_from_date = QDateEdit(self.groupBox_4)
        self.de_from_date.setObjectName(u"de_from_date")
        self.de_from_date.setGeometry(QRect(90, 0, 110, 25))
        self.de_from_date.setCalendarPopup(True)
        self.de_from_date.setDate(QDate(2024, 1, 1))
        self.de_from_date.setDisplayFormat("dd/MM/yyyy")
        self.lb_to_date = QLabel(self.groupBox_4)
        self.lb_to_date.setObjectName(u"lb_to_date")
        self.lb_to_date.setGeometry(QRect(250, 0, 71, 20))
        self.de_to_date = QDateEdit(self.groupBox_4)
        self.de_to_date.setObjectName(u"de_to_date")
        self.de_to_date.setGeometry(QRect(320, 0, 110, 25))
        self.de_to_date.setCalendarPopup(True)
        self.de_to_date.setDate(QDate.currentDate())
        self.de_to_date.setDisplayFormat("dd/MM/yyyy")

        self.verticalLayout.addWidget(self.groupBox_4)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.verticalLayout.addWidget(self.groupBox_5)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.le_search = QLineEdit(self.groupBox)
        self.le_search.setObjectName(u"le_search")
        self.le_search.setMaxLength(6)

        self.verticalLayout.addWidget(self.le_search)


        self.horizontalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout = QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName(u"formLayout")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_3)

        self.le_surname = QLineEdit(self.groupBox_2)
        self.le_surname.setObjectName(u"le_surname")
        self.le_surname.setMaxLength(20)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.le_surname)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.le_fname = QLineEdit(self.groupBox_2)
        self.le_fname.setObjectName(u"le_fname")
        self.le_fname.setMaxLength(20)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.le_fname)

        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_5)

        self.le_id = QLineEdit(self.groupBox_2)
        self.le_id.setObjectName(u"le_id")
        self.le_id.setMaxLength(9)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.le_id)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_7)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.rb_male = QRadioButton(self.groupBox_2)
        self.rb_male.setObjectName(u"rb_male")

        self.horizontalLayout_2.addWidget(self.rb_male)

        self.rb_female = QRadioButton(self.groupBox_2)
        self.rb_female.setObjectName(u"rb_female")

        self.horizontalLayout_2.addWidget(self.rb_female)


        self.formLayout.setLayout(4, QFormLayout.FieldRole, self.horizontalLayout_2)

        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_6)

        self.le_dob = QDateEdit(self.groupBox_2)
        self.le_dob.setObjectName(u"le_dob")
        self.le_dob.setCalendarPopup(True)

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.le_dob)

        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.label_8)

        self.le_email = QLineEdit(self.groupBox_2)
        self.le_email.setObjectName(u"le_email")
        self.le_email.setMaxLength(30)

        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.le_email)

        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(10, QFormLayout.LabelRole, self.label_9)

        self.le_phone = QLineEdit(self.groupBox_2)
        self.le_phone.setObjectName(u"le_phone")
        self.le_phone.setMaxLength(12)

        self.formLayout.setWidget(10, QFormLayout.FieldRole, self.le_phone)

        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName(u"label_10")

        self.formLayout.setWidget(12, QFormLayout.LabelRole, self.label_10)

        self.cb_smoker = QCheckBox(self.groupBox_2)
        self.cb_smoker.setObjectName(u"cb_smoker")

        self.formLayout.setWidget(12, QFormLayout.FieldRole, self.cb_smoker)

        self.pb_clear = QPushButton(self.groupBox_2)
        self.pb_clear.setObjectName(u"pb_clear")

        self.formLayout.setWidget(15, QFormLayout.SpanningRole, self.pb_clear)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pb_save_new = QPushButton(self.groupBox_2)
        self.pb_save_new.setObjectName(u"pb_save_new")

        self.horizontalLayout_3.addWidget(self.pb_save_new)

        self.pb_modify = QPushButton(self.groupBox_2)
        self.pb_modify.setObjectName(u"pb_modify")

        self.horizontalLayout_3.addWidget(self.pb_modify)

        self.pb_delete = QPushButton(self.groupBox_2)
        self.pb_delete.setObjectName(u"pb_delete")

        self.horizontalLayout_3.addWidget(self.pb_delete)


        self.formLayout.setLayout(16, QFormLayout.SpanningRole, self.horizontalLayout_3)

        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(13, QFormLayout.LabelRole, self.label)

        self.cb_consent = QCheckBox(self.groupBox_2)
        self.cb_consent.setObjectName(u"cb_consent")

        self.formLayout.setWidget(13, QFormLayout.FieldRole, self.cb_consent)


        self.horizontalLayout.addWidget(self.groupBox_2)


        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 3)

        self.lb_Patient = QLabel(self.centralwidget)
        self.lb_Patient.setObjectName(u"lb_Patient")

        self.gridLayout.addWidget(self.lb_Patient, 0, 0, 1, 1)

        self.pb_Visits = QPushButton(self.centralwidget)
        self.pb_Visits.setObjectName(u"pb_Visits")
        self.pb_Visits.setMinimumSize(QSize(0, 30))

        self.gridLayout.addWidget(self.pb_Visits, 3, 2, 1, 1)

        w_MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(w_MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 965, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuForms = QMenu(self.menubar)
        self.menuForms.setObjectName(u"menuForms")
        self.menuPrint = QMenu(self.menubar)
        self.menuPrint.setObjectName(u"menuPrint")
        w_MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(w_MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        w_MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuForms.menuAction())
        self.menubar.addAction(self.menuPrint.menuAction())
        self.menuFile.addAction(self.actionQuit)
        self.menuForms.addAction(self.actionSomething)
        self.menuPrint.addAction(self.actionVisit_Summary)
        self.menuPrint.addAction(self.actionSomething_Else)

        self.retranslateUi(w_MainWindow)

        QMetaObject.connectSlotsByName(w_MainWindow)
    # setupUi

    def retranslateUi(self, w_MainWindow):
        w_MainWindow.setWindowTitle(QCoreApplication.translate("w_MainWindow", u"MainWindow", None))
        self.actionQuit.setText(QCoreApplication.translate("w_MainWindow", u"Quit", None))
        self.actionSomething.setText(QCoreApplication.translate("w_MainWindow", u"Something", None))
        self.actionVisit_Summary.setText(QCoreApplication.translate("w_MainWindow", u"Visit Summary", None))
        self.actionSomething_Else.setText(QCoreApplication.translate("w_MainWindow", u"Something Else", None))
        self.pb_PastHistory.setText(QCoreApplication.translate("w_MainWindow", u"Past History", None))
        self.pb_blood.setText(QCoreApplication.translate("w_MainWindow", u"Blood Pressure / Pulse", None))
        self.groupBox.setTitle(QCoreApplication.translate("w_MainWindow", u"Choose Existing Patient", None))
        self.pb_refresh.setText(QCoreApplication.translate("w_MainWindow", u"Refresh", None))
        self.groupBox_3.setTitle("")
        self.lb_total_pat.setText(QCoreApplication.translate("w_MainWindow", u"Total # Patients", None))
        self.lb_total_visits.setText(QCoreApplication.translate("w_MainWindow", u"Total # Visits", None))
        self.lb_total_procedures.setText(QCoreApplication.translate("w_MainWindow", u"Total # Procedures", None))
        self.lb_from_date.setText(QCoreApplication.translate("w_MainWindow", u"From Date:", None))
        self.lb_to_date.setText(QCoreApplication.translate("w_MainWindow", u"To Date:", None))
        self.label_2.setText(QCoreApplication.translate("w_MainWindow", u"Search by:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("w_MainWindow", u"Patient Details", None))
        self.label_3.setText(QCoreApplication.translate("w_MainWindow", u"Surname", None))
        self.label_4.setText(QCoreApplication.translate("w_MainWindow", u"First Name", None))
        self.label_5.setText(QCoreApplication.translate("w_MainWindow", u"TZ (ID)", None))
        self.le_id.setInputMask(QCoreApplication.translate("w_MainWindow", u"999999999", None))
        self.label_7.setText(QCoreApplication.translate("w_MainWindow", u"Sex", None))
        self.rb_male.setText(QCoreApplication.translate("w_MainWindow", u"Male", None))
        self.rb_female.setText(QCoreApplication.translate("w_MainWindow", u"Female", None))
        self.label_6.setText(QCoreApplication.translate("w_MainWindow", u"Date of Birth", None))
        self.label_8.setText(QCoreApplication.translate("w_MainWindow", u"Email", None))
        self.label_9.setText(QCoreApplication.translate("w_MainWindow", u"Phone", None))
        self.le_phone.setInputMask(QCoreApplication.translate("w_MainWindow", u"000-000-0000", None))
        self.label_10.setText(QCoreApplication.translate("w_MainWindow", u"Smoker", None))
        self.cb_smoker.setText("")
        self.pb_clear.setText(QCoreApplication.translate("w_MainWindow", u"Clear", None))
        self.pb_save_new.setText(QCoreApplication.translate("w_MainWindow", u"Save as new Patient", None))
        self.pb_modify.setText(QCoreApplication.translate("w_MainWindow", u"Modify Patient Data", None))
        self.pb_delete.setText(QCoreApplication.translate("w_MainWindow", u"Delete Patient", None))
        self.label.setText(QCoreApplication.translate("w_MainWindow", u"Consent Signed", None))
        self.cb_consent.setText("")
        self.lb_Patient.setText(QCoreApplication.translate("w_MainWindow", u"Current Patient:", None))
        self.pb_Visits.setText(QCoreApplication.translate("w_MainWindow", u"Visits", None))
        self.menuFile.setTitle(QCoreApplication.translate("w_MainWindow", u"File", None))
        self.menuForms.setTitle(QCoreApplication.translate("w_MainWindow", u"Forms", None))
        self.menuPrint.setTitle(QCoreApplication.translate("w_MainWindow", u"Print", None))
    # retranslateUi

