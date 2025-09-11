from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, Slot,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel, QListView,
    QLineEdit, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QTextEdit, QVBoxLayout,
    QWidget, QMainWindow, QMessageBox)
import sys
from my_classes import HoverButton

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


class uiVisitForm(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Patient Visit")
        layVerticalTop       = QVBoxLayout()
        layHorizontalPatient = QHBoxLayout()
        layHorizontalData    = QHBoxLayout()
        layVerticalTabs      = QVBoxLayout()
        layHorizontalButtons = QHBoxLayout()

        self.checkboxPairs = {}
        # layHorizontalPatient
        self.lb_patient = QLabel("Patient: ")
        # self.le_patient = QLineEdit()
        self.cb_date = QComboBox()
        # self.pb_new = QPushButton("New Visit")

        layHorizontalPatient.addWidget(self.lb_patient)
        layHorizontalPatient.addStretch()
        layHorizontalPatient.addWidget(self.cb_date)

        self.pb_cc = QPushButton("Current Complaint", self)
        # self.pb_cc = QPushButton("Current Complaint", self)
        self.pb_cc.setAutoFillBackground(True)
        self.pb_neck = QPushButton("Neck")
        self.pb_shoulder = QPushButton("Shoulder")
        self.pb_back = QPushButton("Back")
        self.pb_knee_ankle = QPushButton("Knee - Ankle")
        self.pb_hip = QPushButton("Hip")
        self.pb_exam = QPushButton("Examination")
        self.pb_tests = QPushButton("Tests")
        self.pb_proc = QPushButton("Procedures")
        self.pb_recommend = QPushButton("Recomendations")
        self.pb_diagnoses = QPushButton("Diagnoses")
        self.pb_reports = QPushButton("Summary")

        self.pb_cc.setStyleSheet("background-color: yellow;")

        layVerticalTabs.addWidget(self.pb_cc)
        layVerticalTabs.addWidget(self.pb_exam)
        layVerticalTabs.addWidget(self.pb_back)
        layVerticalTabs.addWidget(self.pb_hip)
        layVerticalTabs.addWidget(self.pb_neck)
        layVerticalTabs.addWidget(self.pb_shoulder)
        layVerticalTabs.addWidget(self.pb_knee_ankle)
        layVerticalTabs.addWidget(self.pb_tests)
        layVerticalTabs.addWidget(self.pb_diagnoses)
        layVerticalTabs.addWidget(self.pb_proc)
        layVerticalTabs.addWidget(self.pb_recommend)
        layVerticalTabs.addWidget(self.pb_reports)

        # row = 0
        self.cb_trend_l, self.cb_trend_l_pos, self.cb_trend_r, self.cb_trend_r_pos = None, None, None, None
        self.cb_slr_l, self.cb_slr_l_le, self.cb_slr_r, self.cb_slr_r_le = None, None, None, None
        self.cb_phf_l, self.cb_phf_l_pos, self.cb_phf_r, self.cb_phf_r_pos = None, None, None, None
        self.cb_tt_l, self.cb_tt_l_pos, self.cb_tt_r, self.cb_tt_r_pos = None, None, None, None
        self.cb_Fabere_l, self.cb_Fabere_l_pos, self.cb_Fabere_r, self.cb_Fabere_r_pos = None, None, None, None
        self.cb_Sensation, self.cb_Sensation_equals, self.le_Sensation = None, None, None

        self.cb_hip_pt, self.rb_hip_pt_normal, self.rb_hip_pt_posterior, self.rb_hip_pt_anterior = None, None, None, None
        self.hip_trend_l, self.hip_trend_r, self.hip_trend_l_pos, self.hip_trend_r_pos = None, None, None, None
        self.cb_hip_trend_l, self.cb_hip_trend_l_pos, self.cb_hip_trend_r, self.cb_hip_trend_r_pos= None, None, None, None

        self.lb_hip_lrot_l, self.le_hip_lrot_l_pos, self.lb_hip_lrot_r, self.le_hip_lrot_r_pos = None, None, None, None

        self.cb_hip_mrot_l, self.cb_hip_mrot_l_limited, self.cb_hip_mrot_r, self.cb_hip_mrot_r_limited = None, None, None, None


        self.gb_back = self.doLayoutBack()
        self.gb_neck = self.doLayoutNeck()
        self.gb_knee_ankle = self.doLayoutKneeAnkle()
        self.gb_shoulder = self.doLayoutShoulder()
        self.gb_hip = self.doLayoutHip()
        self.gb_cc = self.doLayoutCC()
        self.gb_exam = self.doLayoutExam()
        self.gb_tests = self.doLayoutTests()
        self.gb_proc = self.doLayoutProc()
        self.gb_recommend = self.doLayoutRecommend()
        self.gb_diagnoses = self.doLayoutDiagnoses()
        self.gb_reports = self.doLayoutReports()


        #=======
        self.sw_data = QStackedWidget()
        self.sw_data.addWidget(self.gb_cc)
        self.sw_data.addWidget(self.gb_exam)
        self.sw_data.addWidget(self.gb_back)
        self.sw_data.addWidget(self.gb_hip)
        self.sw_data.addWidget(self.gb_neck)
        self.sw_data.addWidget(self.gb_shoulder)
        self.sw_data.addWidget(self.gb_knee_ankle)
        self.sw_data.addWidget(self.gb_tests)
        self.sw_data.addWidget(self.gb_diagnoses)
        self.sw_data.addWidget(self.gb_proc)
        self.sw_data.addWidget(self.gb_recommend)
        self.sw_data.addWidget(self.gb_reports)

        # Allow pushbuttons to choose the tab
        self.pb_cc.clicked.connect(lambda: self.onChooseTab(0, self.pb_cc))
        self.pb_exam.clicked.connect(lambda: self.onChooseTab(1, self.pb_exam))
        self.pb_back.clicked.connect(lambda: self.onChooseTab(2, self.pb_back))
        self.pb_hip.clicked.connect(lambda: self.onChooseTab(3, self.pb_hip))
        self.pb_neck.clicked.connect(lambda: self.onChooseTab(4, self.pb_neck))
        self.pb_shoulder.clicked.connect(lambda: self.onChooseTab(5, self.pb_shoulder))
        self.pb_knee_ankle.clicked.connect(lambda: self.onChooseTab(6, self.pb_knee_ankle))
        self.pb_tests.clicked.connect(lambda: self.onChooseTab(7, self.pb_tests))
        self.pb_diagnoses.clicked.connect(lambda: self.onChooseTab(8, self.pb_diagnoses))
        self.pb_proc.clicked.connect(lambda: self.onChooseTab(9, self.pb_proc))
        self.pb_recommend.clicked.connect(lambda: self.onChooseTab(10, self.pb_recommend))
        self.pb_reports.clicked.connect(lambda: self.onChooseTab(11, self.pb_reports))

        self.pb_save = HoverButton("Save the Visit")
        self.pb_clear = HoverButton("Clear Visit Form")
        self.pb_delete = HoverButton("Delete Todays' Visit")
        # self.pb_summary = HoverButton("Print Visit Summary")
        self.pb_cancel = HoverButton("Exit")

        layHorizontalButtons.addWidget(self.pb_save)
        layHorizontalButtons.addWidget(self.pb_clear)
        layHorizontalButtons.addWidget(self.pb_delete)
        # layHorizontalButtons.addWidget(self.pb_summary)
        layHorizontalButtons.addWidget(self.pb_cancel)

        layHorizontalData.addLayout(layVerticalTabs)
        layHorizontalData.addWidget(self.sw_data)

        layVerticalTop.addLayout(layHorizontalPatient)
        layVerticalTop.addLayout(layHorizontalData)
        layVerticalTop.addLayout(layHorizontalButtons)

        widget = QWidget()

        widget.setLayout(layVerticalTop)
        self.setCentralWidget(widget)

        self.buttons = [self.pb_cc, self.pb_back, self.pb_neck, self.pb_exam,
                        self.pb_shoulder, self.pb_knee_ankle, self.pb_hip,
                        self.pb_proc, self.pb_recommend, self.pb_diagnoses,
                        self.pb_reports, self.pb_tests]

        self.setTopEnabled(widget)
        self.onChooseTab(0, self.pb_cc)

    def setAllDisabled(self, w):
        for c in w.findChildren(QWidget):
            if c not in self.buttons and not c.property("top"):
                c.setEnabled(False)

    def setTopEnabled(self, w):
        # print("in set initial")
        for c in w.findChildren(QWidget):
            if c.property("top"):
                # print(c)
                c.setEnabled(True)


    @Slot()
    def onChooseTab(self, index, w):
        self.sw_data.setCurrentIndex(index)
        allClear(self.buttons, w)


    def doLayoutHip(self):
        gb_hip = QGroupBox("Hip")
        gb_hip.setAlignment(Qt.AlignCenter)
        gb_hip_assess = QGroupBox("Hip Assessment")
        gb_hip_assess.setAlignment(Qt.AlignCenter)
        gb_hip_passive = QGroupBox("Hip Passive")
        gb_hip_passive.setAlignment(Qt.AlignCenter)
        gb_hip_resisted = QGroupBox("Hip Resisted")
        gb_hip_resisted.setAlignment(Qt.AlignCenter)
        gb_hip_other = QGroupBox("Hip Other")
        gb_hip_other.setAlignment(Qt.AlignCenter)

        layGridHipAssessment = QGridLayout()
        self.bg_hip_pt = QButtonGroup(self)
        # self.bg_hip_pt.setExclusive(False)
        self.cb_hip_pt = QCheckBox("Pelvic Tilt")
        self.cb_hip_pt.setProperty("top", True)
        self.rb_hip_pt_normal    = QRadioButton("Normal")
        self.rb_hip_pt_posterior = QRadioButton("Posterior")
        self.rb_hip_pt_anterior  = QRadioButton("Anterior")
        self.bg_hip_pt.addButton(self.rb_hip_pt_normal)
        self.bg_hip_pt.addButton(self.rb_hip_pt_posterior)
        self.bg_hip_pt.addButton(self.rb_hip_pt_anterior)
        layGridHipAssessment.addWidget(self.cb_hip_pt,0,0)
        layGridHipAssessment.addWidget(self.rb_hip_pt_normal,0,1)
        layGridHipAssessment.addWidget(self.rb_hip_pt_posterior,0,2)
        layGridHipAssessment.addWidget(self.rb_hip_pt_anterior,0,3)

        self.cb_hip_trend_l     = QCheckBox("Trendelenberg, L")
        self.cb_hip_trend_l_pos = QCheckBox("+ve")
        self.cb_hip_trend_r     = QCheckBox("Trendelenberg, R")
        self.cb_hip_trend_r_pos = QCheckBox("+ve")

        self.checkboxPairs[self.cb_hip_trend_l] = [self.cb_hip_trend_l_pos]
        self.checkboxPairs[self.cb_hip_trend_r] = [self.cb_hip_trend_r_pos]
        self.cb_hip_trend_l.stateChanged.connect(self.onCheckboxStateChanged)
        self.cb_hip_trend_r.stateChanged.connect(self.onCheckboxStateChanged)

        layGridHipAssessment.addWidget(self.cb_hip_trend_l,1,0)
        layGridHipAssessment.addWidget(self.cb_hip_trend_l_pos,1,1)
        layGridHipAssessment.addWidget(self.cb_hip_trend_r,1,2)
        layGridHipAssessment.addWidget(self.cb_hip_trend_r_pos,1,3)

        gb_hip_assess.setLayout(layGridHipAssessment)

        layGridHipPassive = QGridLayout()
        self.lb_hip_lrot_l = QLabel("Lateral Rotation, L")
        self.le_hip_lrot_l_pos = QLineEdit()
        self.lb_hip_lrot_r = QLabel("Lateral Rotation, R")
        self.le_hip_lrot_r_pos = QLineEdit()
        layGridHipPassive.addWidget(self.lb_hip_lrot_l,0,0)
        layGridHipPassive.addWidget(self.le_hip_lrot_l_pos,0,1)
        layGridHipPassive.addWidget(self.lb_hip_lrot_r,0,2)
        layGridHipPassive.addWidget(self.le_hip_lrot_r_pos,0,3)

        self.lb_hip_mrot_l = QLabel("Medial Rotation, L")
        self.le_hip_mrot_l_pos = QLineEdit()
        self.lb_hip_mrot_r = QLabel("Medial Rotation, R")
        self.le_hip_mrot_r_pos = QLineEdit()
        layGridHipPassive.addWidget(self.lb_hip_mrot_l,1,0)
        layGridHipPassive.addWidget(self.le_hip_mrot_l_pos,1,1)
        layGridHipPassive.addWidget(self.lb_hip_mrot_r,1,2)
        layGridHipPassive.addWidget(self.le_hip_mrot_r_pos,1,3)

        self.lb_hip_flex_l = QLabel("Flexion, L")
        self.le_hip_flex_l_pos = QLineEdit()
        self.lb_hip_flex_r = QLabel("Flexion, R")
        self.le_hip_flex_r_pos = QLineEdit()
        layGridHipPassive.addWidget(self.lb_hip_flex_l,2,0)
        layGridHipPassive.addWidget(self.le_hip_flex_l_pos,2,1)
        layGridHipPassive.addWidget(self.lb_hip_flex_r,2,2)
        layGridHipPassive.addWidget(self.le_hip_flex_r_pos,2,3)

        gb_hip_passive.setLayout(layGridHipPassive)

        layGridHipResisted = QGridLayout()

        layGridHipResisted, self.cb_hip_abd_l, self.cb_hip_abd_l_painful, \
        self.cb_hip_abd_r, self.cb_hip_abd_r_painful= self.isPositive("Abduction", "Painful", layGridHipResisted, 0)

        layGridHipResisted, self.cb_hip_rlrot_l, self.cb_hip_rlrot_l_painful, \
        self.cb_hip_rlrot_r, self.cb_hip_rlrot_r_painful= self.isPositive("Lateral Rotation", "Painful", layGridHipResisted, 1)

        layGridHipResisted, self.cb_hip_rmrot_l, self.cb_hip_rmrot_l_painful, \
        self.cb_hip_rmrot_r, self.cb_hip_rmrot_r_painful= self.isPositive("Medial Rotation", "Painful", layGridHipResisted, 2)

        layGridHipResisted, self.cb_hip_radd_l, self.cb_hip_radd_l_painful, \
        self.cb_hip_radd_r, self.cb_hip_radd_r_painful= self.isPositive("Adduction", "Painful", layGridHipResisted, 3)

        layGridHipResisted, self.cb_hip_flexion_l, self.cb_hip_flexion_l_pain, \
        self.cb_hip_flexion_r, self.cb_hip_flexion_r_pain= self.isPositive("Flexion", "Painful", layGridHipResisted, 4)

        layGridHipResisted, self.cb_hip_extension_l, self.cb_hip_extension_l_pain, \
        self.cb_hip_extension_r, self.cb_hip_extension_r_pain= self.isPositive("Extension", "Painful", layGridHipResisted, 5)

        gb_hip_resisted.setLayout(layGridHipResisted)

        layGridHipOther = QGridLayout()
        self.lb_hip_tender = QLabel("Tenderness")
        self.le_hip_tenderness = QLineEdit()
        self.lb_hip_other = QLabel("Other")
        self.le_hip_other = QLineEdit()
        layGridHipOther.addWidget(self.lb_hip_tender,0,0)
        layGridHipOther.addWidget(self.le_hip_tenderness,0,1,1,3)
        layGridHipOther.addWidget(self.lb_hip_other,1,0)
        layGridHipOther.addWidget(self.le_hip_other,1,1,1,3)

        gb_hip_other.setLayout(layGridHipOther)

        layHip = QVBoxLayout()
        layHip.addWidget(gb_hip_assess)
        layHip.addWidget(gb_hip_passive)
        layHip.addWidget(gb_hip_resisted)
        layHip.addWidget(gb_hip_other)
        layHip.addStretch()

        gb_hip.setLayout(layHip)
        return gb_hip

    def doLayoutBack(self):
        gb_back_top = QGroupBox("Back")
        gb_back_top.setAlignment(Qt.AlignCenter)

        gb_back = QGroupBox("Examinations")
        gb_back.setAlignment(Qt.AlignCenter)

        gb_backhip = QGroupBox("Resisted Hip")
        gb_backhip.setAlignment(Qt.AlignCenter)
        gb_backhip.isCheckable()

        gb_backtspine = QGroupBox("Thoracic Spine")
        gb_backtspine.setAlignment(Qt.AlignCenter)
        gb_backtspine.isCheckable()

        layBack = QVBoxLayout()
        layGridBack = QGridLayout()
        layBackHip = QGridLayout()
        layBackTSpine = QGridLayout()

        row=0
        self.lb_back_movement = QLabel("Movement", self)
        self.le_back_movement = QLineEdit(self)

        layGridBack.addWidget(self.lb_back_movement,row,0)
        layGridBack.addWidget(self.le_back_movement,row,1,1,3 )
        # print("Done row %d" % row)

        row = row+1
        self.cb_trend_l = QCheckBox("Trendelenberg, L", self)
        self.cb_trend_l.setProperty("top", True)
        self.cb_trend_l_pos = QCheckBox("+ve", self)
        self.cb_trend_r = QCheckBox("Trendelenberg, R", self)
        self.cb_trend_r.setProperty("top", True)
        self.cb_trend_r_pos = QCheckBox("+ve", self)

        self.checkboxPairs[self.cb_trend_l] = [self.cb_trend_l_pos]
        self.checkboxPairs[self.cb_trend_r] = [self.cb_trend_r_pos]
        self.cb_trend_l.stateChanged.connect(self.onCheckboxStateChanged)
        self.cb_trend_r.stateChanged.connect(self.onCheckboxStateChanged)

        layGridBack.addWidget(self.cb_trend_l,row,0)
        layGridBack.addWidget(self.cb_trend_l_pos,row,1)
        layGridBack.addWidget(self.cb_trend_r,row,2)
        layGridBack.addWidget(self.cb_trend_r_pos,row,3)
        # print("Done row %d" % row)

        row = row + 1
        self.lb_slr_l = QLabel("SLR, L", self)
        self.le_slr_l_le = QLineEdit(self)
        self.lb_slr_r = QLabel("SLR, R", self)
        self.le_slr_r_le = QLineEdit(self)
        layGridBack.addWidget(self.lb_slr_l,row,0)
        layGridBack.addWidget(self.le_slr_l_le,row,1)
        layGridBack.addWidget(self.lb_slr_r,row,2)
        layGridBack.addWidget(self.le_slr_r_le,row,3)
        # print("Done row %d" % row)

        row = row + 1
        self.cb_fst_l = QCheckBox("FST, L", self)
        self.cb_fst_l_pos = QCheckBox("+ve", self)
        self.cb_fst_r = QCheckBox("FST, R", self)
        self.cb_fst_r_pos = QCheckBox("+ve", self)

        self.checkboxPairs[self.cb_fst_l] = [self.cb_fst_l_pos]
        self.checkboxPairs[self.cb_fst_r] = [self.cb_fst_r_pos]
        self.cb_fst_l.stateChanged.connect(self.onCheckboxStateChanged)
        self.cb_fst_r.stateChanged.connect(self.onCheckboxStateChanged)

        layGridBack.addWidget(self.cb_fst_l,row,0)
        layGridBack.addWidget(self.cb_fst_l_pos,row,1)
        layGridBack.addWidget(self.cb_fst_r,row,2)
        layGridBack.addWidget(self.cb_fst_r_pos,row,3)
        # print("Done row %d" % row)

        row = row + 1
        self.cb_phf_l = QCheckBox("Passive Hip Flexion, L", self)
        self.cb_phf_l_pos = QCheckBox("Painful", self)
        self.cb_phf_r = QCheckBox("Passive Hip Flexion, R", self)
        self.cb_phf_r_pos = QCheckBox("Painful", self)

        self.checkboxPairs[self.cb_phf_l] = [self.cb_phf_l_pos]
        self.checkboxPairs[self.cb_phf_r] = [self.cb_phf_r_pos]
        self.cb_phf_l.stateChanged.connect(self.onCheckboxStateChanged)
        self.cb_phf_r.stateChanged.connect(self.onCheckboxStateChanged)

        layGridBack.addWidget(self.cb_phf_l,row,0)
        layGridBack.addWidget(self.cb_phf_l_pos,row,1)
        layGridBack.addWidget(self.cb_phf_r,row,2)
        layGridBack.addWidget(self.cb_phf_r_pos,row,3)
        # print("Done row %d" % row)

        row = row + 1
        self.cb_tt_l = QCheckBox("Thigh Thrust, L", self)
        self.cb_tt_l_pos = QCheckBox("+ve", self)
        self.cb_tt_r = QCheckBox("Thigh Thrust, R", self)
        self.cb_tt_r_pos = QCheckBox("+ve", self)

        self.checkboxPairs[self.cb_tt_l] = [self.cb_tt_l_pos]
        self.checkboxPairs[self.cb_tt_r] = [self.cb_tt_r_pos]
        self.cb_tt_l.stateChanged.connect(self.onCheckboxStateChanged)
        self.cb_tt_r.stateChanged.connect(self.onCheckboxStateChanged)

        layGridBack.addWidget(self.cb_tt_l,row,0)
        layGridBack.addWidget(self.cb_tt_l_pos,row,1)
        layGridBack.addWidget(self.cb_tt_r,row,2)
        layGridBack.addWidget(self.cb_tt_r_pos,row,3)
        # print("Done row %d" % row)

        row = row + 1
        self.cb_Fabere_l = QCheckBox("Fabere, L", self)
        self.cb_Fabere_l_pos = QCheckBox("+ve", self)
        self.cb_Fabere_r = QCheckBox("Fabere, R", self)
        self.cb_Fabere_r_pos = QCheckBox("+ve", self)

        self.checkboxPairs[self.cb_Fabere_l] = [self.cb_Fabere_l_pos]
        self.checkboxPairs[self.cb_Fabere_r] = [self.cb_Fabere_r_pos]
        self.cb_Fabere_l.stateChanged.connect(self.onCheckboxStateChanged)
        self.cb_Fabere_r.stateChanged.connect(self.onCheckboxStateChanged)

        layGridBack.addWidget(self.cb_Fabere_l,row,0)
        layGridBack.addWidget(self.cb_Fabere_l_pos,row,1)
        layGridBack.addWidget(self.cb_Fabere_r,row,2)
        layGridBack.addWidget(self.cb_Fabere_r_pos,row,3)
        # print("Done row %d" % row)

        row = row + 1
        self.cb_Sensation = QCheckBox("Sensation", self)
        self.cb_Sensation_equals = QCheckBox("L==R?", self)
        self.le_Sensation = QLineEdit(self)

        self.checkboxPairs[self.cb_Sensation] = [self.cb_Sensation_equals, self.le_Sensation]
        self.cb_Sensation.stateChanged.connect(self.onCheckboxStateChanged)

        layGridBack.addWidget(self.cb_Sensation,row,0)
        layGridBack.addWidget(self.cb_Sensation_equals,row,1)
        layGridBack.addWidget(self.le_Sensation,row,2, 1,2)
        # print("Done row %d" % row)

        row = row + 1
        self.cb_power = QCheckBox("Power", self)
        self.cb_power_equals = QCheckBox("L==R?", self)
        self.le_power = QLineEdit(self)

        self.checkboxPairs[self.cb_power] = [self.cb_power_equals, self.le_power]
        self.cb_power.stateChanged.connect(self.onCheckboxStateChanged)

        layGridBack.addWidget(self.cb_power,row,0)
        layGridBack.addWidget(self.cb_power_equals,row,1)
        layGridBack.addWidget(self.le_power,row,2, 1,2)
        # print("Done row %d" % row)

        row = row + 1
        self.cb_reflexes = QCheckBox("Reflexes", self)
        self.cb_reflexes_equals = QCheckBox("L==R?", self)
        self.le_reflexes = QLineEdit(self)

        self.checkboxPairs[self.cb_reflexes] = [self.cb_reflexes_equals, self.le_reflexes]
        self.cb_reflexes.stateChanged.connect(self.onCheckboxStateChanged)

        layGridBack.addWidget(self.cb_reflexes,row,0)
        layGridBack.addWidget(self.cb_reflexes_equals,row,1)
        layGridBack.addWidget(self.le_reflexes,row,2, 1,2)

        gb_back.setLayout(layGridBack)


        self.cb_bhip_abd_l     = QCheckBox("Abduction , L"    , self)
        self.cb_bhip_abd_pos_l = QCheckBox("+ve"  , self)
        self.cb_bhip_abd_r     = QCheckBox("Abduction , R"    , self)
        self.cb_bhip_abd_pos_r = QCheckBox("+ve"  , self)
        self.checkboxPairs[self.cb_bhip_abd_l] = [self.cb_bhip_abd_pos_l]
        self.checkboxPairs[self.cb_bhip_abd_r] = [self.cb_bhip_abd_pos_r]
        self.cb_bhip_abd_l.stateChanged.connect(self.onCheckboxStateChanged)
        self.cb_bhip_abd_r.stateChanged.connect(self.onCheckboxStateChanged)
        layBackHip.addWidget(self.cb_bhip_abd_l     , 0   , 0)
        layBackHip.addWidget(self.cb_bhip_abd_pos_l , 0   , 1)
        layBackHip.addWidget(self.cb_bhip_abd_r     , 0   , 2)
        layBackHip.addWidget(self.cb_bhip_abd_pos_r , 0   , 3)

        self.cb_bhip_lrot_l     = QCheckBox("Lateral Rotation , L"    , self)
        self.cb_bhip_lrot_pos_l = QCheckBox("+ve"  , self)
        self.cb_bhip_lrot_r     = QCheckBox("Lateral Rotation , R"    , self)
        self.cb_bhip_lrot_pos_r = QCheckBox("+ve"  , self)
        self.checkboxPairs[self.cb_bhip_lrot_l] = [self.cb_bhip_lrot_pos_l]
        self.checkboxPairs[self.cb_bhip_lrot_r] = [self.cb_bhip_lrot_pos_r]
        self.cb_bhip_lrot_l.stateChanged.connect(self.onCheckboxStateChanged)
        self.cb_bhip_lrot_r.stateChanged.connect(self.onCheckboxStateChanged)
        layBackHip.addWidget(self.cb_bhip_lrot_l     , 1   , 0)
        layBackHip.addWidget(self.cb_bhip_lrot_pos_l , 1   , 1)
        layBackHip.addWidget(self.cb_bhip_lrot_r     , 1   , 2)
        layBackHip.addWidget(self.cb_bhip_lrot_pos_r , 1   , 3)

        self.cb_bhip_add_l     = QCheckBox("Adduction , L"    , self)
        self.cb_bhip_add_pos_l = QCheckBox("+ve"  , self)
        self.cb_bhip_add_r     = QCheckBox("Adduction , R"    , self)
        self.cb_bhip_add_pos_r = QCheckBox("+ve"  , self)
        self.checkboxPairs[self.cb_bhip_add_l] = [self.cb_bhip_add_pos_l]
        self.checkboxPairs[self.cb_bhip_add_r] = [self.cb_bhip_add_pos_r]
        self.cb_bhip_add_l.stateChanged.connect(self.onCheckboxStateChanged)
        self.cb_bhip_add_r.stateChanged.connect(self.onCheckboxStateChanged)
        layBackHip.addWidget(self.cb_bhip_add_l     , 2   , 0)
        layBackHip.addWidget(self.cb_bhip_add_pos_l , 2   , 1)
        layBackHip.addWidget(self.cb_bhip_add_r     , 2   , 2)
        layBackHip.addWidget(self.cb_bhip_add_pos_r , 2   , 3)

        self.cb_bhip_flex_l     = QCheckBox("Flexion , L"    , self)
        self.cb_bhip_flex_pos_l = QCheckBox("+ve"  , self)
        self.cb_bhip_flex_r     = QCheckBox("Flexion , R"    , self)
        self.cb_bhip_flex_pos_r = QCheckBox("+ve"  , self)
        self.checkboxPairs[self.cb_bhip_flex_l] = [self.cb_bhip_flex_pos_l]
        self.checkboxPairs[self.cb_bhip_flex_r] = [self.cb_bhip_flex_pos_r]
        self.cb_bhip_flex_l.stateChanged.connect(self.onCheckboxStateChanged)
        self.cb_bhip_flex_r.stateChanged.connect(self.onCheckboxStateChanged)
        layBackHip.addWidget(self.cb_bhip_flex_l     , 3   , 0)
        layBackHip.addWidget(self.cb_bhip_flex_pos_l , 3   , 1)
        layBackHip.addWidget(self.cb_bhip_flex_r     , 3   , 2)
        layBackHip.addWidget(self.cb_bhip_flex_pos_r , 3   , 3)

        self.lb_bhip_tender     = QLabel("Tenderness"    , self)
        self.le_bhip_tender = QLineEdit()
        layBackHip.addWidget(self.lb_bhip_tender , 4   , 0)
        layBackHip.addWidget(self.le_bhip_tender , 4   , 1, 1, 3)

        gb_backhip.setLayout(layBackHip)

        self.cb_back_tspine_rot_l = QCheckBox("Thoracic Spine Rot L")
        self.cb_back_tspine_rot_l_pain = QCheckBox("Painful")
        self.cb_back_tspine_rot_r = QCheckBox("Thoracic Spine Rot R")
        self.cb_back_tspine_rot_r_pain = QCheckBox("Painful")
        self.lb_back_tspine_tender = QLabel("Tenderness")
        self.checkboxPairs[self.cb_back_tspine_rot_l] = [self.cb_back_tspine_rot_l_pain]
        self.checkboxPairs[self.cb_back_tspine_rot_r] = [self.cb_back_tspine_rot_r_pain]
        self.cb_back_tspine_rot_l.stateChanged.connect(self.onCheckboxStateChanged)
        self.cb_back_tspine_rot_r.stateChanged.connect(self.onCheckboxStateChanged)

        self.le_back_tspine_rot_tender = QLineEdit()

        layBackTSpine.addWidget(self.cb_back_tspine_rot_l, 0, 0)
        layBackTSpine.addWidget(self.cb_back_tspine_rot_l_pain, 0, 1)
        layBackTSpine.addWidget(self.cb_back_tspine_rot_r, 0, 2)
        layBackTSpine.addWidget(self.cb_back_tspine_rot_r_pain, 0, 3)
        layBackTSpine.addWidget(self.lb_back_tspine_tender, 1, 0)
        layBackTSpine.addWidget(self.le_back_tspine_rot_tender, 1, 1, 1, 3)

        gb_backtspine.setLayout(layBackTSpine)

        layBack.addWidget(gb_back)
        layBack.addWidget(gb_backhip)
        layBack.addWidget(gb_backtspine)
        layBack.addStretch()
        gb_back_top.setLayout(layBack)
        return gb_back_top

    def doLayoutKneeAnkle(self):
        gb_knee_ankle = QGroupBox("Knee - Ankle")
        gb_knee_ankle.setAlignment(Qt.AlignCenter)
        gb_ankle = QGroupBox("Ankle Joint")
        gb_ankle.setAlignment(Qt.AlignCenter)
        gb_ankle_st = QGroupBox("Ankle Subtalar")
        gb_ankle_st.setAlignment(Qt.AlignCenter)
        gb_knee = QGroupBox("Knee")
        gb_knee.setAlignment(Qt.AlignCenter)

        laykneeankle = QVBoxLayout()
        layankle     = QGridLayout()
        layankle_st  = QGridLayout()
        layknee      = QGridLayout()

        layankle, self.cb_ankle_scar_l, self.cb_ankle_scar_pos_l, \
        self.cb_ankle_scar_r, self.cb_ankle_scar_pos_r= self.isPositive("Scarring Ankle", "+ve", layankle, 0)

        # TODO align should be L/R

        self.cb_ankle_align_l = QCheckBox("Alignment L", self)
        self.rb_ankle_pronate_l = QRadioButton("Pronated", self)
        self.rb_ankle_supinate_l = QRadioButton("Supinated", self)
        scarg3 = QButtonGroup(self)
        scarg3.addButton(self.rb_ankle_pronate_l)
        scarg3.addButton(self.rb_ankle_supinate_l)
        layankle.addWidget(self.cb_ankle_align_l  ,1,0)
        layankle.addWidget(self.rb_ankle_pronate_l  ,1,1)
        layankle.addWidget(self.rb_ankle_supinate_l  ,1,2)

        self.cb_ankle_align_r = QCheckBox("Alignment R", self)
        self.rb_ankle_pronate_r = QRadioButton("Pronated", self)
        self.rb_ankle_supinate_r = QRadioButton("Supinated", self)
        scarg4 = QButtonGroup(self)
        scarg4.addButton(self.rb_ankle_pronate_r)
        scarg4.addButton(self.rb_ankle_supinate_r)
        layankle.addWidget(self.cb_ankle_align_r  ,1,3)
        layankle.addWidget(self.rb_ankle_pronate_r  ,1,4)
        layankle.addWidget(self.rb_ankle_supinate_r  ,1,5)

        # TODO dors/plant should be L/R
        self.lb_ankle_dors_l = QLabel("Dorsflexion L", self)
        self.le_ankle_dors_l = QLineEdit()
        self.lb_ankle_dors_r = QLabel("Dorsflexion R", self)
        self.le_ankle_dors_r = QLineEdit()

        layankle.addWidget(self.lb_ankle_dors_l, 2, 0)
        layankle.addWidget(self.le_ankle_dors_l, 2, 1, 1, 2)
        layankle.addWidget(self.lb_ankle_dors_r, 2, 3)
        layankle.addWidget(self.le_ankle_dors_r, 2, 4, 1, 2)

        self.lb_ankle_plant_l = QLabel("Plantarflexion L", self)
        self.le_ankle_plant_l = QLineEdit()
        self.lb_ankle_plant_r = QLabel("Plantarflexion R", self)
        self.le_ankle_plant_r = QLineEdit()
        layankle.addWidget(self.lb_ankle_plant_l, 3, 0)
        layankle.addWidget(self.le_ankle_plant_l, 3, 1, 1, 2)
        layankle.addWidget(self.lb_ankle_plant_r, 3, 3)
        layankle.addWidget(self.le_ankle_plant_r, 3, 4, 1, 2)

        self.lb_ankle_inversion_l = QLabel("Inversion L", self)
        self.le_ankle_inversion_l = QLineEdit()
        self.lb_ankle_inversion_r = QLabel("Inversion R", self)
        self.le_ankle_inversion_r = QLineEdit()
        layankle.addWidget(self.lb_ankle_inversion_l, 4, 0)
        layankle.addWidget(self.le_ankle_inversion_l, 4, 1, 1, 2)
        layankle.addWidget(self.lb_ankle_inversion_r, 4, 3)
        layankle.addWidget(self.le_ankle_inversion_r, 4, 4, 1, 2)

        self.lb_ankle_eversion_l = QLabel("Eversion L", self)
        self.le_ankle_eversion_l = QLineEdit()
        self.lb_ankle_eversion_r = QLabel("Eversion R", self)
        self.le_ankle_eversion_r = QLineEdit()
        layankle.addWidget(self.lb_ankle_eversion_l, 5, 0)
        layankle.addWidget(self.le_ankle_eversion_l, 5, 1, 1, 2)
        layankle.addWidget(self.lb_ankle_eversion_r, 5, 3)
        layankle.addWidget(self.le_ankle_eversion_r, 5, 4, 1, 2)

        self.lb_ankle_tender_l = QLabel("Tender L", self)
        self.le_ankle_tender_l = QLineEdit()
        self.lb_ankle_tender_r = QLabel("Tender R", self)
        self.le_ankle_tender_r = QLineEdit()
        layankle.addWidget(self.lb_ankle_tender_l, 6, 0)
        layankle.addWidget(self.le_ankle_tender_l, 6, 1, 1, 2)
        layankle.addWidget(self.lb_ankle_tender_r, 6, 3)
        layankle.addWidget(self.le_ankle_tender_r, 6, 4, 1, 2)

        gb_ankle.setLayout(layankle)

        # === subtalar =======
        layankle_st, self.cb_anklest_addpain_l, self.cb_anklest_addpain_pos_l, \
        self.cb_anklest_addpain_r, self.cb_anklest_addpain_pos_r = self.isPositive("Adduction Painful","+ve", layankle_st, 0)

        layankle_st, self.cb_anklest_abcpain_l, self.cb_anklest_abcpain_pos_l, \
        self.cb_anklest_abcpain_r, self.cb_anklest_abcpain_pos_r = self.isPositive("Abduction Painful","+ve", layankle_st, 1)
        
        layankle_st, self.cb_anklest_addlimited_l, self.cb_anklest_addlimited_pos_l, \
        self.cb_anklest_addlimited_r, self.cb_anklest_addlimited_pos_r = self.isPositive("Adduction Limited","+ve", layankle_st, 2)

        layankle_st, self.cb_anklest_abclimited_l, self.cb_anklest_abclimited_pos_l, \
        self.cb_anklest_abclimited_r, self.cb_anklest_abclimited_pos_r = self.isPositive("Abduction Limited","+ve", layankle_st, 3)
        
        gb_ankle_st.setLayout(layankle_st)

        # ===== Knee =====
        layknee, self.cb_knee_scar_l, self.cb_knee_scar_pos_l,  \
        self.cb_knee_scar_r, self.cb_knee_scar_pos_r = self.isPositive("Scarring Knee","+ve", layknee, 0)
        
        self.cb_knee_align_l = QCheckBox("Alignment, L", self)
        self.cb_knee_align_pos_l = QCheckBox("Abnormal", self)
        self.le_knee_align_no_l = QLineEdit()
        self.cb_knee_align_r = QCheckBox("Alignment, R", self)
        self.cb_knee_align_pos_r = QCheckBox("Abnormal", self)
        self.le_knee_align_no_r = QLineEdit()
        layknee.addWidget(self.cb_knee_align_l     , 1 , 0)
        layknee.addWidget(self.cb_knee_align_pos_l , 1 , 1)
        layknee.addWidget(self.le_knee_align_no_l  , 1 , 2)
        layknee.addWidget(self.cb_knee_align_r     , 1 , 3)
        layknee.addWidget(self.cb_knee_align_pos_r , 1 , 4)
        layknee.addWidget(self.le_knee_align_no_r  , 1 , 5)

        layknee, self.cb_knee_muscle_l, self.cb_knee_muscle_pos_l,\
        self.cb_knee_muscle_r, self.cb_knee_muscle_pos_r = self.isPositive("Muscle Wasting","+ve", layknee, 2)

        layknee, self.cb_knee_effusion_l, self.cb_knee_effusion_pos_l, \
        self.cb_knee_effusion_r, self.cb_knee_effusion_pos_r = self.isPositive("Effusion", "+ve",layknee, 3)

        layknee, self.cb_knee_rext_l, self.cb_knee_rext_pos_l, \
        self.cb_knee_rext_r, self.cb_knee_rext_pos_r  = self.isPositive("Resisted Extension Pain", "+ve",layknee, 4)

        layknee, self.cb_knee_rflex_l, self.cb_knee_rflex_pos_l,  \
        self.cb_knee_rflex_r, self.cb_knee_rflex_pos_r = self.isPositive("Resisted Flexion Pain","+ve", layknee, 5)
        
        layknee, self.cb_knee_mm_l, self.cb_knee_mm_pos_l, \
        self.cb_knee_mm_r, self.cb_knee_mm_pos_r = self.isPositive("Pos. McMurrays","+ve", layknee, 6)
        
        layknee, self.cb_knee_pfg_l, self.cb_knee_pfg_pos_l, \
        self.cb_knee_pfg_r, self.cb_knee_pfg_pos_r = self.isPositive("Patelofemoral Grinding","+ve", layknee, 7)

        self.lb_knee_rom_l = QLabel("ROM, L", self)
        self.le_knee_rom_l = QLineEdit()
        self.lb_knee_rom_r = QLabel("ROM, R", self)
        self.le_knee_rom_r = QLineEdit()
        layknee.addWidget(self.lb_knee_rom_l , 8 , 0)
        layknee.addWidget(self.le_knee_rom_l , 8 , 1)
        layknee.addWidget(self.lb_knee_rom_r , 8 , 3)
        layknee.addWidget(self.le_knee_rom_r , 8 , 4)

        self.cb_knee_mcl_l = QCheckBox("MCL, L", self)
        self.cb_knee_mcl_lax_l = QCheckBox("Lax.")
        self.cb_knee_mcl_r = QCheckBox("MCL, R", self)
        self.cb_knee_mcl_lax_r = QCheckBox("Lax.")
        layknee.addWidget(self.cb_knee_mcl_l , 9 , 0)
        layknee.addWidget(self.cb_knee_mcl_lax_l , 9 , 1)
        layknee.addWidget(self.cb_knee_mcl_r , 9 , 3)
        layknee.addWidget(self.cb_knee_mcl_lax_r , 9 , 4)

        self.cb_knee_lcl_l = QCheckBox("LCL, L", self)
        self.cb_knee_lcl_lax_l = QCheckBox("Lax.")
        self.cb_knee_lcl_r = QCheckBox("LCL, R", self)
        self.cb_knee_lcl_lax_r = QCheckBox("Lax.")
        layknee.addWidget(self.cb_knee_lcl_l , 10 , 0)
        layknee.addWidget(self.cb_knee_lcl_lax_l , 10 , 1)
        layknee.addWidget(self.cb_knee_lcl_r , 10 , 3)
        layknee.addWidget(self.cb_knee_lcl_lax_r , 10 , 4)

        self.lb_knee_l_tender = QLabel("Tenderness L")
        self.le_knee_l_tender = QLineEdit()
        self.lb_knee_r_tender = QLabel("Tenderness R")
        self.le_knee_r_tender = QLineEdit()
        layknee.addWidget(self.lb_knee_l_tender , 11 , 0)
        layknee.addWidget(self.le_knee_l_tender , 11 , 1, 1, 2)
        layknee.addWidget(self.lb_knee_r_tender , 11 , 3)
        layknee.addWidget(self.le_knee_r_tender , 11 , 4, 1, 2)

        self.lb_knee_other = QLabel("Other")
        self.le_knee_other = QLineEdit()
        layknee.addWidget(self.lb_knee_other , 12 , 0)
        layknee.addWidget(self.le_knee_other , 12 , 1, 1, 3)

        gb_knee.setLayout(layknee)

        laykneeankle.addWidget(gb_knee)
        laykneeankle.addWidget(gb_ankle)
        laykneeankle.addWidget(gb_ankle_st)
        
        laykneeankle.addStretch()

        gb_knee_ankle.setLayout(laykneeankle)
        return gb_knee_ankle

    def doLayoutNeck(self):
        gb_neck = QGroupBox("Neck Examinations")
        gb_neck.setAlignment(Qt.AlignCenter)
        gb_neck.isCheckable()
        layneck = QVBoxLayout()
        layGridneck = QGridLayout()

        self.lb_neck_ext = QLabel("Extension", self)
        self.le_neck_ext = QLineEdit()
        self.lb_neck_rot_l = QLabel("Rotation, L", self)
        self.le_neck_rot_l = QLineEdit()
        self.lb_neck_rot_r = QLabel("Rotation, R", self)
        self.le_neck_rot_r = QLineEdit()

        layGridneck.addWidget(self.lb_neck_ext,0,0)
        layGridneck.addWidget(self.le_neck_ext,0,1, 1, 3)

        layGridneck.addWidget(self.lb_neck_rot_l,1,0)
        layGridneck.addWidget(self.le_neck_rot_l,1,1)
        layGridneck.addWidget(self.lb_neck_rot_r,1,2)
        layGridneck.addWidget(self.le_neck_rot_r,1,3)

        self.lb_neck_cranial = QLabel("Cranial Nerve")
        self.le_neck_cranial = QLineEdit()
        layGridneck.addWidget(self.lb_neck_cranial,2,0)
        layGridneck.addWidget(self.le_neck_cranial,2,1, 1, 3)

        self.cb_neck_sen = QCheckBox("Sensation", self)
        self.cb_neck_sen_equals = QCheckBox("L==R", self)
        self.le_neck_sen = QLineEdit()
        self.checkboxPairs[self.cb_neck_sen] = [self.cb_neck_sen_equals, self.le_neck_sen  ]
        self.cb_neck_sen.stateChanged.connect(self.onCheckboxStateChanged)
        layGridneck.addWidget(self.cb_neck_sen,3,0)
        layGridneck.addWidget(self.cb_neck_sen_equals,3,1)
        layGridneck.addWidget(self.le_neck_sen,3,2, 1, 2)

        self.cb_neck_power = QCheckBox("Power", self)
        self.cb_neck_power_equals = QCheckBox("L==R", self)
        self.le_neck_power = QLineEdit()
        self.checkboxPairs[self.cb_neck_power] = [self.cb_neck_power_equals, self.le_neck_power]
        self.cb_neck_power.stateChanged.connect(self.onCheckboxStateChanged)
        layGridneck.addWidget(self.cb_neck_power,4,0)
        layGridneck.addWidget(self.cb_neck_power_equals,4,1)
        layGridneck.addWidget(self.le_neck_power,4,2, 1, 2)

        self.cb_neck_reflexes = QCheckBox("Reflexes", self)
        self.cb_neck_reflexes_equals = QCheckBox("L==R", self)
        self.le_neck_reflexes = QLineEdit()
        self.checkboxPairs[self.cb_neck_reflexes] = [self.cb_neck_reflexes_equals, self.le_neck_reflexes]
        self.cb_neck_reflexes.stateChanged.connect(self.onCheckboxStateChanged)
        layGridneck.addWidget(self.cb_neck_reflexes, 5, 0)
        layGridneck.addWidget(self.cb_neck_reflexes_equals, 5, 1)
        layGridneck.addWidget(self.le_neck_reflexes, 5, 2, 1, 2)

        self.lb_neck_tender = QLabel("Tenderness", self)
        self.le_neck_tender = QLineEdit()
        layGridneck.addWidget(self.lb_neck_tender, 6, 0)
        layGridneck.addWidget(self.le_neck_tender, 6, 1, 1, 3)

        self.lb_neck_other = QLabel("Other", self)
        self.le_neck_other = QLineEdit()
        layGridneck.addWidget(self.lb_neck_other, 7, 0)
        layGridneck.addWidget(self.le_neck_other, 7, 1, 1, 3)

        layneck.addLayout(layGridneck)
        layneck.addStretch()
        gb_neck.setLayout(layneck)
        return gb_neck

    def doLayoutShoulder(self):
        gb_shoulder = QGroupBox("Shoulder Examinations")
        gb_shoulder.setAlignment(Qt.AlignCenter)
        gb_shoulder_align = QGroupBox("Scapular Motion")
        gb_shoulder_align.setAlignment(Qt.AlignCenter)
        gb_shoulder_passive = QGroupBox("Passive Shoulder Motion")
        gb_shoulder_passive.setAlignment(Qt.AlignCenter)
        gb_shoulder_resisted = QGroupBox("Resisted Shoulder Motion")
        gb_shoulder_resisted.setAlignment(Qt.AlignCenter)

        layShoulder = QVBoxLayout()

        layGridShoulder = QGridLayout()

        layShoulderResisted = QGridLayout()
        gb_shoulder_resisted.setLayout(layShoulderResisted)

        self.cb_sh_align_l = QCheckBox("Alignment, L", self)
        self.cb_sh_align_ab_l = QCheckBox("Abnormal", self)
        self.le_sh_align_l = QLineEdit()
        self.cb_sh_align_r = QCheckBox("Alignment, R", self)
        self.cb_sh_align_ab_r = QCheckBox("Abnormal", self)
        self.le_sh_align_r = QLineEdit()

        self.checkboxPairs[self.cb_sh_align_l] = [self.cb_sh_align_ab_l, self.le_sh_align_l  ]
        self.cb_sh_align_l.stateChanged.connect(self.onCheckboxStateChanged)
        self.checkboxPairs[self.cb_sh_align_r] = [self.cb_sh_align_ab_r, self.le_sh_align_r  ]
        self.cb_sh_align_r.stateChanged.connect(self.onCheckboxStateChanged)

        layGridShoulder.addWidget(self.cb_sh_align_l,0,0)
        layGridShoulder.addWidget(self.cb_sh_align_ab_l,0,1)
        layGridShoulder.addWidget(self.le_sh_align_l,0,2)

        layGridShoulder.addWidget(self.cb_sh_align_r,0,3)
        layGridShoulder.addWidget(self.cb_sh_align_ab_r,0,4)
        layGridShoulder.addWidget(self.le_sh_align_r,0,5)
        gb_shoulder_align.setLayout(layGridShoulder)

        group1 = QButtonGroup(self)
        self.cb_sh_rom_l = QCheckBox("ROM, L", self)
        self.rb_sh_rom_full_l = QRadioButton("Full", self)
        self.rb_sh_rom_limit_l = QRadioButton("Limited", self)
        group1.addButton(self.rb_sh_rom_full_l)
        group1.addButton(self.rb_sh_rom_limit_l)

        group2 = QButtonGroup(self)
        self.cb_sh_rom_r = QCheckBox("ROM, R", self)
        self.rb_sh_rom_full_r = QRadioButton("Full", self)
        self.rb_sh_rom_limit_r = QRadioButton("Limited", self)
        group2.addButton(self.rb_sh_rom_full_r)
        group2.addButton(self.rb_sh_rom_limit_r)

        layGridShoulder.addWidget(self.cb_sh_rom_l,1,0)
        layGridShoulder.addWidget(self.rb_sh_rom_full_l,1,1)
        layGridShoulder.addWidget(self.rb_sh_rom_limit_l,1,2)
        layGridShoulder.addWidget(self.cb_sh_rom_r,1,3)
        layGridShoulder.addWidget(self.rb_sh_rom_full_r,1,4)
        layGridShoulder.addWidget(self.rb_sh_rom_limit_r,1,5)

        # passive
        layShoulderPassive = QGridLayout()

        self.lb_sh_abd_l = QLabel("Abduction, L")
        self.le_sh_abd_l = QLineEdit()
        self.lb_sh_abd_r = QLabel("Abduction, R")
        self.le_sh_abd_r = QLineEdit()
        layShoulderPassive.addWidget(self.lb_sh_abd_l, 0,0)
        layShoulderPassive.addWidget(self.le_sh_abd_l, 0,1, 1, 2)
        layShoulderPassive.addWidget(self.lb_sh_abd_r, 0,3, 1, 2)
        layShoulderPassive.addWidget(self.le_sh_abd_r, 0,4, 1, 2)

        self.lb_sh_lrot_l = QLabel("Lat. Rotation, L")
        self.le_sh_lrot_l = QLineEdit()
        self.lb_sh_lrot_r = QLabel("Lat. Rotation, R")
        self.le_sh_lrot_r = QLineEdit()

        layShoulderPassive.addWidget(self.lb_sh_lrot_l, 1,0)
        layShoulderPassive.addWidget(self.le_sh_lrot_l, 1,1, 1, 2)
        layShoulderPassive.addWidget(self.lb_sh_lrot_r, 1,3, 1, 2)
        layShoulderPassive.addWidget(self.le_sh_lrot_r, 1,4, 1, 2)

        layShoulderPassive, self.cb_sh_mrot_l, self.cb_sh_mrot_limit_l, \
        self.cb_sh_mrot_r, self.cb_sh_mrot_limit_r, \
            self.cb_sh_mrot_pain_l, self.cb_sh_mrot_pain_r = self.isPositive("Med. Rotation", "Limited", layShoulderPassive, 2, True)

        layShoulderPassive, self.cb_sh_add_l, self.cb_sh_add_limit_l, \
        self.cb_sh_add_r, self.cb_sh_add_limit_r, \
            self.cb_sh_add_pain_l, self.cb_sh_add_pain_r = self.isPositive("Adduction", "Limited", layShoulderPassive, 3, True)


        gb_shoulder_passive.setLayout(layShoulderPassive)


        self.lb_sh_res_abd_l = QLabel("Abduction, L")
        self.le_sh_res_abd_l = QLineEdit()
        self.lb_sh_res_abd_r = QLabel("Abduction, R")
        self.le_sh_res_abd_r = QLineEdit()

        self.lb_sh_res_lrot_l = QLabel("Lat. Rotation, L")
        self.le_sh_res_lrot_l = QLineEdit()
        self.lb_sh_res_lrot_r = QLabel("Lat. Rotation, R")
        self.le_sh_res_lrot_r = QLineEdit()

        layShoulderResisted.addWidget(self.lb_sh_res_abd_l, 0,0)
        layShoulderResisted.addWidget(self.le_sh_res_abd_l, 0,1)
        layShoulderResisted.addWidget(self.lb_sh_res_abd_r, 0,2)
        layShoulderResisted.addWidget(self.le_sh_res_abd_r, 0,3)

        layShoulderResisted.addWidget(self.lb_sh_res_lrot_l, 1,0)
        layShoulderResisted.addWidget(self.le_sh_res_lrot_l, 1,1)
        layShoulderResisted.addWidget(self.lb_sh_res_lrot_r, 1,2)
        layShoulderResisted.addWidget(self.le_sh_res_lrot_r, 1,3)

        layShoulderResisted, self.cb_sh_res_mrot_l, self.cb_sh_res_mrot_painful_l, \
        self.cb_sh_res_mrot_r, self.cb_sh_res_mrot_painful_r= self.isPositive("Med. Rotation", "Painful", layShoulderResisted, 2)

        layShoulderResisted, self.cb_sh_res_add_l, self.cb_sh_res_add_painful_l, \
        self.cb_sh_res_add_r, self.cb_sh_res_add_painful_r= self.isPositive("Adduction", "Painful", layShoulderResisted, 3)

        layShoulderResisted, self.cb_sh_res_jobes_l, self.cb_sh_res_jobes_pos_l, \
        self.cb_sh_res_jobes_r, self.cb_sh_res_jobes_pos_r= self.isPositive("Jobes", "+ve", layShoulderResisted, 4)

        layShoulder.addWidget(gb_shoulder_align)
        layShoulder.addWidget(gb_shoulder_passive)
        layShoulder.addWidget(gb_shoulder_resisted)
        layShoulder.addStretch()
        gb_shoulder.setLayout(layShoulder)
        return gb_shoulder


    def update_cb_trend_l_pos(self):
        # print("changed")
        # print (self.cb_trend_l.isChecked())
        self.cb_trend_l_pos.setEnabled(self.cb_trend_l.isChecked())

    def doLayoutCC(self):
        gb_cc = QGroupBox("Current Complaint")
        gb_cc.setAlignment(Qt.AlignCenter)
        gb_cc_gen = QGroupBox("General")
        gb_cc_gen.setAlignment(Qt.AlignCenter)
        gb_aggravate = QGroupBox("Aggravating Factors")
        gb_aggravate.setAlignment(Qt.AlignCenter)
        gb_location = QGroupBox("Location")
        gb_location.setAlignment(Qt.AlignCenter)

        layGridCC = QGridLayout()
        layGridLocation = QGridLayout()

        self.lb_onset = QLabel("Onset of Pain", self)
        self.le_onset = QLineEdit()
        self.lb_description = QLabel("Description of Pain", self)
        self.te_description = QTextEdit()


        layGridCC.addWidget(self.lb_onset, 0, 0)
        layGridCC.addWidget(self.le_onset, 0, 1, 1, 3)
        layGridCC.addWidget(self.lb_description, 1,0)
        layGridCC.addWidget(self.te_description, 1,1, 1, 3)

        gb_cc_gen.setLayout(layGridCC)

        # Aggravating Factors
        layGridAggravate = QGridLayout()

        layGridAggravate, self.cb_cc_walking, self.le_cc_walking  = self.add_cb_le("Walking", layGridAggravate, 0, 0)
        layGridAggravate, self.cb_cc_standing, self.le_cc_standing  = self.add_cb_le("Standing", layGridAggravate, 0, 3)
        layGridAggravate, self.cb_cc_sitting, self.le_cc_sitting  = self.add_cb_le("Sitting", layGridAggravate, 1, 0)
        layGridAggravate, self.cb_cc_lying, self.le_cc_lying  = self.add_cb_le("Lying", layGridAggravate, 1, 3)
        layGridAggravate, self.cb_cc_lifting, self.le_cc_lifting  = self.add_cb_le("Lifting", layGridAggravate, 2, 0)
        layGridAggravate, self.cb_cc_shoulder_move, self.le_cc_shoulder_move  = self.add_cb_le("Shoulder Movement", layGridAggravate, 2, 3)

        gb_aggravate.setLayout(layGridAggravate)

        # Location
        layGridLocation = QGridLayout()
        self.cb_loc_neck = QCheckBox("Neck", self)
        self.cb_loc_spine = QCheckBox("Thoracic Spine")
        self.cb_loc_back = QCheckBox("Lower Back", self)

        self.cb_loc_shoulder_l = QCheckBox("Shoulder, L", self)
        self.cb_loc_shoulder_r = QCheckBox("Shoulder, R", self)
        self.cb_loc_hip_l = QCheckBox("Hip, L", self)
        self.cb_loc_hip_r = QCheckBox("Hip, R", self)

        self.cb_loc_groin_l = QCheckBox("Groin, L", self)
        self.cb_loc_groin_r = QCheckBox("Groin, R", self)
        self.cb_loc_knee_l = QCheckBox("Knee, L", self)
        self.cb_loc_knee_r = QCheckBox("Knee, R", self)

        self.cb_loc_ankle_l = QCheckBox("Ankle, L", self)
        self.cb_loc_ankle_r = QCheckBox("Ankle, R", self)
        self.cb_loc_other = QCheckBox("Other", self)
        self.le_loc_radiates = QLineEdit()
        self.le_loc_precise = QLineEdit()

        layGridLocation.addWidget(self.cb_loc_neck, 0, 0)
        layGridLocation.addWidget(self.cb_loc_spine, 0, 1)
        layGridLocation.addWidget(self.cb_loc_back, 0, 2)

        layGridLocation.addWidget(self.cb_loc_shoulder_l, 1, 0)
        layGridLocation.addWidget(self.cb_loc_shoulder_r, 1, 1)
        layGridLocation.addWidget(self.cb_loc_hip_l, 1, 2)
        layGridLocation.addWidget(self.cb_loc_hip_r, 1, 3)

        layGridLocation.addWidget(self.cb_loc_groin_l, 4, 0)
        layGridLocation.addWidget(self.cb_loc_groin_r, 4, 1)
        layGridLocation.addWidget(self.cb_loc_knee_l, 4, 2)
        layGridLocation.addWidget(self.cb_loc_knee_r, 4, 3)

        layGridLocation.addWidget(self.cb_loc_ankle_l, 5, 0)
        layGridLocation.addWidget(self.cb_loc_ankle_r, 5, 1)
        layGridLocation.addWidget(self.cb_loc_other, 5, 2)

        layGridLocation.addWidget(QLabel("Radiates"), 6, 0,)
        layGridLocation.addWidget(self.le_loc_radiates, 6, 1, 1,3)

        layGridLocation.addWidget(QLabel("Precise Location"), 7, 0,)
        layGridLocation.addWidget(self.le_loc_precise, 7, 1, 1,3)
        gb_location.setLayout(layGridLocation)

        layCC = QVBoxLayout()
        layCC.addWidget(gb_cc_gen)
        layCC.addWidget(gb_aggravate)
        layCC.addWidget(gb_location)
        layCC.addStretch()
        gb_cc.setLayout(layCC)
        return gb_cc

    def doLayoutExam(self):
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        gb_exam = QGroupBox("Examination")
        gb_exam.setAlignment(Qt.AlignCenter)
        gb_exam.setSizePolicy(sizePolicy)

        layExam = QVBoxLayout()
        self.te_exam = QTextEdit()
        self.te_exam.setSizePolicy(sizePolicy)

        layExam.addWidget(self.te_exam, 1)
        gb_exam.setLayout(layExam)
        return gb_exam

    def doLayoutTests(self):
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        gb_tests = QGroupBox("Tests")
        gb_tests.setAlignment(Qt.AlignCenter)
        gb_tests.setSizePolicy(sizePolicy)

        layTests = QVBoxLayout()
        self.te_tests = QTextEdit()
        self.te_tests.setSizePolicy(sizePolicy)

        layTests.addWidget(self.te_tests, 1)
        gb_tests.setLayout(layTests)
        return gb_tests

    def doLayoutRecommend(self):
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        gb_recommend = QGroupBox("Recommendations")
        gb_recommend.setAlignment(Qt.AlignCenter)
        gb_recommend.setSizePolicy(sizePolicy)
        layrecommend = QVBoxLayout()
        self.te_recommend = QTextEdit()
        self.te_recommend.setSizePolicy(sizePolicy)
        layrecommend.addWidget(self.te_recommend, 1)
        gb_recommend.setLayout(layrecommend)
        return gb_recommend

    def doLayoutDiagnoses(self):
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        gb_diagnoses = QGroupBox("Diagnoses")
        gb_diagnoses.setAlignment(Qt.AlignCenter)
        gb_diagnoses.setSizePolicy(sizePolicy)
        WIDTH = 250
        laydiag = QHBoxLayout()
        laydiag_buttons = QVBoxLayout()
        self.lv_diag = CustomListView()
        self.lv_diag.setFixedWidth(WIDTH)

        self.lv_diag_list = QListView()
        self.lv_diag_list.setFixedWidth(WIDTH)

        self.le_diag = QLineEdit()
        self.le_diag.setFixedWidth(WIDTH)

        self.le_diag_filter = QLineEdit()
        self.le_diag_filter.setFixedWidth(WIDTH)

        self.pb_diag_add = QPushButton("Add Diagnosis")
        self.pb_diag_add.setFixedWidth(WIDTH)
        self.pb_diag_del = QPushButton("Delete Diagnosis")
        self.pb_diag_del.setFixedWidth(WIDTH)

        self.lb_diag_details = QLabel("Diagnosis Details")
        self.lb_diag_details.setAlignment(Qt.AlignCenter)
        self.te_diag_details = QTextEdit()
        self.te_diag_details.setFixedWidth(WIDTH)
        self.pb_diag_add_details = QPushButton("Add Diagnosis Details")
        self.pb_diag_add_details.setFixedWidth(WIDTH)
        # self.pb_diag_del_details = QPushButton("Delete Diagnosis Details")
        # self.pb_diag_del_details.setFixedWidth(WIDTH)



        # laydiag_buttons.addWidget(self.cmb_diag)
        laydiag_buttons.addWidget(self.lv_diag_list)
        laydiag_buttons.addWidget(self.le_diag_filter)
        laydiag_buttons.addWidget(self.le_diag)
        laydiag_buttons.addWidget(self.pb_diag_add)
        laydiag_buttons.addWidget(self.pb_diag_del)
        laydiag_buttons.addStretch()
        laydiag_buttons.addWidget(self.lb_diag_details)
        laydiag_buttons.addWidget(self.te_diag_details)
        laydiag_buttons.addWidget(self.pb_diag_add_details)
        # laydiag_buttons.addWidget(self.pb_diag_del_details)

        laydiag_buttons.addStretch(2)

        laydiag.addWidget(self.lv_diag)
        laydiag.addLayout(laydiag_buttons)

        gb_diagnoses.setLayout(laydiag)
        return gb_diagnoses

    def doLayoutReports(self):
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        gb_reports = QGroupBox("Summary")
        gb_reports.setAlignment(Qt.AlignCenter)
        gb_reports.setSizePolicy(sizePolicy)
        layreports= QVBoxLayout()
        layButtons = QHBoxLayout()
        self.te_reports = QTextEdit()
        self.te_reports.setSizePolicy(sizePolicy)

        self.pb_review = HoverButton("Create Visit Summary")
        # self.pb_print_preview = HoverButton("Print Preview Visit Summary")
        self.pb_print = HoverButton("Print Visit Summary")

        layButtons.addWidget(self.pb_review)
        # layButtons.addWidget(self.pb_print_preview)
        layButtons.addWidget(self.pb_print)

        layreports.addWidget(self.te_reports, 1)
        layreports.addLayout(layButtons)
        gb_reports.setLayout(layreports)
        return gb_reports

    def doLayoutProc(self):
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        gb_proc = QGroupBox("Procedures")
        gb_proc.setAlignment(Qt.AlignCenter)
        gb_proc.setSizePolicy(sizePolicy)
        WIDTH = 250
        # layproc = QGridLayout()
        layproc = QHBoxLayout()
        layproc_buttons = QVBoxLayout()
        # self.lv_proc = QListView()
        self.lv_proc = CustomListView()
        self.lv_proc.setFixedWidth(WIDTH)
        # self.cmb_proc.setSizePolicy(sizePolicy)

        self.cmb_proc = QComboBox()
        self.cmb_proc.setEditable(False)
        # self.cmb_proc.setInsertPolicy(QComboBox.InsertAlphabetically)
        self.cmb_proc.setFixedWidth(WIDTH)

        self.lv_proc_list = QListView()
        self.lv_proc_list.setFixedWidth(WIDTH)

        self.le_proc = QLineEdit()
        self.le_proc.setFixedWidth(WIDTH)

        self.le_proc_filter = QLineEdit()
        self.le_proc_filter.setFixedWidth(WIDTH)

        # self.cmb_proc.addItems(["Needling", "Head Amputation", "Prolotherapy"])
        self.pb_proc_add = QPushButton("Add")
        self.pb_proc_add.setFixedWidth(WIDTH)
        self.pb_proc_del = QPushButton("Delete")
        self.pb_proc_del.setFixedWidth(WIDTH)

        self.lb_proc_details = QLabel("Procedure Details")
        self.lb_proc_details.setAlignment(Qt.AlignCenter)
        self.te_proc_details = QTextEdit()
        # self.le_proc_details = QLineEdit()
        self.te_proc_details.setFixedWidth(WIDTH)
        # self.le_proc_details.setFixedWidth(WIDTH)
        self.pb_proc_add_details = QPushButton("Add Procedure Details")
        self.pb_proc_add_details.setFixedWidth(WIDTH)

        # layproc_buttons.addWidget(self.cmb_proc)
        layproc_buttons.addWidget(self.lv_proc_list)
        layproc_buttons.addWidget(self.le_proc_filter)
        layproc_buttons.addWidget(self.le_proc)
        layproc_buttons.addWidget(self.pb_proc_add)
        layproc_buttons.addWidget(self.pb_proc_del)
        layproc_buttons.addWidget(self.lb_proc_details)
        layproc_buttons.addWidget(self.te_proc_details)
        layproc_buttons.addWidget(self.pb_proc_add_details)
        layproc_buttons.addStretch()

        # layproc.addWidget(self.lv_proc, 0,0)
        layproc.addWidget(self.lv_proc)
        # layproc.addLayout(layproc_buttons, 0,1)
        layproc.addLayout(layproc_buttons)

        gb_proc.setLayout(layproc)
        return gb_proc

    def onCheckboxStateChanged(self, state):
        # Sender gives us the checkbox A that triggered the event
        checkboxA = self.sender()

        # Find the corresponding checkbox B using the dictionary
        for w in self.checkboxPairs.get(checkboxA):
            if isinstance(w, QCheckBox):
                if state == 0:  # If checkbox A is unchecked
                    w.setChecked(False)
                    w.setEnabled(False)
                else:  # If checkbox A is checked
                    w.setEnabled(True)
            elif isinstance(w, QLineEdit):
                if state == 0:  # If checkbox A is unchecked
                    w.setText("")
                    w.setEnabled(False)
                else:  # If checkbox A is checked
                    w.setEnabled(True)

    def isPositive(self, title, answer, layout, row, PAIN = False):
        hboxl = QHBoxLayout()
        hboxr = QHBoxLayout()
        cbl     = QCheckBox(title + ", L", self)
        cbl_pos = QCheckBox(answer)
        cbr     = QCheckBox(title + ", R", self)
        cbr_pos = QCheckBox(answer)
        hboxl.addWidget(cbl)
        hboxl.addWidget(cbl_pos)
        hboxr.addWidget(cbr)
        hboxr.addWidget(cbr_pos)
        if PAIN:
            cb_pain_l = QCheckBox("Painful", self)
            cb_pain_r = QCheckBox("Painful", self)
            hboxl.addWidget(cb_pain_l)
            hboxr.addWidget(cb_pain_r)
            self.checkboxPairs[cbl] = [cbl_pos, cb_pain_l]
            self.checkboxPairs[cbr] = [cbr_pos, cb_pain_r]
        else:
            self.checkboxPairs[cbl] = [cbl_pos]
            self.checkboxPairs[cbr] = [cbr_pos]

        # layout.addWidget(cbl, row , 0)
        # layout.addWidget(cbl_pos, row , 1)
        # layout.addWidget(cbr, row , 3)
        # layout.addWidget(cbr_pos, row , 4)

        # self.checkboxPairs[cbl] = [cbl_pos]
        # self.checkboxPairs[cbr] = [cbr_pos]
        cbl.stateChanged.connect(self.onCheckboxStateChanged)
        cbr.stateChanged.connect(self.onCheckboxStateChanged)
        layout.addLayout(hboxl, row, 0, 1,3)
        layout.addLayout(hboxr, row, 3, 1, 3)
        if PAIN:
            return layout, cbl, cbl_pos, cbr, cbr_pos, cb_pain_l, cb_pain_r
        else:
            return layout, cbl, cbl_pos, cbr, cbr_pos

    def add_cb_le(self, title, layout, row, col):
        cb     = QCheckBox(title, self)
        le = QLineEdit()
        layout.addWidget(cb, row , col)
        layout.addWidget(le, row , col+1, 1, 2)
        self.checkboxPairs[cb] = [le]
        cb.stateChanged.connect(self.onCheckboxStateChanged)
        return layout, cb, le


def allClear(widgets, active):
    for w in widgets:
        if w == active:
            w.setStyleSheet("""
            background-color: limegreen;
            border: 2px solid gray;
            border-radius: 10px;
            color: black;
            """)
        else:
            w.setStyleSheet("""
            background-color: lightgrey;
            border: 2px solid gray;
            border-radius: 10px;
            color: black;
            """)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = uiVisitForm()
    window.show()

    sys.exit(app.exec())
