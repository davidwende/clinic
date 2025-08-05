import sys
import os
from PySide6 import QtCore as qtc
from PySide6.QtCore import Qt
from PySide6 import QtWidgets as qtw
from PySide6.QtWidgets import QMessageBox, QCheckBox, QLineEdit
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PySide6 import QtGui as qtg

import error_codes
from Visits.UI.uiVisitsForm import uiVisitForm
from Database.dbFuncs import save_visit, get_visit_dates, get_visit, \
    get_all_procedures, visit_exists, delete_visit, get_all_diagnoses
import string
import datetime
from Reports import reports
from Config.config import header, tail, print_reports, users


class ListViewModel(qtc.QAbstractListModel):
    def __init__(self, entries = None):
        super().__init__()
        self.entries = entries or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            status, text = self.entries[index.row()]
            return text

    def rowCount(self, index):
        return len(self.entries)

    def clear(self):
        self.entries = []

class VisitForm(uiVisitForm):
    def __init__(self, tz, fname, surname, admin_mode):
        super().__init__()

        font = qtg.QFont()
        font.setStyleHint(qtg.QFont.TypeWriter)
        font.setFamily('monospace')

        self.admin_mode = admin_mode
        self.tz = tz
        self.fname = fname
        self.surname = surname
        self.alldiags = {}
        self.allprocs = {}
        self.visit_procs = {}
        self.visit_diags = {}
        self.print_content = ""
        self.lb_patient.setStyleSheet("border :2px solid black;")
        self.lb_patient.setText("Patient: {}   {} {}".format(self.tz, self.fname, self.surname))
        # self.le_patient.setEnabled(False)
        self.visit_date = None
        self.selected_diagnosis = None
        self.selected_procedure = None


        # Setup model for list view of procedures
        self.lv_model_proc = ListViewModel()
        self.lv_proc.setModel(self.lv_model_proc)
        # Setup model for combo box of procedures
        self.cmb_proc_model = ListViewModel()
        self.cmb_proc.setModel(self.cmb_proc_model)

        # Setup model for list view of diagnoses
        self.lv_model_diag = ListViewModel()
        self.lv_diag.setModel(self.lv_model_diag)
        # Setup model for combo box of diagnoses
        self.cmb_diag_model = ListViewModel()
        self.cmb_diag.setModel(self.cmb_diag_model)

        self.today = datetime.date.today().strftime("%Y %m %d")

        self.populate_dates()
        self.hip_pelvic_tilt = "Normal"
        self.populate_procedures()
        self.populate_diagnoses()
        self.s = ""

        self.cmb_proc.textActivated.connect(lambda text : self.le_proc.setText(text))
        self.pb_proc_add.clicked.connect(self.add_procedure)
        self.pb_proc_del.clicked.connect(self.delete_procedure)
        self.pb_proc_add_details.clicked.connect(self.add_procedure_details)

        self.cmb_diag.textActivated.connect(lambda text : self.le_diag.setText(text))
        self.pb_diag_add.clicked.connect(self.add_diagnosis)
        self.pb_diag_del.clicked.connect(self.delete_diagnosis)
        self.pb_diag_add_details.clicked.connect(self.add_diagnosis_details)
        # self.pb_diag_del_details.clicked.connect(self.delete_diagnosis_details)

        self.pb_save.clicked.connect(lambda : self.save_new_visit(self.pb_save))
        self.pb_clear.clicked.connect(self.clear_visit_form)
        self.pb_review.clicked.connect(self.review_summary)
        # self.pb_print_preview.clicked.connect(self.print_preview_dialog)
        self.pb_print.clicked.connect(self.print_summary)
        self.pb_cancel.clicked.connect(self.close)
        self.pb_delete.clicked.connect(self.delete)

        self.lv_diag.clicked.connect(self.show_diag_detail)
        self.lv_proc.clicked.connect(self.show_proc_detail)
        self.old_index = len(get_visit_dates(self.tz))
        self.cb_date.currentIndexChanged.connect(self.change_visit_date)
        self.bg_hip_pt.buttonClicked.connect(self.rb_hip_clicked)

        self.show()


    def show_diag_detail(self, idx):
        self.selected_diagnosis = idx.data()
        self.lb_diag_details.setText("Diagnosis Details: " + self.selected_diagnosis)
        diag_detail = self.visit_diags.get(idx.data(), "")
        print(idx.data(), diag_detail)
        self.te_diag_details.setText(diag_detail)

    def show_proc_detail(self, idx):
        self.selected_procedure = idx.data()
        self.lb_proc_details.setText("Procedure Details: " + self.selected_procedure)
        proc_detail = self.visit_procs.get(idx.data(), "")
        print(idx.data(), proc_detail)
        self.te_proc_details.setText(proc_detail)
        # self.le_proc_details.setText(proc_detail)

    def review_summary(self):
        print("Summary ", self.tz, self.visit_date)
        r = reports.Report(self.tz, self.visit_date, self.surname, self.fname)
        self.s = r.get_string()
        self.print_content = header + self.s + tail
        self.te_reports.setHtml(self.print_content)
        # print(self.print_content[670:690])


    def print_summary(self):
        # check if anything to print
        content = self.te_reports.toPlainText()
        if not content:
            QMessageBox.warning(self, "Print Summary",
                "You must create the report before printing!")
            return
        if "printer" == print_reports["printer"]:
            printer = QPrinter()
            printer.setResolution(600)
            printer.setOutputFileName("output.pdf")
            dialog = QPrintDialog(printer)
            res = dialog.exec_()
            print("from dialog got ", res)
            if res != 0:
                self.te_reports.print_(printer)
                QMessageBox.information(self, "Print Summary",
                    "The summary report was sent to the printer")
        elif "file" == print_reports["printer"]:
            filename = self.tz + "_" + str(self.visit_date) + ".html"
            fullfilename = os.path.join(print_reports['save_path'], filename)
            with open(fullfilename, 'w', encoding="utf-8") as file:
                file.write(self.print_content)
            QMessageBox.information(self, "Print Summary",
                   "The summary report was saved at "+fullfilename)

        # reports.write_pdf(self.s)
        a = """
            <html
            lang = "he">
            <head>
            <meta
            charset = "UTF-8" >
            <title > Page Layout Example </title>
            <style>
            .header
            {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10 px;
            }
            .logo
            {
                text-align: center;
            }
            .eng
            {
                direction: ltr;
            }
            .heb
            {
                direction: rtl;
            }
        </style>
        </head>
        <body>
            <div >
            <img src = "file:///home/dwende/clinic/logo_small.png"
            alt = "Logo">
            </div>
        <div class ="header">
            <div class ="eng">
            <p> Dr Osnat Wende
            <br> 
            Specialist in Pain Relief Medicine
            <br> Area of interest: Musculoskeletal Medicine
            <br> 44 Choshen St., Mevaseret Zion
            <br> 053-431-5551 
            </p>
            </div>
        <div class ="heb">
        <p>
דר אסנת וונדי        
        <br>
        מומחית לשיכוך כאב
        <br>
        תחום ענין: רפואת שריר שלד
         <br>
רח" החושן 44, מבשרת ציון
<br>
053-431-5551      
        </p>
        </div>
        </div>
        </body>
        </html>"""


    def delete(self):
        # First check if today
        print(self.admin_mode)
        print(self.visit_date, datetime.date.today())
        if self.admin_mode != "admin" and self.visit_date != datetime.date.today():
            QMessageBox.warning(self, "Delete Visit", "You can delete a visit ONLY from today!")
        else:
            msgBox = QMessageBox(self)
            msgBox.setText("Are you sure about deleting todays' visit?")
            msgBox.setStandardButtons(QMessageBox.Cancel  | QMessageBox.Ok )
            ret = msgBox.exec()
            if ret == QMessageBox.Ok:
                # if error_codes.ERR_OK == delete_visit(self.tz, datetime.date.today()):
                if error_codes.ERR_OK == delete_visit(self.tz, self.visit_date):
                    QMessageBox.information(self, "Delete Visit", "Todays' visit was deleted")
                    self.clear_visit_form()
                else:
                    QMessageBox.information(self, "Delete Visit", "Visit could not be deleted")

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
        self.show_visit(new_value)

    def populate_procedures(self):
        allprocs = get_all_procedures()
        for proc in allprocs:
            self.cmb_proc_model.entries.append((False, proc))
        self.cmb_proc_model.layoutAboutToBeChanged.emit()
        self.cmb_proc_model.layoutChanged.emit()
        
    def populate_diagnoses(self):
        alldiags = dict(get_all_diagnoses())
        for diag in alldiags:
            self.cmb_diag_model.entries.append((False, diag))
        self.cmb_diag_model.layoutAboutToBeChanged.emit()
        self.cmb_diag_model.layoutChanged.emit()

    def rb_hip_clicked(self, button):
        self.hip_pelvic_tilt = f"{button.text()}"

    def populate_dates(self):
        dates = get_visit_dates(self.tz)
        dates = [date.strftime("%Y %m %d") for date in dates]
        self.cb_date.addItems(dates)
        if not dates or self.today != dates[-1]:
            self.cb_date.addItem(self.today)
        self.cb_date.setCurrentIndex(self.cb_date.count() -  1)
        self.show_visit(self.today)

    def show_visit(self, d):
        self.clear_visit_form()
        year, month, day = d.split()
        self.visit_date = datetime.date(int(year), int(month), int(day))
        if visit_exists(self.tz, self.visit_date):
            v, procs, diags = get_visit(self.tz, self.visit_date)
            # === cc ===
            self.le_onset.setText                       ( v.cc_onset      )
            self.te_description.setPlainText(v.cc_description)
            self.cb_cc_walking.setChecked                   ( v.cc_walking )
            self.le_cc_walking.setText                 ( v.cc_walking_le)
            self.cb_cc_standing.setChecked              ( v.cc_standing   )
            self.le_cc_standing.setText                 ( v.cc_standing_le)
            self.cb_cc_sitting.setChecked               ( v.cc_sitting    )
            self.le_cc_sitting.setText                  ( v.cc_sitting_le )
            self.cb_cc_lying.setChecked                 ( v.cc_lying      )
            self.le_cc_lying.setText                    ( v.cc_lying_le   )
            self.cb_cc_lifting.setChecked               ( v.cc_lifting      )
            self.le_cc_lifting.setText                  ( v.cc_lifting_le   )
            self.cb_cc_shoulder_move.setChecked         ( v.cc_shoulder_move      )
            self.le_cc_shoulder_move.setText            ( v.cc_shoulder_move_le   )

            # print("getting neck loc as ", v.cc_loc_neck)
            self.cb_loc_neck.setChecked                 ( v.cc_loc_neck     )
            self.cb_loc_spine.setChecked                ( v.cc_loc_spine )
            self.cb_loc_back.setChecked                 ( v.cc_loc_back        )
            self.cb_loc_shoulder_l.setChecked           ( v.cc_loc_shoulder_l )
            self.cb_loc_shoulder_r.setChecked           ( v.cc_loc_shoulder_r )
            self.cb_loc_hip_l.setChecked                ( v.cc_loc_hips_l     )
            self.cb_loc_hip_r.setChecked                ( v.cc_loc_hips_r     )
            self.cb_loc_groin_l.setChecked              ( v.cc_loc_groin_l)
            self.cb_loc_groin_r.setChecked              ( v.cc_loc_groin_r)
            self.cb_loc_knee_l.setChecked               ( v.cc_loc_knee_l )
            self.cb_loc_knee_r.setChecked               ( v.cc_loc_knee_r )
            self.cb_loc_ankle_l.setChecked              ( v.cc_loc_ankle_l )
            self.cb_loc_ankle_r.setChecked              ( v.cc_loc_ankle_r )
            self.cb_loc_other.setChecked                ( v.cc_loc_other   )
            self.le_loc_radiates.setText                ( v.cc_loc_radiates_le)
            self.le_loc_precise.setText                ( v.cc_loc_precise_le)

            # back 0
            self.le_back_movement.setText               (v.back_movement_le)
            self.cb_trend_l.setChecked                  ( v.back_trend_l          )
            self.cb_trend_l_pos.setChecked              ( v.back_trend_r          )
            self.cb_trend_r.setChecked                  ( v.back_trend_l_pos      )
            self.cb_trend_r_pos.setChecked              ( v.back_trend_r_pos      )
            self.le_slr_l_le.setText                    ( v.back_slr_l_le         )
            self.le_slr_r_le.setText                    ( v.back_slr_r_le         )

            self.cb_fst_l.setChecked                    ( v.back_fst_l         )
            self.cb_fst_r.setChecked                    ( v.back_fst_r         )
            self.cb_fst_l_pos.setChecked                    ( v.back_fst_l_pos         )
            self.cb_fst_r_pos.setChecked                    ( v.back_fst_r_pos         )

            self.cb_phf_l.setChecked                    ( v.back_hip_l            )
            self.cb_phf_l_pos.setChecked                ( v.back_hip_l_pain       )
            self.cb_phf_r.setChecked                    ( v.back_hip_r            )
            self.cb_phf_r_pos.setChecked                ( v.back_hip_r_pain       )
            self.cb_tt_l.setChecked                     ( v.back_thigh_l          )
            self.cb_tt_l_pos.setChecked                 ( v.back_thigh_l_pos      )
            self.cb_tt_r.setChecked                     ( v.back_thigh_r          )
            self.cb_tt_r_pos.setChecked                 ( v.back_thigh_r_pos      )
            self.cb_Fabere_l.setChecked                 ( v.back_fabere_l         )
            self.cb_Fabere_l_pos.setChecked             ( v.back_fabere_l_pos     )
            self.cb_Fabere_r.setChecked                 ( v.back_fabere_r         )
            self.cb_Fabere_r_pos.setChecked             ( v.back_fabere_r_pos     )
            self.cb_Sensation.setChecked                ( v.back_sensation        )
            self.cb_Sensation_equals.setChecked         ( v.back_sensation_equals )
            self.le_Sensation.setText                   ( v.back_sensation_le     )
            self.cb_power.setChecked                    ( v.back_power            )
            self.cb_power_equals.setChecked             ( v.back_power_equals     )
            self.le_power.setText                       ( v.back_power_le         )
            self.cb_reflexes.setChecked                 ( v.back_reflexes         )
            self.cb_reflexes_equals.setChecked          ( v.back_reflexes_equals  )
            self.le_reflexes.setText                    ( v.back_reflexes_le      )

            self.cb_back_tspine_rot_l.setChecked(v.back_tspine_rot_l)
            self.cb_back_tspine_rot_l_pain.setChecked(v.back_tspine_rot_l_pain)
            self.cb_back_tspine_rot_r.setChecked(v.back_tspine_rot_r)
            self.cb_back_tspine_rot_r_pain.setChecked(v.back_tspine_rot_r_pain)
            self.le_back_tspine_rot_tender.setText(v.back_tspine_tender_le)

            self.cb_bhip_abd_l.setChecked               ( v.back_abduction_l      )
            self.cb_bhip_abd_pos_l.setChecked           ( v.back_abduction_l_pos  )
            self.cb_bhip_abd_r.setChecked               ( v.back_abduction_r      )
            self.cb_bhip_abd_pos_r.setChecked           ( v.back_abduction_r_pos  )
            self.cb_bhip_lrot_l.setChecked              ( v.back_lat_rot_l        )
            self.cb_bhip_lrot_pos_l.setChecked          ( v.back_lat_rot_l_pos    )
            self.cb_bhip_lrot_r.setChecked              ( v.back_lat_rot_r        )
            self.cb_bhip_lrot_pos_r.setChecked          ( v.back_lat_rot_r_pos    )
            self.cb_bhip_add_l.setChecked               ( v.back_adduction_l      )
            self.cb_bhip_add_pos_l.setChecked           ( v.back_adduction_l_pos  )
            self.cb_bhip_add_r.setChecked               ( v.back_adduction_r      )
            self.cb_bhip_add_pos_r.setChecked           ( v.back_adduction_r_pos  )
            self.cb_bhip_flex_l.setChecked              ( v.back_flexion_l        )
            self.cb_bhip_flex_pos_l.setChecked          ( v.back_flexion_l_pos    )
            self.cb_bhip_flex_r.setChecked              ( v.back_flexion_r        )
            self.cb_bhip_flex_pos_r.setChecked          ( v.back_flexion_r_pos    )
            self.le_bhip_tender.setText                 ( v.back_tenderness_le    )
            # ankle 0
            self.cb_ankle_scar_l.setChecked             ( v.ankle_scar_l          )
            self.cb_ankle_scar_pos_l.setChecked         ( v.ankle_scar_l_yes      )
            self.cb_ankle_scar_r.setChecked             ( v.ankle_scar_r          )
            self.cb_ankle_scar_pos_r.setChecked         ( v.ankle_scar_r_yes      )
            self.cb_ankle_align_l.setChecked            ( v.ankle_align_l         )
            self.rb_ankle_pronate_l.setChecked          ( v.ankle_align_l_pronated)
            self.rb_ankle_supinate_l.setChecked         (not v.ankle_align_l_pronated)
            self.cb_ankle_align_r.setChecked            ( v.ankle_align_r         )
            self.rb_ankle_pronate_r.setChecked          ( v.ankle_align_r_pronated)
            self.rb_ankle_supinate_r.setChecked         (not v.ankle_align_r_pronated)
            self.le_ankle_dors_l.setText                ( v.ankle_dors_l_le       )
            self.le_ankle_dors_r.setText                ( v.ankle_dors_r_le       )
            self.le_ankle_plant_l.setText               ( v.ankle_plant_l_le      )
            self.le_ankle_plant_r.setText               ( v.ankle_plant_r_le      )
            self.le_ankle_inversion_l.setText               ( v.ankle_inversion_l_le      )
            self.le_ankle_inversion_r.setText               ( v.ankle_inversion_r_le      )
            self.le_ankle_eversion_l.setText               ( v.ankle_eversion_l_le      )
            self.le_ankle_tender_l.setText               ( v.ankle_tender_le_l      )
            self.le_ankle_tender_r.setText               ( v.ankle_tender_le_r      )

            # ankle st
            self.cb_anklest_addpain_l.setChecked        ( v.anklest_addpain_l        )
            self.cb_anklest_addpain_pos_l.setChecked    ( v.anklest_addpain_yes_l    )
            self.cb_anklest_addpain_pos_l.setEnabled    ( v.anklest_addpain_l    )

            self.cb_anklest_addpain_r.setChecked        ( v.anklest_addpain_r        )
            self.cb_anklest_addpain_pos_r.setChecked    ( v.anklest_addpain_yes_r    )
            self.cb_anklest_abcpain_l.setChecked        ( v.anklest_abcpain_l        )
            self.cb_anklest_abcpain_pos_l.setChecked    ( v.anklest_abcpain_yes_l    )
            self.cb_anklest_abcpain_r.setChecked        ( v.anklest_abcpain_r        )
            self.cb_anklest_abcpain_pos_r.setChecked    ( v.anklest_abcpain_yes_r    )
            self.cb_anklest_addlimited_l.setChecked     ( v.anklest_addlimited_l     )
            self.cb_anklest_addlimited_pos_l.setChecked ( v.anklest_addlimited_yes_l )
            self.cb_anklest_addlimited_r.setChecked     ( v.anklest_addlimited_r     )
            self.cb_anklest_addlimited_pos_r.setChecked ( v.anklest_addlimited_yes_r )
            self.cb_anklest_abclimited_l.setChecked     ( v.anklest_abclimited_l     )
            self.cb_anklest_abclimited_pos_l.setChecked ( v.anklest_abclimited_yes_l )
            self.cb_anklest_abclimited_r.setChecked     ( v.anklest_abclimited_r     )
            self.cb_anklest_abclimited_pos_r.setChecked ( v.anklest_abclimited_yes_r )
            # knee
            self.cb_knee_scar_l.setChecked              ( v.knee_scar_l           )
            self.cb_knee_scar_pos_l.setChecked          ( v.knee_scar_l_yes       )
            self.cb_knee_scar_r.setChecked              ( v.knee_scar_r           )
            self.cb_knee_scar_pos_r.setChecked          ( v.knee_scar_r_yes       )
            self.cb_knee_align_l.setChecked             ( v.knee_align_l          )
            self.cb_knee_align_pos_l.setChecked         ( v.knee_align_l_ab       )
            self.le_knee_align_no_l.setText(v.knee_align_l_le)
            self.le_knee_align_no_r.setText(v.knee_align_r_le)

            self.cb_knee_align_r.setChecked             ( v.knee_align_r          )
            self.cb_knee_align_pos_r.setChecked         ( v.knee_align_r_ab       )
            self.cb_knee_muscle_l.setChecked            ( v.knee_muscle_l         )
            self.cb_knee_muscle_pos_l.setChecked        ( v.knee_muscle_l_yes     )
            self.cb_knee_muscle_r.setChecked            ( v.knee_muscle_r         )
            self.cb_knee_muscle_pos_r.setChecked        ( v.knee_muscle_r_yes     )
            self.cb_knee_effusion_l.setChecked          ( v.knee_effusion_l       )
            self.cb_knee_effusion_pos_l.setChecked      ( v.knee_effusion_l_yes   )
            self.cb_knee_effusion_r.setChecked          ( v.knee_effusion_r       )
            self.cb_knee_effusion_pos_r.setChecked      ( v.knee_effusion_r_yes   )
            self.cb_knee_rext_l.setChecked              (v.knee_res_ext_l         )
            self.cb_knee_rext_pos_l.setChecked          (v.knee_res_ext_l_yes     )
            self.cb_knee_rext_r.setChecked              (v.knee_res_ext_r         )
            self.cb_knee_rext_pos_r.setChecked          (v.knee_res_ext_r_yes     )
            self.cb_knee_rflex_l.setChecked             (v.knee_res_flexion_l     )
            self.cb_knee_rflex_pos_l.setChecked         (v.knee_res_flexion_l_yes )
            self.cb_knee_rflex_r.setChecked             (v.knee_res_flexion_r     )
            self.cb_knee_rflex_pos_r.setChecked         (v.knee_res_flexion_r_yes )
            self.cb_knee_mm_l.setChecked                (v.knee_macmurray_l       )
            self.cb_knee_mm_pos_l.setChecked            (v.knee_macmurray_l_pos   )
            self.cb_knee_mm_r.setChecked                (v.knee_macmurray_r       )
            self.cb_knee_mm_pos_r.setChecked            (v.knee_macmurray_r_pos   )
            self.cb_knee_pfg_l.setChecked               (v.knee_grind_l           )
            self.cb_knee_pfg_pos_l.setChecked           (v.knee_grind_l_pos       )
            self.cb_knee_pfg_r.setChecked               (v.knee_grind_r           )
            self.cb_knee_pfg_pos_r.setChecked           (v.knee_grind_r_pos       )
            self.le_knee_rom_l.setText                  (v.knee_rom_l             )
            self.le_knee_rom_r.setText                  (v.knee_rom_r             )
            self.cb_knee_mcl_l.setChecked               (v.knee_mcl_l             )
            self.cb_knee_mcl_lax_l.setChecked           (v.knee_mcl_lax_l         )
            self.cb_knee_mcl_r.setChecked               (v.knee_mcl_r             )
            self.cb_knee_mcl_lax_r.setChecked           (v.knee_mcl_lax_r         )
            self.cb_knee_lcl_l.setChecked               (v.knee_lcl_l             )
            self.cb_knee_lcl_lax_l.setChecked           (v.knee_lcl_lax_l         )
            self.cb_knee_lcl_r.setChecked               (v.knee_lcl_r             )
            self.cb_knee_lcl_lax_r.setChecked           (v.knee_lcl_lax_r         )
            self.le_knee_l_tender.setText               (v.knee_tender_l_le       )
            self.le_knee_r_tender.setText               (v.knee_tender_r_le       )
            self.le_knee_other.setText               (v.knee_other_le       )
            # hip 0
            self.cb_hip_pt.setChecked                   ( v.hip_pelvic_tilt               )
            self.rb_hip_pt_normal.setChecked              ( "Normal" == v.hip_pelvic_tilt_type)
            self.rb_hip_pt_posterior.setChecked           ( "Posterior" == v.hip_pelvic_tilt_type)
            self.rb_hip_pt_anterior.setChecked            ( "Anterior" == v.hip_pelvic_tilt_type)

            self.cb_hip_trend_l.setChecked              ( v.hip_trend_l                   )
            self.cb_hip_trend_l_pos.setChecked          ( v.hip_trend_r                   )
            self.cb_hip_trend_r.setChecked              ( v.hip_trend_l_pos               )
            self.cb_hip_trend_r_pos.setChecked          ( v.hip_trend_r_pos               )
            # passive
            self.le_hip_lrot_l_pos.setText              ( v.hip_passive_lat_rot_l_le      )
            self.le_hip_lrot_r_pos.setText              ( v.hip_passive_lat_rot_r_le      )
            self.le_hip_mrot_l_pos.setText              ( v.hip_passive_medial_rot_l_le      )
            self.le_hip_mrot_r_pos.setText              ( v.hip_passive_medial_rot_r_le      )
            self.le_hip_flex_l_pos.setText              ( v.hip_passive_flexion_l_le      )
            self.le_hip_flex_r_pos.setText              ( v.hip_passive_flexion_r_le      )
            #
            #
            # self.le_hip_abd_l.setText                   ( v.hip_resisted_abduction_l_le   )
            # self.le_hip_abd_r.setText                   ( v.hip_resisted_abduction_r_le   )
            # self.le_hip_rlrot_l.setText                 ( v.hip_resisted_lat_rot_l_le     )
            # self.le_hip_rlrot_r.setText                 ( v.hip_resisted_lat_rot_r_le     )


            self.cb_hip_abd_l.setChecked              ( v.hip_resisted_abd_l        )
            self.cb_hip_abd_l_painful   .setChecked   ( v.hip_resisted_abd_l_limit  )
            self.cb_hip_abd_r.setChecked              ( v.hip_resisted_abd_r        )
            self.cb_hip_abd_r_painful.setChecked      ( v.hip_resisted_abd_r_limit  )
            # resisted
            self.cb_hip_rlrot_l.setChecked              ( v.hip_resisted_lat_rot_l        )
            self.cb_hip_rlrot_l_painful   .setChecked   ( v.hip_resisted_lat_rot_l_limit  )
            self.cb_hip_rlrot_r.setChecked              ( v.hip_resisted_lat_rot_r        )
            self.cb_hip_rlrot_r_painful.setChecked      ( v.hip_resisted_lat_rot_r_limit  )

            self.cb_hip_rmrot_l.setChecked              ( v.hip_resisted_med_rot_l        )
            self.cb_hip_rmrot_l_painful   .setChecked        ( v.hip_resisted_med_rot_l_limit  )
            self.cb_hip_rmrot_r.setChecked              ( v.hip_resisted_med_rot_r        )
            self.cb_hip_rmrot_r_painful.setChecked        ( v.hip_resisted_med_rot_r_limit  )
            self.cb_hip_radd_l.setChecked               ( v.hip_resisted_adduction_l      )
            self.cb_hip_radd_l_painful.setChecked         ( v.hip_resisted_adduction_l_limit)
            self.cb_hip_radd_r.setChecked               ( v.hip_resisted_adduction_r      )
            self.cb_hip_radd_r_painful.setChecked         ( v.hip_resisted_adduction_r_limit)
            self.le_hip_tenderness.setText              ( v.hip_tenderness                )
            self.le_hip_other.setText                   ( v.hip_other                     )
            # neck 0
            self.le_neck_ext.setText                    ( v.neck_extension_le    )
            self.le_neck_rot_l.setText                  ( v.neck_rotation_l_le   )
            self.le_neck_rot_r.setText                  ( v.neck_rotation_r_le   )
            self.le_neck_cranial.setText                ( v.neck_cranial_le      )
            # neck 4
            self.cb_neck_sen.setChecked                 ( v.neck_sensation       )
            self.cb_neck_sen_equals.setChecked          ( v.neck_sensation_equals)
            self.le_neck_sen.setText                    ( v.neck_sensation_le    )
            # neck 7
            self.cb_neck_power.setChecked               ( v.neck_power        )
            self.cb_neck_power_equals.setChecked        ( v.neck_power_equals        )
            self.le_neck_power.setText                  ( v.neck_power_le        )
            # neck 10
            self.cb_neck_reflexes.setChecked            ( v.neck_reflexes     )
            self.cb_neck_reflexes_equals.setChecked     ( v.neck_reflexes_equals     )
            self.le_neck_tender.setText                 ( v.neck_tenderness_le   )
            self.le_neck_other.setText                 ( v.neck_other_le   )

            # shoulder 0
            self.cb_sh_align_l.setChecked               ( v.shoulder_align_l                    )
            self.cb_sh_align_ab_l.setChecked            ( v.shoulder_align_l_ab                 )
            self.le_sh_align_l.setText                  ( v.shoulder_align_l_le                 )
            self.cb_sh_align_l.setChecked               ( v.shoulder_align_r                    )
            self.cb_sh_align_ab_l.setChecked            ( v.shoulder_align_r_ab                 )
            self.le_sh_align_l.setText                  ( v.shoulder_align_r_le                 )
            self.cb_sh_rom_l.setChecked                 ( v.shoulder_rom_l                      )
            self.rb_sh_rom_full_l.setChecked            ( v.shoulder_rom_l_full                 )
            self.rb_sh_rom_limit_l.setChecked            (not v.shoulder_rom_l_full                 )
            self.cb_sh_rom_r.setChecked                 ( v.shoulder_rom_r                      )
            self.rb_sh_rom_full_r.setChecked            ( v.shoulder_rom_r_full                 )
            self.rb_sh_rom_limit_r.setChecked            (not v.shoulder_rom_r_full                 )
            self.le_sh_abd_l.setText                    ( v.shoulder_passive_abduction_l_le     )
            self.le_sh_abd_r.setText                    ( v.shoulder_passive_abduction_r_le     )
            self.le_sh_lrot_l.setText                   ( v.shoulder_passive_lat_rot_l_le       )
            self.le_sh_lrot_r.setText                   ( v.shoulder_passive_lat_rot_r_le       )

            self.cb_sh_mrot_l.setChecked                ( v.shoulder_passive_med_rot_l          )
            self.cb_sh_mrot_limit_l.setChecked          ( v.shoulder_passive_med_rot_l_limit    )
            self.cb_sh_mrot_pain_l.setChecked          ( v.shoulder_passive_med_rot_l_pain    )
            self.cb_sh_mrot_r.setChecked                ( v.shoulder_passive_med_rot_r          )
            self.cb_sh_mrot_limit_r.setChecked          ( v.shoulder_passive_med_rot_r_limit    )
            self.cb_sh_mrot_pain_r.setChecked          ( v.shoulder_passive_med_rot_r_pain    )

            self.cb_sh_add_l.setChecked                 ( v.shoulder_passive_adduction_l        )
            self.cb_sh_add_limit_l.setChecked           ( v.shoulder_passive_adduction_l_limit  )
            self.cb_sh_add_pain_l.setChecked           ( v.shoulder_passive_adduction_l_pain  )
            self.cb_sh_add_r.setChecked                 ( v.shoulder_passive_adduction_r        )
            self.cb_sh_add_limit_r.setChecked           ( v.shoulder_passive_adduction_r_limit  )
            self.cb_sh_add_pain_r.setChecked           ( v.shoulder_passive_adduction_r_pain  )

            self.le_sh_res_abd_l.setText                ( v.shoulder_resisted_abduction_l_le    )
            self.le_sh_res_abd_r.setText                ( v.shoulder_resisted_abduction_r_le    )
            self.le_sh_res_lrot_l.setText               ( v.shoulder_resisted_lat_rot_l_le      )
            self.le_sh_res_lrot_r.setText               ( v.shoulder_resisted_lat_rot_r_le      )
            self.cb_sh_res_mrot_l.setChecked            ( v.shoulder_resisted_med_rot_l         )
            self.cb_sh_res_mrot_painful_l.setChecked      ( v.shoulder_resisted_med_rot_l_limit   )
            self.cb_sh_res_mrot_r.setChecked            ( v.shoulder_resisted_med_rot_r         )
            self.cb_sh_res_mrot_painful_r.setChecked      ( v.shoulder_resisted_med_rot_r_limit   )
            self.cb_sh_res_add_l.setChecked             ( v.shoulder_resisted_adduction_l       )
            self.cb_sh_res_add_painful_l.setChecked       ( v.shoulder_resisted_adduction_l_limit )
            self.cb_sh_res_add_r.setChecked             ( v.shoulder_resisted_adduction_r       )
            self.cb_sh_res_add_painful_r.setChecked       ( v.shoulder_resisted_adduction_r_limit )

            self.cb_sh_res_jobes_l.setChecked(v.shoulder_jobes_l)
            self.cb_sh_res_jobes_pos_l.setChecked(v.shoulder_jobes_l_pos)
            self.cb_sh_res_jobes_r.setChecked(v.shoulder_jobes_r)
            self.cb_sh_res_jobes_pos_r.setChecked(v.shoulder_jobes_r_pos)

            self.te_exam.setPlainText                   (v.examination)
            self.te_recommend.setPlainText               (v.recommendation)
            self.te_tests.setPlainText               (v.tests)
            self.lv_model_proc.entries.clear()
            self.lv_model_diag.entries.clear()

            self.visit_procs = dict(procs)
            self.visit_diags = dict(diags)
            for proc in self.visit_procs:
                self.lv_model_proc.entries.append((False, proc))
                self.lv_model_proc.layoutAboutToBeChanged.emit()
                self.lv_model_proc.layoutChanged.emit()
            for diag in self.visit_diags:
                self.lv_model_diag.entries.append((False, diag))
                self.lv_model_diag.layoutAboutToBeChanged.emit()
                self.lv_model_diag.layoutChanged.emit()
            # now set enabled according to parent
            for cb in self.checkboxPairs:
                state = cb.isChecked()
                for w in self.checkboxPairs.get(cb):
                    if isinstance(w, QCheckBox):
                        if not state:
                            w.setChecked(False)
                            w.setEnabled(False)
                        else:
                            w.setEnabled(True)
                    elif isinstance(w, QLineEdit):
                        if not state:  # If checkbox A is unchecked
                            w.setText("")
                            w.setEnabled(False)
                        else:  # If checkbox A is checked
                            w.setEnabled(True)

    @qtc.Slot()
    def save_new_visit(self, button):
        if self.visit_date != datetime.date.today():
            QMessageBox.information(self, "Save", "You can Save/Modify a Visit only from today!")
            return

        msgBox = QMessageBox(self)
        msgBox.setText("You requested to save this visit data from {}".format(self.visit_date))
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = msgBox.exec()
        if QMessageBox.Ok == ret:
            print("Saving or Modifying Visit ======")
            cc, loc, back, knee, ankle, anklest,  hip = [], [], [], [], [], [], []
            neck, shoulder, exam, recommend, tests = [], [], [], [], []
            cc.append(self.le_onset.text())
            cc.append(self.te_description.toPlainText())
            cc.append(self.cb_cc_walking.isChecked())
            cc.append(self.le_cc_walking.text())
            cc.append(self.cb_cc_standing.isChecked())
            cc.append(self.le_cc_standing.text())
            cc.append(self.cb_cc_sitting.isChecked())
            cc.append(self.le_cc_sitting.text())
            cc.append(self.cb_cc_lying.isChecked())
            cc.append(self.le_cc_lying.text())
            cc.append(self.cb_cc_lifting.isChecked())
            cc.append(self.le_cc_lifting.text())
            cc.append(self.cb_cc_shoulder_move.isChecked())
            cc.append(self.le_cc_shoulder_move.text())
            # Location 0
            loc.append(self.cb_loc_neck.isChecked())
            loc.append(self.cb_loc_spine.isChecked())
            loc.append(self.cb_loc_back.isChecked())
            loc.append(self.cb_loc_shoulder_l.isChecked())
            loc.append(self.cb_loc_shoulder_r.isChecked())
            # Location 5
            loc.append(self.cb_loc_hip_l.isChecked())
            loc.append(self.cb_loc_hip_r.isChecked())
            # Location 7
            loc.append(self.cb_loc_groin_l.isChecked())
            loc.append(self.cb_loc_groin_r.isChecked())
            loc.append(self.cb_loc_knee_l.isChecked())
            loc.append(self.cb_loc_knee_r.isChecked())
            # Location 11
            loc.append(self.cb_loc_ankle_l.isChecked())
            loc.append(self.cb_loc_ankle_r.isChecked())
            loc.append(self.cb_loc_other.isChecked())
            loc.append(self.le_loc_radiates.text())
            loc.append(self.le_loc_precise.text())

            # back 0
            back.append(self.cb_trend_l.isChecked())
            back.append(self.cb_trend_l_pos.isChecked())
            back.append(self.cb_trend_r.isChecked())
            back.append(self.cb_trend_r_pos.isChecked())
            # back 4
            back.append(self.le_slr_l_le.text())
            back.append(self.le_slr_r_le.text())
            # back 6
            back.append(self.cb_phf_l.isChecked())
            back.append(self.cb_phf_l_pos.isChecked())
            back.append(self.cb_phf_r.isChecked())
            back.append(self.cb_phf_r_pos.isChecked())
            # back 10
            back.append(self.cb_tt_l.isChecked())
            back.append(self.cb_tt_l_pos.isChecked())
            back.append(self.cb_tt_r.isChecked())
            back.append(self.cb_tt_r_pos.isChecked())
            # back 14
            back.append(self.cb_Fabere_l.isChecked())
            back.append(self.cb_Fabere_l_pos.isChecked())
            back.append(self.cb_Fabere_r.isChecked())
            back.append(self.cb_Fabere_r_pos.isChecked())
            # back 18
            back.append(self.cb_Sensation.isChecked())
            back.append(self.cb_Sensation_equals.isChecked())
            back.append(self.le_Sensation.text())
            # back 21
            back.append(self.cb_power.isChecked())
            back.append(self.cb_power_equals.isChecked())
            back.append(self.le_power.text())
            # back 24
            back.append(self.cb_reflexes.isChecked())
            back.append(self.cb_reflexes_equals.isChecked())
            back.append(self.le_reflexes.text())
            # Back - resisted hip
            # back 27
            back.append(self.cb_bhip_abd_l.isChecked())
            back.append(self.cb_bhip_abd_pos_l.isChecked())
            back.append(self.cb_bhip_abd_r.isChecked())
            back.append(self.cb_bhip_abd_pos_r.isChecked())
            # back 31
            back.append(self.cb_bhip_lrot_l.isChecked())
            back.append(self.cb_bhip_lrot_pos_l.isChecked())
            back.append(self.cb_bhip_lrot_r.isChecked())
            back.append(self.cb_bhip_lrot_pos_r.isChecked())
            # back 35
            back.append(self.cb_bhip_add_l.isChecked())
            back.append(self.cb_bhip_add_pos_l.isChecked())
            back.append(self.cb_bhip_add_r.isChecked())
            back.append(self.cb_bhip_add_pos_r.isChecked())
            # back 39
            back.append(self.cb_bhip_flex_l.isChecked())
            back.append(self.cb_bhip_flex_pos_l.isChecked())
            back.append(self.cb_bhip_flex_r.isChecked())
            back.append(self.cb_bhip_flex_pos_r.isChecked())
            # back 43
            back.append(self.le_bhip_tender.text())
            # back 44 thoracic spine
            back.append(self.cb_back_tspine_rot_l.isChecked())
            back.append(self.cb_back_tspine_rot_l_pain.isChecked())
            back.append(self.cb_back_tspine_rot_r.isChecked())
            back.append(self.cb_back_tspine_rot_r_pain.isChecked())
            back.append(self.le_back_tspine_rot_tender.text())
            # additions May 2024
            # back 49
            back.append(self.le_back_movement.text())
            # back 50
            back.append(self.cb_fst_l.isChecked())
            back.append(self.cb_fst_l_pos.isChecked())
            back.append(self.cb_fst_r.isChecked())
            back.append(self.cb_fst_r_pos.isChecked())

            # ankle 0
            ankle.append(self.cb_ankle_scar_l.isChecked())
            ankle.append(self.cb_ankle_scar_pos_l.isChecked())
            ankle.append(self.cb_ankle_scar_r.isChecked())
            ankle.append(self.cb_ankle_scar_pos_r.isChecked())
            # ankle 4
            ankle.append(self.cb_ankle_align_l.isChecked())
            ankle.append(self.rb_ankle_pronate_l.isChecked())
            ankle.append(self.cb_ankle_align_r.isChecked())
            ankle.append(self.rb_ankle_pronate_r.isChecked())
            # ankle 8
            ankle.append(self.le_ankle_dors_l.text())
            ankle.append(self.le_ankle_dors_r.text())
            ankle.append(self.le_ankle_plant_l.text())
            ankle.append(self.le_ankle_plant_r.text())
            ankle.append(self.le_ankle_inversion_l.text())
            ankle.append(self.le_ankle_inversion_r.text())
            ankle.append(self.le_ankle_eversion_l.text())
            ankle.append(self.le_ankle_eversion_r.text())
            # ankle 16
            ankle.append(self.le_ankle_tender_l.text())
            ankle.append(self.le_ankle_tender_r.text())

            # anklest 0
            anklest.append(self.cb_anklest_addpain_l.isChecked())
            anklest.append(self.cb_anklest_addpain_pos_l.isChecked())
            anklest.append(self.cb_anklest_addpain_r.isChecked())
            anklest.append(self.cb_anklest_addpain_pos_r.isChecked())
            # ankle 4           cb
            anklest.append(self.cb_anklest_abcpain_l.isChecked())
            anklest.append(self.cb_anklest_abcpain_pos_l.isChecked())
            anklest.append(self.cb_anklest_abcpain_r.isChecked())
            anklest.append(self.cb_anklest_abcpain_pos_r.isChecked())
            # ankle 8           cb
            anklest.append(self.cb_anklest_addlimited_l.isChecked())
            anklest.append(self.cb_anklest_addlimited_pos_l.isChecked())
            anklest.append(self.cb_anklest_addlimited_r.isChecked())
            anklest.append(self.cb_anklest_addlimited_pos_r.isChecked())
            # ankle 12          cb
            anklest.append(self.cb_anklest_abclimited_l.isChecked())
            anklest.append(self.cb_anklest_abclimited_pos_l.isChecked())
            anklest.append(self.cb_anklest_abclimited_r.isChecked())
            anklest.append(self.cb_anklest_abclimited_pos_r.isChecked())
            # knee 0
            knee.append(self.cb_knee_scar_l.isChecked())
            knee.append(self.cb_knee_scar_pos_l.isChecked())
            knee.append(self.cb_knee_scar_r.isChecked())
            knee.append(self.cb_knee_scar_pos_r.isChecked())
            # knee 4
            knee.append(self.cb_knee_align_l.isChecked())
            knee.append(self.cb_knee_align_pos_l.isChecked())
            knee.append(self.le_knee_align_no_l.text())
            knee.append(self.cb_knee_align_r.isChecked())
            knee.append(self.cb_knee_align_pos_r.isChecked())
            knee.append(self.le_knee_align_no_r.text())
            # knee 10
            knee.append(self.cb_knee_muscle_l.isChecked())
            knee.append(self.cb_knee_muscle_pos_l.isChecked())
            knee.append(self.cb_knee_muscle_r.isChecked())
            knee.append(self.cb_knee_muscle_pos_r.isChecked())
            # knee 14        cb
            knee.append(self.cb_knee_effusion_l.isChecked())
            knee.append(self.cb_knee_effusion_pos_l.isChecked())
            knee.append(self.cb_knee_effusion_r.isChecked())
            knee.append(self.cb_knee_effusion_pos_r.isChecked())
            # knee 18        cb
            knee.append(self.cb_knee_rext_l.isChecked())
            knee.append(self.cb_knee_rext_pos_l.isChecked())
            knee.append(self.cb_knee_rext_r.isChecked())
            knee.append(self.cb_knee_rext_pos_r.isChecked())
            # knee 22        cb
            knee.append(self.cb_knee_rflex_l.isChecked())
            knee.append(self.cb_knee_rflex_pos_l.isChecked())
            knee.append(self.cb_knee_rflex_r.isChecked())
            knee.append(self.cb_knee_rflex_pos_r.isChecked())
            # knee 26        cb
            knee.append(self.cb_knee_mm_l.isChecked())
            knee.append(self.cb_knee_mm_pos_l.isChecked())
            knee.append(self.cb_knee_mm_r.isChecked())
            knee.append(self.cb_knee_mm_pos_r.isChecked())
            # knee 30        cb
            knee.append(self.cb_knee_pfg_l.isChecked())
            knee.append(self.cb_knee_pfg_pos_l.isChecked())
            knee.append(self.cb_knee_pfg_r.isChecked())
            knee.append(self.cb_knee_pfg_pos_r.isChecked())
            # knee 34
            knee.append(self.le_knee_rom_l.text())
            knee.append(self.le_knee_rom_r.text())
            # knee 36
            knee.append(self.cb_knee_mcl_l.isChecked())
            knee.append(self.cb_knee_mcl_lax_l.isChecked())
            knee.append(self.cb_knee_mcl_r.isChecked())
            knee.append(self.cb_knee_mcl_lax_r.isChecked())
            # knee 40
            knee.append(self.cb_knee_lcl_l.isChecked())
            knee.append(self.cb_knee_lcl_lax_l.isChecked())
            knee.append(self.cb_knee_lcl_r.isChecked())
            knee.append(self.cb_knee_lcl_lax_r.isChecked())
            # knee 44
            knee.append(self.le_knee_l_tender.text())
            knee.append(self.le_knee_r_tender.text())
            knee.append(self.le_knee_other.text())
            # hip 0
            hip.append(self.cb_hip_pt.isChecked())
            hip.append(self.hip_pelvic_tilt)
            # hip 2
            hip.append(self.cb_hip_trend_l.isChecked())
            hip.append(self.cb_hip_trend_l_pos.isChecked())
            hip.append(self.cb_hip_trend_r.isChecked())
            hip.append(self.cb_hip_trend_r_pos.isChecked())
            # hip 6
            hip.append(self.le_hip_lrot_l_pos.text())
            hip.append(self.le_hip_lrot_r_pos.text())
            hip.append(self.le_hip_mrot_l_pos.text())
            hip.append(self.le_hip_mrot_r_pos.text())
            hip.append(self.le_hip_flex_l_pos.text())
            hip.append(self.le_hip_flex_r_pos.text())
            # hip 12
            hip.append(self.cb_hip_abd_l.isChecked())
            hip.append(self.cb_hip_abd_l_painful.isChecked())
            hip.append(self.cb_hip_abd_r.isChecked())
            hip.append(self.cb_hip_abd_r_painful.isChecked())
            # hip 16
            hip.append(self.cb_hip_rlrot_l.isChecked())
            hip.append(self.cb_hip_rlrot_l_painful.isChecked())
            hip.append(self.cb_hip_rlrot_r.isChecked())
            hip.append(self.cb_hip_rlrot_r_painful.isChecked())
            # hip 20
            hip.append(self.cb_hip_rmrot_l.isChecked())
            hip.append(self.cb_hip_rmrot_l_painful.isChecked())
            hip.append(self.cb_hip_rmrot_r.isChecked())
            hip.append(self.cb_hip_rmrot_r_painful.isChecked())
            # hip 24
            hip.append(self.cb_hip_radd_l.isChecked())
            hip.append(self.cb_hip_radd_l_painful.isChecked())
            hip.append(self.cb_hip_radd_r.isChecked())
            hip.append(self.cb_hip_radd_r_painful.isChecked())
            # hip 28
            hip.append(self.le_hip_tenderness.text())
            hip.append(self.le_hip_other.text())
            # neck 0
            neck.append(self.le_neck_ext.text())
            neck.append(self.le_neck_rot_l.text())
            neck.append(self.le_neck_rot_r.text())
            neck.append(self.le_neck_cranial.text())
            # neck 4
            neck.append(self.cb_neck_sen.isChecked())
            neck.append(self.cb_neck_sen_equals.isChecked())
            neck.append(self.le_neck_sen.text())
            # neck 7
            neck.append(self.cb_neck_power.isChecked())
            neck.append(self.cb_neck_power_equals.isChecked())
            neck.append(self.le_neck_power.text())
            # neck 10
            neck.append(self.cb_neck_reflexes.isChecked())
            neck.append(self.cb_neck_reflexes_equals.isChecked())
            neck.append(self.le_neck_reflexes.text())
            # neck 13
            neck.append(self.le_neck_tender.text())
            neck.append(self.le_neck_other.text())
            # shoulder 0
            shoulder.append(self.cb_sh_align_l.isChecked())
            shoulder.append(self.cb_sh_align_ab_l.isChecked())
            shoulder.append(self.le_sh_align_l.text())
            shoulder.append(self.cb_sh_align_r.isChecked())
            shoulder.append(self.cb_sh_align_ab_r.isChecked())
            shoulder.append(self.le_sh_align_r.text())
            # shoulder 6
            shoulder.append(self.cb_sh_rom_l.isChecked())
            shoulder.append(self.rb_sh_rom_full_l.isChecked())
            shoulder.append(self.cb_sh_rom_r.isChecked())
            shoulder.append(self.rb_sh_rom_full_r.isChecked())
            # shoulder 10
            shoulder.append(self.le_sh_abd_l.text())
            shoulder.append(self.le_sh_abd_r.text())
            # shoulder 12
            shoulder.append(self.le_sh_lrot_l.text())
            shoulder.append(self.le_sh_lrot_r.text())
            # shoulder 14
            shoulder.append(self.cb_sh_mrot_l.isChecked())
            shoulder.append(self.cb_sh_mrot_limit_l.isChecked())
            shoulder.append(self.cb_sh_mrot_r.isChecked())
            shoulder.append(self.cb_sh_mrot_limit_r.isChecked())
            # shoulder 18
            shoulder.append(self.cb_sh_add_l.isChecked())
            shoulder.append(self.cb_sh_add_limit_l.isChecked())
            shoulder.append(self.cb_sh_add_r.isChecked())
            shoulder.append(self.cb_sh_add_limit_r.isChecked())

            # shoulder 22
            shoulder.append(self.le_sh_res_abd_l.text())
            shoulder.append(self.le_sh_res_abd_r.text())
            # shoulder 24
            shoulder.append(self.le_sh_res_lrot_l.text())
            shoulder.append(self.le_sh_res_lrot_r.text())
            # shoulder 26
            shoulder.append(self.cb_sh_res_mrot_l.isChecked())
            shoulder.append(self.cb_sh_res_mrot_painful_l.isChecked())
            shoulder.append(self.cb_sh_res_mrot_r.isChecked())
            shoulder.append(self.cb_sh_res_mrot_painful_r.isChecked())
            # shoulder 30
            shoulder.append(self.cb_sh_res_add_l.isChecked())
            shoulder.append(self.cb_sh_res_add_painful_l.isChecked())
            shoulder.append(self.cb_sh_res_add_r.isChecked())
            shoulder.append(self.cb_sh_res_add_painful_r.isChecked())
            # shoulder 34
            shoulder.append(self.cb_sh_res_jobes_l.isChecked())
            shoulder.append(self.cb_sh_res_jobes_pos_l.isChecked())
            shoulder.append(self.cb_sh_res_jobes_r.isChecked())
            shoulder.append(self.cb_sh_res_jobes_pos_r.isChecked())
            # addition 2024
            # shoulder 38
            shoulder.append(self.cb_sh_mrot_pain_l.isChecked())
            shoulder.append(self.cb_sh_mrot_pain_r.isChecked())
            shoulder.append(self.cb_sh_add_pain_l.isChecked())
            shoulder.append(self.cb_sh_add_pain_r.isChecked())

            exam.append(self.te_exam.toPlainText())
            tests.append(self.te_tests.toPlainText())
            recommend.append(self.te_recommend.toPlainText())

            ret = save_visit(self.tz, self.visit_date, cc, loc, back, knee, ankle,
                             anklest,hip, neck, shoulder, exam, tests, self.visit_procs, self.visit_diags, recommend)
            if error_codes.ERR_OK == ret:
                QMessageBox.information(self, "Done", "Visit saved OK")
            elif error_codes.ERR_EXISTS == ret:
                QMessageBox.warning(self, "Save", "Could not save visit data!!!")
            elif error_codes.ERR_BAD == ret:
                QMessageBox.warning(self, "Modify", "Could not modify visit data!!!")


    def clear_visit_form(self):
        for le in self.findChildren(qtw.QLineEdit):
            le.setText('')
        for cb in self.findChildren(qtw.QCheckBox):
            cb.setChecked(False)
        for te in self.findChildren(qtw.QTextEdit):
            te.setPlainText('')
        for bg in self.findChildren(qtw.QButtonGroup):
            bg.setExclusive(False)
        for rb in self.findChildren(qtw.QRadioButton):
            rb.setChecked(False)
        for bg in self.findChildren(qtw.QButtonGroup):
            bg.setExclusive(True)

        self.lv_model_proc.entries.clear()
        self.lv_model_proc.layoutAboutToBeChanged.emit()
        self.lv_model_proc.layoutChanged.emit()

    @qtc.Slot()
    def add_procedure(self):
        text = self.le_proc.text()
        text = text.strip()
        text = string.capwords(text)
        if text:
            self.lv_model_proc.entries.append((False, text))
            self.lv_model_proc.layoutAboutToBeChanged.emit()
            self.lv_model_proc.layoutChanged.emit()
            self.le_proc.setText("")
            self.visit_procs[text] = ""
            self.lb_proc_details.setText("Procedure Details")


    def delete_procedure(self):
        indexes = self.lv_proc.selectedIndexes()
        if indexes:
            index = indexes[0]
            del self.visit_procs[index.data()]
            del self.lv_model_proc.entries[index.row()]
            self.lv_model_proc.layoutAboutToBeChanged.emit()
            self.lv_model_proc.layoutChanged.emit()
            self.lv_proc.clearSelection()
            self.selected_procedure = ""

    def add_diagnosis(self):
        text = self.le_diag.text()
        text = text.strip()
        text = string.capwords(text)
        if text:
            self.lv_model_diag.entries.append((False, text))
            self.lv_model_diag.layoutAboutToBeChanged.emit()
            self.lv_model_diag.layoutChanged.emit()
            self.le_diag.setText("")
            self.visit_diags[text] = ""
            self.selected_diagnosis = ""
            self.lb_diag_details.setText("Diagnosis Details")

    def add_diagnosis_details(self):
        if self.selected_diagnosis:
            self.visit_diags[self.selected_diagnosis] = self.te_diag_details.toPlainText() or " "
            QMessageBox.warning(self, "Diagnosis Detail", "Don't forget to save the visit!")
        else:
            QMessageBox.warning(self, "Diagnosis Detail",
                "You must select a diagnosis first!")

    def add_procedure_details(self):
        if self.selected_procedure:
            self.visit_procs[self.selected_procedure] = self.te_proc_details.toPlainText() or " "
            # self.visit_procs[self.selected_procedure] = self.le_proc_details.text() or " "
            QMessageBox.warning(self, "Diagnosis Detail", "Don't forget to save the visit!")
        else:
            QMessageBox.warning(self, "Procedure Detail",
                "You must select a Procedure first!")

    def delete_diagnosis(self):
        indexes = self.lv_diag.selectedIndexes()
        if indexes:
            index = indexes[0]
            del self.visit_diags[index.data()]
            del self.lv_model_diag.entries[index.row()]
            self.lv_model_diag.layoutAboutToBeChanged.emit()
            self.lv_model_diag.layoutChanged.emit()
            self.lv_diag.clearSelection()

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    window = VisitForm()
    window.show()

    sys.exit(app.exec())
