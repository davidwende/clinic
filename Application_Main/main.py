import datetime
import sys
import os
sys.path.append(os.path.abspath('../Database'))

from pyisemail import is_email
# from email_validaor import validate_email, EmailNotValidError

from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from PySide6.QtCore import QSortFilterProxyModel
from PySide6 import QtGui as qtg
from Database.dbFuncs import get_all_patients, get_patient_by_id,\
    patient_exists, save_new_patient, modify_patient, num_visits, delete_patient,\
    visits_between_dates, visits_with_procedures_between_dates

from Application_Main.UI.uiMainForm import UI_MainWindow

from Application_Login.Login import LoginForm
# from Persons.add_person import AddPerson

from Past_History.PastHistory import PastHistoryForm
from Visits.visits import  VisitForm
from Blood.blood import  BloodForm

import string
import error_codes
import re

# email_pattern = re.compile("^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
pattern = r'^[\w\.-]+@[a-zA-Z\d-]+\.[a-zA-Z]{2,}$'

font = qtg.QFont()
font.setStyleHint(qtg.QFont.TypeWriter)
font.setPointSize(10)
font.setFamily('DejaVue Sans')
# font.setFamily('monospace')
class ListViewModel(qtc.QAbstractListModel):
    def __init__(self, the_list = None):
        super().__init__()
        self.the_list = the_list or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            status, text = self.the_list[index.row()]
            return text

    def rowCount(self, index=qtc.QModelIndex()):
        return len(self.the_list)

    def clear(self):
        self.the_list.clear()

