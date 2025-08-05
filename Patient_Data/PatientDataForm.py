import sys
from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw
from PySide6 import QtGui as qtg


from Patient_Data.UI.patient_data_window import Ui_w_PatientData


class PatientDataForm(qtw.QWidget, Ui_w_PatientData):
    # login_success = qtc.Signal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pb_Cancel.clicked.connect(self.close)
        self.pb_Save.clicked.connect(self.process_login)

    @qtc.Slot()
    def process_login(self):
        print("Save pressed")

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    window = PatientDataForm()
    window.show()

    sys.exit(app.exec())