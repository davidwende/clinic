# import re
import sys
# from PySide6 import QtCore as qtc
# from PySide6.QtCore import Qt
from PySide6 import QtWidgets as qtw
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem

from PySide6 import QtGui as qtg

import error_codes
# import error_codes
from Blood.UI.uiBloodForm import uiBloodForm
from Database.dbFuncs import get_visit_dates, get_all_blood, add_blood_to_db
import string
import datetime

def check_blood(pulse, systolic, diastolic):
    if systolic and int(systolic) > 254:
        return error_codes.ERR_BAD
    if diastolic and int(diastolic) > 120:
        return error_codes.ERR_BAD
    if pulse and int(pulse) > 200:
        return error_codes.ERR_BAD
    if (systolic and not diastolic) or (not systolic and diastolic):
        return error_codes.ERR_BAD
    if not pulse and not systolic and not diastolic:
        return error_codes.ERR_BAD
    return error_codes.ERR_OK


class BloodForm(uiBloodForm):
    def __init__(self, tz, fname, surname):
        super().__init__()

        font = qtg.QFont()
        font.setStyleHint(qtg.QFont.TypeWriter)
        font.setFamily('monospace')

        self.tz = tz
        self.fname = fname
        self.surname = surname
        self.lb_patient.setText("Patient: {}   {} {}".format(self.tz, self.fname, self.surname))
        self.visit_date = None

        self.today = datetime.date.today().strftime("%Y %m %d")
        self.populate_dates()
        # self.populate_blood()
        self.pb_add.clicked.connect(self.add_blood)
        self.pb_delete.clicked.connect(self.delete_blood)
        self.pb_exit.clicked.connect(self.close)

        self.old_index = len(get_visit_dates(self.tz))
        self.cb_date.currentIndexChanged.connect(self.change_visit_date)

        self.lb_patient.setStyleSheet("border :2px solid black;")
        self.setMinimumSize(400,400)
        self.show()

    def add_blood(self):
        # first check that date is today
        # print(self.cb_date.currentText())
        if self.today != self.cb_date.currentText():
            QMessageBox.critical(self, "Save", "Can't add to a date that is not TODAY!")
        else:
            pulse = self.le_pulse.text()
            systolic = self.le_systolic.text()
            diastolic = self.le_diastolic.text()
            if error_codes.ERR_OK == check_blood(pulse, systolic, diastolic):
                time = datetime.datetime.now().strftime("%H:%M")
                rowPosition = self.table.rowCount()
                self.table.insertRow(rowPosition)
                self.table.setItem(rowPosition, 0, QTableWidgetItem(time))
                self.table.setItem(rowPosition, 1, QTableWidgetItem(pulse))
                self.table.setItem(rowPosition, 2, QTableWidgetItem(systolic))
                self.table.setItem(rowPosition, 3, QTableWidgetItem(diastolic))

                # now add to DB
                add_blood_to_db(self.tz, self.visit_date, datetime.datetime.now().time(),
                                pulse, systolic, diastolic)
            else:
                QMessageBox.critical(self, "Save", "Some values are not valid!")

    def delete_blood(self):
        pass

    def change_visit_date(self, index):
        # print("In change visit date: index is ", index)
        new_value = self.cb_date.currentText()
        # Get the text of the old item
        old_value = self.cb_date.itemText(self.old_index)
        # print("In change_visit_date old value {} new value {}".format(old_value, new_value))
        if old_value == self.today and new_value != self.today:
            msgBox = QMessageBox(self)
            msgBox.setText("You are nagivating away from todays visit. Continue?")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel )
            ret = msgBox.exec()
            if ret == QMessageBox.Ok:
                self.show_visit(new_value)
                self.old_index = index
            else:
                self.cb_date.setCurrentIndex(self.old_index)
        self.show_blood(new_value)


    def populate_dates(self):
        dates = get_visit_dates(self.tz)
        dates = [date.strftime("%Y %m %d") for date in dates]
        self.cb_date.addItems(dates)
        if not dates or self.today != dates[-1]:
            self.cb_date.addItem(self.today)
        print("length of dates is ", self.cb_date.count())
        self.cb_date.setCurrentIndex(self.cb_date.count() -  1)
        self.show_blood(self.today)


    def show_blood(self, d):
        year, month, day = d.split()
        self.visit_date = datetime.date(int(year), int(month), int(day))
        bloods = get_all_blood(self.tz, self.visit_date)
        self.table.clearContents()
        for r in range(len(bloods) - self.table.rowCount()):
            self.table.insertRow(r)
        for i, b in enumerate(bloods):
            t = str(b[0]).split(':')[:2]
            t = ':'.join(t)
            self.table.setItem(i, 0, QTableWidgetItem(t))
            self.table.setItem(i, 1, QTableWidgetItem(str(b[1])))
            self.table.setItem(i, 2, QTableWidgetItem(str(b[2])))
            self.table.setItem(i, 3, QTableWidgetItem(str(b[3])))


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    window = BloodForm()
    window.show()

    sys.exit(app.exec())
