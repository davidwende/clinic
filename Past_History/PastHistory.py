import datetime
import string
import sys
from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from PySide6 import QtGui as qtg
from Database.dbFuncs import get_past_history, save_patient_history,\
    get_nacs, get_all_nacs, save_nacs,\
    get_acs, get_all_acs, save_acs

from Past_History.UI.past_history_window import Ui_w_past_history

class ListViewModel(qtc.QAbstractListModel):
    def __init__(self, the_list = None):
        super().__init__()
        self.the_list = the_list or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            status, text = self.the_list[index.row()]
            return text

    def rowCount(self, index):
        return len(self.the_list)

    def clear(self):
        self.the_list.clear()

class PastHistoryForm(qtw.QWidget, Ui_w_past_history):
    # login_success = qtc.Signal()

    def __init__(self, tz, fname, surname):
        super().__init__()
        self.setupUi(self)
        self.tz = tz
        self.fname = fname
        self.surname = surname
        self.lb_patient.setStyleSheet("border :2px solid black;")
        self.lb_patient.setText("Patient: {}   {} {}".format(self.tz, self.fname, self.surname))

        # self.lb_patient.setText(self.tz)
        self.nacs_changed = False
        self.acs_changed = False
        # List Models
        self.nac_model = ListViewModel(the_list=[])
        self.lv_nac.setModel(self.nac_model)
        self.ac_model = ListViewModel(the_list=[])
        self.lv_ac.setModel(self.ac_model)
        # Signals
        self.pb_cancel.clicked.connect(self.close)
        self.pb_save.clicked.connect(self.save_history)
        self.pb_add_nac.clicked.connect(self.add_nac)
        self.pb_del_nac.clicked.connect(self.del_nac)
        self.cb_nac.currentTextChanged.connect(self.le_nac.setText)
        self.pb_add_ac.clicked.connect(self.add_ac)
        self.pb_del_ac.clicked.connect(self.del_ac)
        self.cb_ac.currentTextChanged.connect(self.le_ac.setText)

        self.populate()


    def add_nac(self):
        nac = self.le_nac.text().strip()
        if nac and (False, nac) not in self.nac_model.the_list:
            nac = string.capwords(nac)
            self.nac_model.the_list.append((False, nac))
            self.nac_model.layoutChanged.emit()
            self.nacs_changed = True
            self.le_nac.setText('')

    def add_ac(self):
        ac = self.le_ac.text().strip()
        if ac and (False, ac) not in self.ac_model.the_list:
            ac = string.capwords(ac)
            self.ac_model.the_list.append((False, ac))
            self.ac_model.layoutChanged.emit()
            self.acs_changed = True
            self.le_ac.setText('')

    def del_nac(self):
        idxs = self.lv_nac.selectedIndexes()
        if idxs:
            idx = idxs[0]
            del self.nac_model.the_list[idx.row()]
            self.nac_model.layoutChanged.emit()
            self.lv_nac.clearSelection()
            self.nacs_changed = True

    def del_ac(self):
        idxs = self.lv_ac.selectedIndexes()
        if idxs:
            idx = idxs[0]
            del self.ac_model.the_list[idx.row()]
            self.ac_model.layoutChanged.emit()
            self.lv_ac.clearSelection()
            self.acs_changed = True

    def populate(self):
        # print("in pop with ", self.tz)
        ph = get_past_history(self.tz)
        if ph:
            self.cb_hypertension.setChecked(ph.hypertension)
            self.cb_diabetes.setChecked(ph.diabetes)
            self.cb_blood.setChecked(ph.blood)
            self.le_blood.setText(ph.blood_descr)
            self.cb_malignancies.setChecked(ph.malignancy)
            self.le_malignancy_date.setText(ph.malignancy_date)
            self.le_malignancy_details.setText(ph.malignancy_details)
            self.cb_remission.setChecked(ph.malignancy_remiss)
            self.cb_disabilities.setChecked(ph.disable)
            self.le_disabilities.setText(ph.disable_details)
            self.plt_operations.setPlainText(ph.operations)
            self.plt_trauma.setPlainText(ph.trauma)
            nacs = get_nacs(self.tz)
            self.nac_model.the_list = [(False, x) for x in nacs]
            self.nac_model.layoutChanged.emit()
            acs = get_acs(self.tz)
            self.ac_model.the_list = [(False, x) for x in acs]
            self.ac_model.layoutChanged.emit()
        all_nacs = get_all_nacs()
        self.cb_nac.addItems(all_nacs)
        all_acs = get_all_acs()
        self.cb_ac.addItems(all_acs)

    @qtc.Slot()
    def save_history(self):
        hyper = self.cb_hypertension.isChecked()
        diabetes = self.cb_diabetes.isChecked()
        blood = self.cb_blood.isChecked()
        blood_details = self.le_blood.text()
        malig = self.cb_malignancies.isChecked()
        malig_details = self.le_malignancy_details.text()
        malig_date = self.le_malignancy_date.text()
        malig_remiss = self.cb_remission.isChecked()
        disable = self.cb_disabilities.isChecked()
        disable_details = self.le_disabilities.text()
        operations = self.plt_operations.toPlainText()
        trauma = self.plt_trauma.toPlainText()
        save_patient_history(self.tz, hyper, diabetes, blood, blood_details,
                             malig, malig_date,malig_details, malig_remiss,
                             disable, disable_details,
                             operations,trauma)
        # Now save lists of nacs, ac
        if self.nacs_changed:
            nacs = [x[1] for x in self.nac_model.the_list]
            save_nacs(self.tz, nacs)
        if self.acs_changed:
            acs = [x[1] for x in self.ac_model.the_list]
            save_acs(self.tz, acs)
        QMessageBox.information(self, "Patient History", "Patient History was saved")

    @qtc.Slot()
    def process_modify(self):
        print("Modify clicked")
        self.close()

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    window = PastHistoryForm()
    window.show()

    sys.exit(app.exec())