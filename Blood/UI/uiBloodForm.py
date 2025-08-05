from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, Slot, QAbstractTableModel,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform, QValidator)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel, QListView,
    QLineEdit, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QTextEdit, QVBoxLayout, QTableView, QTableWidget,
    QWidget, QMainWindow, QMessageBox, QTableWidgetItem)
import sys
import re


class NumbersOnly(QValidator):
    def validate(self, string, index):
        pattern = re.compile("[0-9]+")
        if string == "":
            return QValidator.State.Acceptable, string, index
        if pattern.fullmatch(string):
            return QValidator.State.Acceptable, string, index
        else:
            return QValidator.State.Invalid, string, index


class CustomListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteSelectedItem()
        else:
            super().keyPressEvent(event)

    def deleteSelectedItem(self):
        selected_indexes = self.selectedIndexes()
        if selected_indexes:
            model = self.model()
            for index in selected_indexes:
                del model.procedures[index.row()]
                model.layoutChanged.emit()
            QMessageBox.information(self, "Delete", "Selected item(s) deleted.")
        else:
            QMessageBox.warning(self, "Delete", "No item selected.")


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


class uiBloodForm(QMainWindow):
    def __init__(self):
        super().__init__()

        layVerticalTop       = QVBoxLayout()
        layHorizontalPatient = QHBoxLayout()
        layData = QGridLayout()
        layHorizontalButtons = QHBoxLayout()

        # layHorizontalPatient
        self.lb_patient = QLabel("Patient: ")
        self.cb_date = QComboBox()

        layHorizontalPatient.addWidget(self.lb_patient)
        layHorizontalPatient.addStretch()
        layHorizontalPatient.addWidget(self.cb_date)

        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Time", "Pulse", "Systolic", "Diastolic"])
        self.table.setDisabled(True)

        font = QFont()
        font.setBold(True)

        self.table.setFont(font)

        layVerticalTop.addLayout(layHorizontalPatient)
        layVerticalTop.addWidget(self.table)

        # Data

        self.lb_pulse = QLabel("Pulse Rate")
        self.lb_systolic = QLabel("Systolic")
        self.lb_diastolic = QLabel("Diastolic")
        layData.addWidget(self.lb_pulse, 0,0)
        layData.addWidget(self.lb_systolic, 0,1)
        layData.addWidget(self.lb_diastolic, 0,2)


        self.le_pulse = QLineEdit()
        self.le_systolic = QLineEdit()
        self.le_diastolic = QLineEdit()
        layData.addWidget(self.le_pulse, 1, 0)
        layData.addWidget(self.le_systolic, 1, 1)
        layData.addWidget(self.le_diastolic, 1, 2)
        self.le_pulse.setValidator(NumbersOnly())
        self.le_systolic.setValidator(NumbersOnly())
        self.le_diastolic.setValidator(NumbersOnly())

        # buttons
        self.pb_add = QPushButton("Add a reading")
        self.pb_delete = QPushButton("Delete a reading")
        # self.pb_save = QPushButton("Save")
        self.pb_exit = QPushButton("Exit")

        layHorizontalButtons.addWidget(self.pb_add)
        layHorizontalButtons.addWidget(self.pb_delete)
        # layHorizontalButtons.addWidget(self.pb_save)
        layHorizontalButtons.addWidget(self.pb_exit)

        layVerticalTop.addLayout(layData)
        layVerticalTop.addLayout(layHorizontalButtons)

        layVerticalTop.addLayout(layHorizontalPatient)
        layVerticalTop.addLayout(layData)
        layVerticalTop.addLayout(layHorizontalButtons)

        widget = QWidget()

        widget.setLayout(layVerticalTop)
        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = uiBloodForm()
    window.show()

    sys.exit(app.exec())
