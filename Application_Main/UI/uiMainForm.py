import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QRadioButton,
    QButtonGroup, QDateEdit, QCheckBox, QListView
)
from PySide6.QtCore import Qt


class UI_MainWindow(object):
    def setupUi(self, w_MainWindow):
        # if not w_MainWindow.objectName():
        #     w_MainWindow.setObjectName(u"w_MainWindow")




        self.setWindowTitle("Patient Database")
        self.resize(900, 550)

        # =========================================================
        # Main layout
        # =========================================================
        main_layout = QVBoxLayout()

        # =========================================================
        # Top header pane (center-aligned labels)
        # =========================================================
        top_layout = QHBoxLayout()

        self.lb_left_header = QLabel("Current Patient")
        self.lb_current_patient = QLabel("")
        top_layout.addStretch()

        top_layout.addWidget(self.lb_left_header, alignment=Qt.AlignRight)
        #top_layout.addStretch()
        top_layout.addWidget(self.lb_current_patient, alignment=Qt.AlignLeft)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)

        # =========================================================
        # Top section: LEFT + RIGHT panes
        # =========================================================
        panes_layout = QHBoxLayout()

        # ==========================
        # LEFT PANE
        # ==========================
        self.gb_choose_pat = QGroupBox("Choose Patient")
        left_layout = QVBoxLayout(self.gb_choose_pat)

        self.lv_patients = QListView()
        left_layout.addWidget(self.lv_patients)

        self.bn_refresh = QPushButton("Refresh")
        left_layout.addWidget(self.bn_refresh)

        # Search
        hbox_search = QHBoxLayout()
        self.lb_search = QLabel("Search by:")
        self.le_search = QLineEdit()
        hbox_search.addWidget(self.lb_search)
        hbox_search.addWidget(self.le_search)
        left_layout.addLayout(hbox_search)

        # Statistics
        stats_layout = QFormLayout()

        self.de_from = QDateEdit()
        self.de_from.setCalendarPopup(True)
        self.de_from.setDisplayFormat("dd/MM/yyyy")

        self.de_to = QDateEdit()
        self.de_to.setCalendarPopup(True)
        self.de_to.setDisplayFormat("dd/MM/yyyy")

        self.lb_total = QLabel("0")
        self.lb_visits = QLabel("0")
        self.lb_proc = QLabel("0")

        stats_layout.addRow("From Date:", self.de_from)
        stats_layout.addRow("To Date:", self.de_to)
        stats_layout.addRow("Total # Patients:", self.lb_total)
        stats_layout.addRow("Total # Visits:", self.lb_visits)
        stats_layout.addRow("Total # Procedures:", self.lb_proc)

        left_layout.addLayout(stats_layout)

        # ==========================
        # RIGHT PANE
        # ==========================
        self.gb_pat_details = QGroupBox("Patient Details")
        right_layout = QVBoxLayout()
        fl_pat_details = QFormLayout(self.gb_pat_details)

        self.le_surname = QLineEdit()
        self.le_fname = QLineEdit()
        self.le_tz = QLineEdit()
        self.le_email = QLineEdit()
        self.le_phone = QLineEdit()

        fl_pat_details.addRow("Surname:", self.le_surname)
        fl_pat_details.addRow("First Name:", self.le_fname)
        fl_pat_details.addRow("TZ (ID):", self.le_tz)

        # Gender
        gender_layout = QHBoxLayout()
        self.rb_male = QRadioButton("Male")
        self.rb_female = QRadioButton("Female")
        self.rb_male.setChecked(True)

        self.gender_group = QButtonGroup(self)
        self.gender_group.addButton(self.rb_male, 1)
        self.gender_group.addButton(self.rb_female, 2)

        gender_layout.addWidget(self.rb_male)
        gender_layout.addWidget(self.rb_female)
        gender_layout.addStretch()

        fl_pat_details.addRow("Gender:", gender_layout)

        # DOB
        self.de_dob = QDateEdit()
        self.de_dob.setCalendarPopup(True)
        self.de_dob.setDisplayFormat("dd/MM/yyyy")

        fl_pat_details.addRow("Date of Birth:", self.de_dob)

        fl_pat_details.addRow("Email:", self.le_email)
        fl_pat_details.addRow("Phone:", self.le_phone)

        self.cb_smoker = QCheckBox()
        self.cb_consent = QCheckBox()
        fl_pat_details.addRow("Smoker:", self.cb_smoker)
        fl_pat_details.addRow("Consent Signed:", self.cb_consent)

        right_layout.addWidget(self.gb_pat_details)

        # ---------------------------------------------------------
        # Clear button (full width)
        # ---------------------------------------------------------
        self.bn_clear = QPushButton("Clear")
        right_layout.addWidget(self.bn_clear)

        # ---------------------------------------------------------
        # Save / Modify / Delete buttons (below Clear)
        # ---------------------------------------------------------
        hbox_actions = QHBoxLayout()
        self.bn_save = QPushButton("Save as new Patient")
        self.bn_modify = QPushButton("Modify Patient Data")
        self.bn_delete = QPushButton("Delete Patient Data")

        hbox_actions.addWidget(self.bn_save)
        hbox_actions.addWidget(self.bn_modify)
        hbox_actions.addWidget(self.bn_delete)

        right_layout.addLayout(hbox_actions)
        right_layout.addStretch()

        # ---------------------------------------------------------
        # Assemble panes
        # ---------------------------------------------------------
        panes_layout.addWidget(self.gb_choose_pat)
        panes_layout.addLayout(right_layout)


        panes_layout.setStretchFactor(self.gb_choose_pat, 1)
        panes_layout.setStretchFactor(right_layout, 1)

        main_layout.addLayout(panes_layout)

        # Create and set a central widget so layouts and group boxes
        # are owned by the MainWindow and won't be garbage-collected.
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # =========================================================
        # Bottom navigation buttons (equal width)
        # =========================================================
        hbox_bottom = QHBoxLayout()

        self.bn_history = QPushButton("Past History")
        self.bn_blood = QPushButton("Blood Pressure / Pulse")
        self.bn_visits = QPushButton("Visits")

        hbox_bottom.addWidget(self.bn_history)
        hbox_bottom.addWidget(self.bn_blood)
        hbox_bottom.addWidget(self.bn_visits)

        hbox_bottom.setStretch(0, 1)
        hbox_bottom.setStretch(1, 1)
        hbox_bottom.setStretch(2, 1)

        main_layout.addLayout(hbox_bottom)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = UI_MainWindow()
    w.show()
    sys.exit(app.exec())