class MainWindow(qtw.QMainWindow, UI_MainWindow):
# Use the generated `Ui_w_MainWindow` which correctly parents widgets

    def __init__(self):
        super().__init__()

        self.setupUi(self)
        #self.de_dob.setDisplayFormat("dd/MM/yyyy")


        # self.action_Quit.triggered.connect(self.close)
        # self.action_Add_Person.triggered.connect(self.open_add_person)
        self.visits_form = None
        self.mode = None
        self.tz = None
        self.fname = None
        self.surname = None
        self.form = LoginForm()
        self.form.login_success.connect(self.show)
        self.form.login_admin.connect(self.admin_mode)
        self.form.show()

        # List Models
        self.lv_model = ListViewModel(the_list = [])
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(0)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setSourceModel(self.lv_model)
        self.lv_patients.setModel(self.proxy_model)
        self.lv_patients.setUniformItemSizes(True)
        # self.lv_patients.setAlternatingRowColors(True)

        self.le_search.setPlaceholderText('Enter search string')

        self.search_timer = qtc.QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(200)  # ms delay
        self.le_search.textChanged.connect(lambda text: self.search_timer.start())
        self.search_timer.timeout.connect(lambda: self.proxy_model.setFilterFixedString(self.le_search.text()))

        # self.le_search.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.bn_history.clicked.connect(self.show_past_history)
        self.bn_visits.clicked.connect(self.show_visits)

        self.lv_patients.selectionModel().selectionChanged.connect(self.show_patient_details)
        self.bn_save.clicked.connect(lambda : self.save_new_patient(True))
        self.bn_modify.clicked.connect(lambda : self.save_new_patient(False))
        self.bn_clear.clicked.connect(self.clear_data)
        self.bn_delete.clicked.connect(self.delete_patient)
        # self.pb_Summary.clicked.connect(self.summary)
        self.bn_refresh.clicked.connect(self.populate_patients)
        self.bn_blood.clicked.connect(self.show_blood)

        button_style = ("""
            QPushButton {
                background-color: lightgray;
                border: 2px solid gray;
                border-radius: 10px;
                color: black;
            }
            QPushButton:hover {
                background-color: lightgreen;
                color: black;
            }
        """)
        self.bn_save.setStyleSheet(button_style)
        self.bn_modify.setStyleSheet(button_style)
        self.bn_clear.setStyleSheet(button_style)
        self.bn_delete.setStyleSheet(button_style)
        self.bn_refresh.setStyleSheet(button_style)
        self.bn_blood.setStyleSheet(button_style)
        self.bn_visits.setStyleSheet(button_style)
        self.bn_history.setStyleSheet(button_style)
        #self.lb_Patient.setStyleSheet("border :2px solid black;")

        self.populate_patients()

    def admin_mode(self):
        self.mode = "admin"
        print("entered admin mode")

    def show_blood(self):
        if self.tz:
            self.blood_form = BloodForm(self.tz, self.fname, self.surname)
            self.blood_form.show()
        else:
            QMessageBox.warning(self, "Blood / Pulse", "Choose a patient first")


    def delete_patient(self):
        if self.tz:
            if num_visits(self.tz) > 0:
                QMessageBox.warning(self, "Delete Patient", "Cannot delete patient with visits!")
            else:
                msgBox = QMessageBox(self)
                msgBox.setText("Really delete the patient!")
                msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                ret = msgBox.exec()
                if ret == QMessageBox.Ok:
                    delete_patient(self.tz)
                    self.clear_data()
                    self.populate_patients()
        else:
            QMessageBox.warning(self, "Patient Data", "Choose a patient first")

    def show_visits(self):
        if self.tz:
            self.visits_form = VisitForm(self.tz, self.fname, self.surname, self.mode)
            self.visits_form.show()
        else:
            QMessageBox.warning(self, "Patient Data", "Choose a patient first")

    def show_past_history(self):
        if self.tz:
            self.past_history_form = PastHistoryForm(self.tz, self.fname, self.surname)
            self.past_history_form.show()
        else:
            dlg = qtw.QMessageBox(self)
            dlg.setWindowTitle("Patient Data")
            dlg.setText("Choose a patient first")
            button = dlg.exec()
            if button == qtw.QMessageBox.Ok:
                print("OK!")


    def show_patient_details(self, index):
        for idx in self.lv_patients.selectedIndexes():
            result = self.lv_patients.model().itemData(idx)
            # print(result)
            fields = result[0].split(":")
            self.fname = fields[2].strip()
            self.surname = fields[3].strip()
            self.le_fname.setText(self.fname)
            self.le_surname.setText(self.surname)
            self.tz = fields[1].strip()
            self.le_tz.setText(self.tz)
            p = get_patient_by_id(fields[1].strip())
            self.le_email.setText(p[2])
            self.le_phone.setText(p[3])
            self.cb_smoker.setChecked(p[4])
            self.cb_consent.setChecked(p[5])
            self.rb_male.setChecked(p[1])
            self.de_dob.setDate(p[0])
            self.rb_female.setChecked(not p[1])
            self.lb_current_patient.setText("  {}   {} {}".format(self.tz, self.fname, self.surname))

    def save_new_patient(self, SAVE_NEW):
        print("In save patient with ", SAVE_NEW)
        fname = string.capwords(self.le_fname.text().strip())
        surname = string.capwords(self.le_surname.text().strip())
        tz = self.le_id.text().strip()
        email = self.le_email.text().strip()
        phone = self.le_phone.text().strip()
        smoker = self.cb_smoker.isChecked()
        consent = self.cb_consent.isChecked()
        male = self.rb_male.isChecked()
        dob = self.de_dob.date().toPython()
        check = self.check_new_patient(tz, fname, surname, email, phone, dob, SAVE_NEW)
        match check:
            case error_codes.ERR_OK:
                if SAVE_NEW:
                    save_new_patient(tz, fname, surname, email, phone, smoker, dob, male, consent)
                    QMessageBox.information(self, "Patients", "New Patient {} {} was saved".format(fname, surname))
                    self.clear_data()
                else:
                    modify_patient(tz, fname, surname, email, phone, smoker, dob, male, consent)
                    QMessageBox.information(self, "Patients", "Patient {} {} was modified".format(fname, surname))
                self.populate_patients()
            case error_codes.ERR_EXISTS:
                QMessageBox.warning(self, "Patients", "Patient {} {} could not be saved!!".format(fname, surname))
            case _:
                print("other error")


    def populate_patients(self):
        # print("About to Populate")
        self.lv_model.beginResetModel()
        self.lv_model.clear()
        for p in get_all_patients():
            s = '{} : {:>10} : {:>18} : {:>18}'.format(p[0], p[1].strip(), p[2].strip(), p[3].strip())
            self.lv_model.the_list.append((False, s))
        # print("Done update pop model")
        self.lv_model.endResetModel()
        # self.lv_model.layoutAboutToBeChanged.emit()
        # self.lv_model.layoutChanged.emit()
        self.lb_total.setText(str(self.lv_model.rowCount()))
        toDate = self.de_to.date().toPython()
        fromDate = self.de_from.date().toPython()

        print("Emitted ===>", toDate, fromDate)
        vbd = visits_between_dates(fromDate, toDate)
        pbd = visits_with_procedures_between_dates(fromDate, toDate)
        print(vbd, pbd)
        self.lb_proc.setText(str(pbd))
        self.lb_visits.setText(str(vbd))

    def clear_data(self):
        self.le_surname.setText('')
        self.le_fname.setText('')
        self.le_id.setText('')
        self.le_email.setText('')
        self.le_phone.setText('')
        self.cb_smoker.setChecked(False)
        self.cb_consent.setChecked(False)
        self.rb_male.setChecked(False)
        self.de_dob.setDate(datetime.date.today())
        self.rb_female.setChecked(False)
    def check_new_patient(self, tz, fname, surname, email, phone, dob, ADD_PATIENT=True):
        tz = tz.strip()
        e = False
        print("len ", len(tz), tz.isdigit())
        if len(tz) != 9 or not tz.isdigit():
            e = True
            QMessageBox.warning(self, "Patient Data", "Missing 9 digits for ID!")
        elif not fname.strip():
            e = True
            QMessageBox.warning(self, "Patient Data", "Missing Patient First Name!")
        elif not surname.strip():
            e = True
            QMessageBox.warning(self, "Patient Data", "Missing Patient Surname!")
        elif not is_email(email):
            e = True
            QMessageBox.warning(self, "Patient Data", "Please provide a valid email!")
        elif check_good_phone(phone) == error_codes.ERR_BAD:
            e = True
            QMessageBox.warning(self, "Patient Data", "Please provide a valid phone number!")
        elif dob > datetime.datetime.today().date():
            e = True
            QMessageBox.warning(self, "Patient Data", "The birth date is in the future!")
        elif ADD_PATIENT and patient_exists(tz):
            e = True
            QMessageBox.warning(self, "Patient Data", "This patient already exists in the database!")
        if e:
            return error_codes.ERR_BAD
        else:
            return error_codes.ERR_OK


def check_good_phone(phone):
    phone = phone.strip().replace('-', '')
    if len(phone) not in [9,10] or not phone.isdigit() or phone[0] != '0' :
        print("Phone BAD")
        return error_codes.ERR_BAD
    else:
        print("Phone GOOD")
        return error_codes.ERR_OK

# def check_good_email(email):
#
#     if re.match(pattern, email):
#         return error_codes.ERR_OK
#     else:
#         return error_codes.ERR_BAD
    #
    #
    # if email_pattern.fullmatch(email):
    #     return error_codes.ERR_OK
    # else:
    #     return error_codes.ERR_BAD


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    # Apply the font defined at the top of this file to the whole app.
    # You can change the family/size above, e.g., font.setFamily("DejaVu Sans"); font.setPointSize(10)
    app.setFont(font)

    window = MainWindow()

    sys.exit(app.exec())
