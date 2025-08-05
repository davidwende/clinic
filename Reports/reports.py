# from weasyprint import HTML
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

import error_codes
from Database.dbFuncs import get_visit, get_past_history, get_acs, get_nacs
import Config

header = """
    <html
    lang = "he">
    <head>
    <meta
    charset = "UTF-8" >
    <title > Page Layout Example </title>
    <style>
    .header
    {display: flex;justify-content: space-between;align-items: center;padding: 10 px;
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
    <div class = "logo">
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
<hr>
<div>"""
tail = """</div>
</body>
</html>"""


def interesting(l):
    return any(isinstance(i, str) and i or isinstance(i, bool) and i for i in l)


class Report():
    def __init__(self, tz, date, surname, fname):
        self.tz = tz
        self.date = date
        self.surname = surname
        self.fname = fname
        self.s = ""
        self.h1("Summary Report for {}: {} {}".format(self.tz, self.surname, self.fname))
        self.h2("Visit Date: {}".format(self.date.strftime('%Y-%b-%d')))
        # self.count = 2
        self.page_size = 20
        self.create_string()

    def create_string(self):
        v, procs, diags = get_visit(self.tz, self.date)
        if error_codes.ERR_BAD == v:
            return
        ph = get_past_history(self.tz)
        nacs = get_nacs(self.tz)
        acs = get_acs(self.tz)

        # ============== Current Complaint ================
        self.h2("Current Complaint / אנמנזה")
        self.add_text_condition("Onset of Pain: <br>", v.cc_onset)
        self.add_text_condition("Pain Description: <br>", v.cc_description)

        if interesting([v.cc_walking, v.cc_standing, v.cc_sitting, v.cc_lying, v.cc_sitting, v.cc_lifting, v.cc_shoulder_move]):
            self.s += "<h3>Aggravating Factors</h3>"

            self.add_cb_text_condition("Walking", v.cc_walking, "", "", True, v.cc_walking_le)
            self.add_cb_text_condition("Standing", v.cc_standing, "", "", True, v.cc_standing_le)
            self.add_cb_text_condition("Sitting", v.cc_sitting, "", "", True, v.cc_sitting_le)
            self.add_cb_text_condition("Lying", v.cc_lying, "", "", True, v.cc_lying_le)

            self.add_cb_text_condition("Lifting", v.cc_lifting, "", "", True, v.cc_lifting_le)
            self.add_cb_text_condition("Shoulder Movement", v.cc_shoulder_move, "", "", True, v.cc_shoulder_move_le)


        if interesting([v.cc_loc_neck, v.cc_loc_spine, v.cc_loc_back, v.cc_loc_shoulder_l, v.cc_loc_shoulder_r,
            v.cc_loc_hips_l, v.cc_loc_hips_r, v.cc_loc_groin_l, v.cc_loc_groin_r, v.cc_loc_knee_l,
            v.cc_loc_knee_r, v.cc_loc_ankle_l, v.cc_loc_ankle_r, v.cc_loc_other]):
            self.h3("Location")
            self.concatenate_cb_if_true("Neck",  v.cc_loc_neck)
            self.concatenate_cb_if_true("Thoracic Spine",  v.cc_loc_spine)
            self.concatenate_cb_if_true("Lower Back",  v.cc_loc_back)
            self.concatenate_cb_if_true("Shoulder (left)",  v.cc_loc_shoulder_l)
            self.concatenate_cb_if_true("Shoulder (right)", v.cc_loc_shoulder_r)
            self.concatenate_cb_if_true("Hip (left)", v.cc_loc_hips_l)
            self.concatenate_cb_if_true("Hip (right)", v.cc_loc_hips_r)
            self.concatenate_cb_if_true("Groin (left)", v.cc_loc_groin_l)
            self.concatenate_cb_if_true("Groin (right)", v.cc_loc_groin_r)
            self.concatenate_cb_if_true("Knee (left)", v.cc_loc_knee_l)
            self.concatenate_cb_if_true("Knee (right)", v.cc_loc_knee_r)
            self.concatenate_cb_if_true("Ankle (left)", v.cc_loc_ankle_l)
            self.concatenate_cb_if_true("Ankle (right)", v.cc_loc_ankle_r)
            self.s += "\n"
            self.add_text_condition("Precise Location: ", v.cc_loc_precise_le)
            self.add_text_condition("Radiates to: ", v.cc_loc_radiates_le)

        # =================== Past History ====================
        if ph:
            self.h2("Past History / רקע רפואי")
            self.concatenate_cb_if_true("Hypertension",  ph.hypertension)
            self.concatenate_cb_if_true("Diabetes",  ph.diabetes)
            self.add_cb_text_condition("Blood Disorders", ph.blood, "", "", True, ph.blood_descr)
            self.add_cb_text_condition("Malignancies", ph.malignancy, "", "", True, ph.malignancy_date)
            self.add_cb_text_condition("Malignancies", ph.malignancy, "", "", True, ph.malignancy_details)
            self.concatenate_cb_if_true("Malignancy in Remission",  ph.malignancy_remiss)
            self.add_cb_text_condition("Disabilities", ph.disable, "", "", True, ph.disable_details)
            if nacs:
                self.h3("NAC Medications")
                for nac in nacs:
                    self.concatenate_cb_if_true(nac, True)
            if acs:
                self.h3("AC Medications")
                for ac in acs:
                    self.concatenate_cb_if_true(ac, True)
            if ph.operations:
                self.h3("Operations")
            self.concatenate_cb_if_true(ph.operations, True)
            if ph.trauma:
                self.h3("Trauma")
            self.concatenate_cb_if_true(ph.trauma, True )


        # =================== Back ====================
        back_examination = v.back_trend_l_pos or v.back_trend_r_pos or v.back_slr_l_le or v.back_slr_r_le or \
            v.back_hip_l_pain or v.back_hip_r_pain or v.back_thigh_l_pos or v.back_thigh_r_pos or \
            v.back_fabere_l_pos or v.back_fabere_r_pos or v.back_sensation or v.back_power or \
            v.back_reflexes or v.back_fst_l or v.back_fst_l_pos or v.back_fst_r or v.back_fst_r_pos
        back_resisted_hip = v.back_abduction_l or v.back_abduction_r or v.back_lat_rot_l or v.back_lat_rot_r or \
            v.back_adduction_l or v.back_adduction_r or v.back_flexion_l or v.back_flexion_r
        back_thoracic_spine = v.back_tspine_rot_l or v.back_tspine_rot_r or v.back_tspine_tender_le

        if back_examination or back_resisted_hip or back_thoracic_spine:
            self.h2("Back")
            # ======== Back Examination ==========
            if back_examination:
                self.h3("Back Examination")
                self.add_text_condition("Movements: ", v.back_movement_le)
                self.concatenate_if_true("Trendelenberg (left): ", v.back_trend_l, v.back_trend_l_pos)
                self.concatenate_if_true("Trendelenberg (right): ", v.back_trend_r, v.back_trend_r_pos)
                self.add_text_condition("SLR (left): ", v.back_slr_l_le)
                self.add_text_condition("SLR (right): ", v.back_slr_r_le)
                self.concatenate_if_true("FST (left): ", v.back_fst_l,  v.back_fst_l_pos)
                self.concatenate_if_true("FST (right): ", v.back_fst_r,  v.back_fst_r_pos)
                self.concatenate_if_true("Painful passive hip flexion (left): ", v.back_hip_l, v.back_hip_l_pain)
                self.concatenate_if_true("Painful passive hip flexion (right): ",v.back_hip_r,  v.back_hip_r_pain)
                self.concatenate_if_true("Thigh thrust (left): ",v.back_thigh_l,  v.back_thigh_l_pos)
                self.concatenate_if_true("Thigh thrust (right): ",v.back_thigh_r,  v.back_thigh_r_pos)
                self.concatenate_if_true("Fabere (left): ", v.back_fabere_l, v.back_fabere_l_pos)
                self.concatenate_if_true("Fabere (right): ",v.back_fabere_r, v.back_fabere_r_pos)
                self.add_cb_text_condition("Sensation: ", v.back_sensation,"L==R", "L!=R", v.back_sensation_equals, v.back_sensation_le)
                self.add_cb_text_condition("Power: ", v.back_power,"L==R", "L!=R", v.back_power_equals, v.back_power_le)
                self.add_cb_text_condition("Reflexes: ", v.back_reflexes,"L==R", "L!=R", v.back_reflexes_equals, v.back_reflexes_le)
                # ======== Back - Resisted Hip ===========
            if back_resisted_hip:
                self.h3("Back - Resisted Hip")
                self.concatenate_if_true("Abduction (left): ", v.back_abduction_l, v.back_abduction_l_pos)
                self.concatenate_if_true("Abduction (right): ", v.back_abduction_r, v.back_abduction_r_pos)
                self.concatenate_if_true("Lateral Rotation (left): ",  v.back_lat_rot_l, v.back_lat_rot_l_pos)
                self.concatenate_if_true("Lateral Rotation (right): ", v.back_lat_rot_r, v.back_lat_rot_r_pos)
                self.concatenate_if_true("Adduction (left): ",  v.back_adduction_l, v.back_adduction_l_pos)
                self.concatenate_if_true("Adduction (right): ", v.back_adduction_r, v.back_adduction_r_pos)
                self.concatenate_if_true("Flexion (left): ",  v.back_flexion_l, v.back_flexion_l_pos)
                self.concatenate_if_true("Flexion (right): ", v.back_flexion_r, v.back_flexion_r_pos)
                self.add_text_condition("Tenderness: ", v.back_tenderness_le)
                # ========= Back - Thoracic Spin ===========
            if back_thoracic_spine:
                self.h3("Back - Thoracic Spine")
                self.concatenate_if_true("Rotation (left): ", v.back_tspine_rot_l, v.back_tspine_rot_l_pain)
                self.concatenate_if_true("Rotation (right): ", v.back_tspine_rot_r, v.back_tspine_rot_r_pain)
                self.add_text_condition("Tenderness: ", v.back_tspine_tender_le)

        # =========== Neck =============
        neck = interesting([v.neck_extension_le, v.neck_rotation_l_le, v.neck_rotation_r_le, v.neck_cranial_le,
            v.neck_sensation, v.neck_power, v.neck_reflexes, v.neck_tenderness_le, v.neck_other_le])
        if neck:
            self.h2("Neck")
            self.add_text_condition("Extension: ", v.neck_extension_le)
            self.add_text_condition("Rotation (left): ", v.neck_rotation_l_le)
            self.add_text_condition("Rotation (right): ", v.neck_rotation_r_le)
            self.add_text_condition("Cranial Nerve: ", v.neck_cranial_le)
            self.add_cb_text_condition("Sensation: ", v.neck_sensation, "L==R", "L!=R", v.neck_sensation_equals, v.neck_sensation_le)
            self.add_cb_text_condition("Power: ", v.neck_power, "L==R", "L!=R", v.neck_power_equals, v.neck_power_le)
            self.add_cb_text_condition("Reflexes: ", v.neck_reflexes, "L==R", "L!=R", v.neck_reflexes_equals, v.neck_reflexes_le)
            self.add_text_condition("Other: ", v.neck_other_le)
        # =========== Shoulder =============
        scapular_motion = interesting([v.shoulder_align_l, v.shoulder_align_r, v.shoulder_rom_l, v.shoulder_rom_r])
        shoulder_passive_motion = interesting([v.shoulder_passive_abduction_l_le,v.shoulder_passive_abduction_r_le,
            v.shoulder_passive_lat_rot_l_le, v. shoulder_passive_lat_rot_r_le,
            v.shoulder_passive_med_rot_l, v.shoulder_passive_med_rot_r,
            v.shoulder_passive_adduction_l, v.shoulder_passive_adduction_r])
        shoulder_resisted_motion = interesting([v.shoulder_resisted_abduction_l_le, v.shoulder_resisted_abduction_r_le,
            v.shoulder_resisted_lat_rot_l_le, v.shoulder_resisted_lat_rot_r_le,
            v.shoulder_resisted_med_rot_l, v.shoulder_resisted_med_rot_r,
            v.shoulder_resisted_adduction_l, v.shoulder_resisted_adduction_r,
            v.shoulder_jobes_l, v.shoulder_jobes_r])
        shoulder = interesting([scapular_motion,shoulder_passive_motion, shoulder_resisted_motion])
        if shoulder:
            self.h2("Shoulder")
            if scapular_motion:
                self.h3("Shoulder - Scapular Motion")
                self.add_cb_text_condition("Alignment (left): ", v.shoulder_align_l, "Abnormal", "NAD", v.shoulder_align_l_ab, v.shoulder_align_l_le)
                self.add_cb_text_condition("Alignment (right): ", v.shoulder_align_r, "Abnormal", "NAD", v.shoulder_align_r_ab, v.shoulder_align_r_le)
                # TODO ROM
                if v.shoulder_rom_l:
                    if v.shoulder_rom_l_full:
                        self.s += "<br>" + "ROM (left) Full Range"
                    else:
                        self.s += "<br>" + "ROM (left) Limited"
                    # self.count += 1
                if v.shoulder_rom_r:
                    if v.shoulder_rom_r_full:
                        self.s += "<br>" + "ROM (right) Full Range"
                    else:
                        self.s += "<br>" + "ROM (right) Limited"
                    # self.count += 1

            if shoulder_passive_motion:
                self.h3("Shoulder - Passive Motion")
                self.add_text_condition("Abduction (left): ", v.shoulder_passive_abduction_l_le)
                self.add_text_condition("Abduction (right): ", v.shoulder_passive_abduction_r_le)
                self.add_text_condition("Lateral Rotation (left): ", v.shoulder_passive_lat_rot_l_le)
                self.add_text_condition("Lateral Rotation (right): ", v.shoulder_passive_lat_rot_r_le)

                self.limited_painful("Medial Rotation (left): ", v.shoulder_passive_med_rot_l, \
                                         v.shoulder_passive_med_rot_l_limit, v.shoulder_passive_med_rot_l_pain)
                self.limited_painful("Medial Rotation (right): ", v.shoulder_passive_med_rot_r, \
                                         v.shoulder_passive_med_rot_r_limit, v.shoulder_passive_med_rot_r_pain)
                self.limited_painful("Adduction (left): ", v.shoulder_passive_adduction_l, \
                                         v.shoulder_passive_adduction_l_limit, v.shoulder_passive_adduction_l_pain)
                self.limited_painful("Adduction (right): ", v.shoulder_passive_adduction_r, \
                                         v.shoulder_passive_adduction_r_limit, v.shoulder_passive_adduction_r_pain)
            if shoulder_resisted_motion:
                self.h3("Shoulder - Resisted Motion")
                self.add_text_condition("Abduction (left): ", v.shoulder_resisted_abduction_l_le)
                self.add_text_condition("Abduction (right): ", v.shoulder_resisted_abduction_r_le)
                self.add_text_condition("Lateral Rotation (left): ", v.shoulder_resisted_lat_rot_l_le)
                self.add_text_condition("Lateral Rotation (right): ", v.shoulder_resisted_lat_rot_r_le)

                self.concatenate_if_true("Medial Rotation (left): ", v.shoulder_resisted_med_rot_l, \
                                         v.shoulder_resisted_med_rot_l_limit, pos = "Painful", neg="")
                self.concatenate_if_true("Medial Rotation (right): ", v.shoulder_resisted_med_rot_r, \
                                         v.shoulder_resisted_med_rot_r_limit, pos = "Painful", neg="")
                self.concatenate_if_true("Adduction (left): ", v.shoulder_resisted_adduction_l, \
                                         v.shoulder_resisted_adduction_l_limit, pos = "Painful", neg="")
                self.concatenate_if_true("Adduction (right): ", v.shoulder_resisted_adduction_r, \
                                         v.shoulder_resisted_adduction_r_limit, pos = "Painful", neg="")

                self.concatenate_if_true("Jobes (left): ", v.shoulder_jobes_l, v.shoulder_jobes_l_pos)
                self.concatenate_if_true("Jobes (right): ", v.shoulder_jobes_r, v.shoulder_jobes_r_pos)
        # ========= Knee ===========
        knee = interesting([v.knee_scar_l, v.knee_scar_r, v.knee_align_l, v.knee_align_r,
        v.knee_muscle_l, v.knee_muscle_r, v.knee_effusion_l, v.knee_effusion_r,
        v.knee_res_ext_l, v.knee_res_ext_r, v.knee_res_flexion_l, v.knee_res_flexion_r,
        v.knee_macmurray_l, v.knee_macmurray_r, v.knee_grind_l, v.knee_grind_r,
        v.knee_rom_l, v.knee_rom_r, v.knee_mcl_l, v.knee_mcl_r, v.knee_lcl_l, v.knee_lcl_r,
        v.knee_tender_l_le, v.knee_tender_r_le, v.knee_other_le])
        if knee:
            self.h2("Knee")
            self.concatenate_if_true("Scarring (left): ", v.knee_scar_l, v.knee_scar_l_yes)
            self.concatenate_if_true("Scarring (right): ", v.knee_scar_l, v.knee_scar_l_yes)
            self.add_cb_text_condition("Alignment (left): ", v.knee_align_l, "Abnormal", "NAD",
                                       v.knee_align_l_ab, v.knee_align_l_le)
            self.add_cb_text_condition("Alignment (right): ", v.knee_align_r, "Abnormal", "NAD",
                                       v.knee_align_r_ab, v.knee_align_r_le)
            self.concatenate_if_true("Muscle Wasting (left): ", v.knee_muscle_l, v.knee_muscle_l_yes)
            self.concatenate_if_true("Muscle Wasting (right): ", v.knee_muscle_r, v.knee_muscle_r_yes)
            self.concatenate_if_true("Effusion (left): ", v.knee_effusion_l, v.knee_effusion_l_yes)
            self.concatenate_if_true("Effusion (right): ", v.knee_effusion_r, v.knee_effusion_r_yes)
            self.concatenate_if_true("Resisted Extension (left): ", v.knee_res_ext_l, v.knee_res_ext_l_yes, pos="Painful", neg="Painless")
            self.concatenate_if_true("Resisted Extension (right): ", v.knee_res_ext_r, v.knee_res_ext_r_yes, pos="Painful", neg="Painless")
            self.concatenate_if_true("Resisted Flexion (left): ", v.knee_res_flexion_l, v.knee_res_flexion_l_yes, pos="Painful", neg="Painless")
            self.concatenate_if_true("Resisted Flexion (right): ", v.knee_res_flexion_r, v.knee_res_flexion_r_yes, pos="Painful", neg="Painless")

            self.concatenate_if_true("McMurrays (left): ", v.knee_macmurray_l, v.knee_macmurray_l_pos)
            self.concatenate_if_true("McMurrays (right): ", v.knee_macmurray_r, v.knee_macmurray_r_pos)
            # self.concatenate_if_true("McMurrays (left): ", v.knee_res_flexion_l, v.knee_res_flexion_l_yes)
            # self.concatenate_if_true("McMurrays (right): ", v.knee_res_flexion_r, v.knee_res_flexion_r_yes)

            self.concatenate_if_true("Patelofemoral Grinding (left): ", v.knee_grind_l, v.knee_grind_l_pos)
            self.concatenate_if_true("Patelofemoral Grinding (right): ", v.knee_grind_r, v.knee_grind_r_pos)
            self.add_text_condition("ROM (left): ", v.knee_rom_l)
            self.add_text_condition("ROM (right): ", v.knee_rom_r)
            self.concatenate_if_true("MCL (left): ", v.knee_lcl_r, v.knee_lcl_lax_r, pos="Lax", neg="NAD")
            self.concatenate_if_true("MCL (right): ", v.knee_lcl_r, v.knee_lcl_lax_r, pos="Lax", neg="NAD")
            self.concatenate_if_true("LCL (left): ", v.knee_lcl_r, v.knee_lcl_lax_r, pos="Lax", neg="NAD")
            self.concatenate_if_true("LCL (right): ", v.knee_lcl_r, v.knee_lcl_lax_r, pos="Lax", neg="NAD")
            self.add_text_condition("Tenderness (left): ", v.knee_tender_l_le)
            self.add_text_condition("Tenderness (right): ", v.knee_tender_r_le)
            self.add_text_condition("Other: ", v.knee_other_le)

        ankle_joint = interesting([v.ankle_scar_l, v.ankle_scar_r, v.ankle_align_l, v.ankle_align_r,
                v.ankle_dors_l_le, v.ankle_dors_r_le,  v.ankle_plant_l_le, v.ankle_plant_r_le,
                v.ankle_inversion_l_le, v.ankle_inversion_r_le, v.ankle_eversion_l_le, v.ankle_eversion_r_le,
                               v.ankle_tender_le_l, v.ankle_tender_le_r])
        ankle_subtalar = interesting([v.anklest_addpain_l,v.anklest_addpain_r,v.anklest_abcpain_l, v.anklest_abcpain_r,
                v.anklest_addlimited_l,v.anklest_addlimited_r, v.anklest_abclimited_l, v.anklest_abclimited_r])
        if ankle_joint or ankle_subtalar:
            self.h2("Ankle")
            if ankle_joint:
                self.h3("Ankle - Joint")
                self.concatenate_if_true("Scarring (left): ", v.ankle_scar_l, v.ankle_scar_l_yes)
                self.concatenate_if_true("Scarring (right): ", v.ankle_scar_r, v.ankle_scar_r_yes)

                self.add_cb_text_condition("Alignment (left)", v.ankle_align_l, "", "", True,
                                          "Pronated" if  v.ankle_align_l_pronated else "Suppinated")
                self.add_cb_text_condition("Alignment (right)", v.ankle_align_r, "", "", True,
                                           "Pronated" if v.ankle_align_r_pronated else "Suppinated")

                # TODO Alignment
                self.add_text_condition("Dorsflexion (left): ", v.ankle_dors_l_le)
                self.add_text_condition("Dorsflexion (right): ", v.ankle_dors_r_le)
                self.add_text_condition("Plantarflexion (left): ", v.ankle_plant_l_le)
                self.add_text_condition("Plantarflexion (right): ", v.ankle_plant_r_le)
                self.add_text_condition("Inversion (left): ", v.ankle_inversion_l_le)
                self.add_text_condition("Inversion (right): ", v.ankle_inversion_r_le)
                self.add_text_condition("Eversion (left): ", v.ankle_eversion_l_le)
                self.add_text_condition("Eversion (right): ", v.ankle_eversion_r_le)
                self.add_text_condition("Tenderness (left): ", v.ankle_tender_le_l)
                self.add_text_condition("Tenderness (right): ", v.ankle_tender_le_r)
            if ankle_subtalar:
                self.h3("Ankle - Subtalar")
                self.concatenate_if_true("Adduction (left): ", v.anklest_addpain_l, v.anklest_addpain_yes_l,
                                         pos="Painful", neg="Painless")
                self.concatenate_if_true("Adduction (right): ", v.anklest_addpain_r, v.anklest_addpain_yes_r,
                                         pos="Painful", neg="Painless")
                self.concatenate_if_true("Abduction (left): ", v.anklest_abcpain_l, v.anklest_abcpain_yes_l,
                                         pos="Painful", neg="Painless")
                self.concatenate_if_true("Abduction (right): ", v.anklest_abcpain_r, v.anklest_abcpain_yes_r,
                                         pos="Painful", neg="Painless")

                self.concatenate_if_true("Adduction (left): ", v.anklest_addlimited_l, v.anklest_addlimited_yes_l,
                                         pos="Limited", neg="Full Range")
                self.concatenate_if_true("Adduction (right): ", v.anklest_addlimited_r, v.anklest_addlimited_yes_r,
                                         pos="Limited", neg="Full Range")
                self.concatenate_if_true("Abduction (left): ", v.anklest_abclimited_l, v.anklest_abclimited_yes_l,
                                         pos="Limited", neg="Full Range")
                self.concatenate_if_true("Abduction (right): ", v.anklest_abclimited_r, v.anklest_abclimited_yes_r,
                                         pos="Limited", neg="Full Range")
        hip_assessment = interesting([v.hip_pelvic_tilt, v.hip_trend_l, v.hip_trend_r])
        hip_passive = interesting([v.hip_passive_lat_rot_l_le, v.hip_passive_lat_rot_r_le,
            v.hip_passive_medial_rot_l_le,v.hip_passive_medial_rot_r_le,v.hip_passive_flexion_l_le, v.hip_passive_flexion_r])
        hip_resisted = interesting([v.hip_resisted_abd_l, v.hip_resisted_abd_r,
            v.hip_resisted_lat_rot_l,    v.hip_resisted_lat_rot_r,
            v.hip_resisted_med_rot_l, v.hip_resisted_med_rot_r,v.hip_resisted_adduction_l,v.hip_passive_flexion_r_le])
        hip_other = interesting([v.hip_tenderness, v.hip_other])
        if hip_assessment or hip_passive or hip_resisted or hip_other:
            self.h2("Ankle")
            if hip_assessment:
                self.h3("Hip - Assessment")
                self.add_cb_text_condition("Pelvic Tilt", v.hip_pelvic_tilt, "", "", True, v.hip_pelvic_tilt_type)
                self.concatenate_if_true("Trendelenberg (left): ", v.hip_trend_l, v.hip_trend_l_pos)
                self.concatenate_if_true("Trendelenberg (right): ", v.hip_trend_r, v.hip_trend_r_pos)
            if hip_passive:
                self.h3("Hip - Passive")
                self.add_text_condition("Lateral Rotation (left): ", v.hip_passive_lat_rot_l_le)
                self.add_text_condition("Lateral Rotation (right): ", v.hip_passive_lat_rot_r_le)

                self.add_text_condition("Medial Rotation (left): ", v.hip_passive_medial_rot_l_le)
                self.add_text_condition("Medial Rotation (right): ", v.hip_passive_medial_rot_r_le)

                self.add_text_condition("Flexion (left): ", v.hip_passive_flexion_l_le)
                self.add_text_condition("Flexion (right): ", v.hip_passive_flexion_r_le)

            if hip_resisted:
                self.h3("Hip - Resisted")

                self.concatenate_if_true("Abduction (left): ", v.hip_resisted_abd_l,
                                         v.hip_resisted_abd_l_limit, pos="Painful", neg="Painless")
                self.concatenate_if_true("Abduction (right): ", v.hip_resisted_abd_r,
                                         v.hip_resisted_abd_r_limit, pos="Painful", neg="Painless")

                self.concatenate_if_true("Lateral Rotation (left): ", v.hip_resisted_lat_rot_l,
                                         v.hip_resisted_lat_rot_l_limit, pos="Painful", neg="Painless")
                self.concatenate_if_true("Lateral Rotation (right): ", v.hip_resisted_lat_rot_r,
                                         v.hip_resisted_lat_rot_r_limit, pos="Painful", neg="Painless")

                self.concatenate_if_true("Medial Rotation (left): ", v.hip_resisted_med_rot_l,
                                         v.hip_resisted_med_rot_l_limit, pos="Painful", neg="Painless")
                self.concatenate_if_true("Medial Rotation (right): ", v.hip_resisted_med_rot_r,
                                         v.hip_resisted_med_rot_r_limit, pos="Painful", neg="Painless")

                self.concatenate_if_true("Adduction (left): ", v.hip_resisted_adduction_l,
                                         v.hip_resisted_adduction_l_limit, pos="Painful", neg="Painless")
                self.concatenate_if_true("Adduction (right): ", v.hip_resisted_adduction_r,
                                         v.hip_resisted_adduction_r_limit, pos="Painful", neg="Painless")

                self.concatenate_if_true("Flexion (left): ", v.hip_resisted_flexion_l,
                                         v.hip_resisted_flexion_l_limit, pos="Painful", neg="Painless")
                self.concatenate_if_true("Flexion (right): ", v.hip_resisted_flexion_r,
                                         v.hip_resisted_flexion_r_limit, pos="Painful", neg="Painless")
                self.concatenate_if_true("Extension (left): ", v.hip_resisted_extension_l,
                                         v.hip_resisted_extension_l_limit, pos="Painful", neg="Painless")
                self.concatenate_if_true("Extension (right): ", v.hip_resisted_extension_r,
                                         v.hip_resisted_extension_r_limit, pos="Painful", neg="Painless")
            if hip_other:
                self.h3("Hip - Other")
                self.add_text_condition("Tenderness: ", v.hip_tenderness)
                self.add_text_condition("Other: ", v.hip_other)
        if v.examination:
            self.h2("Examination / בדיקה פיזיקלאית כללית")
            c, e = self.convert_to_br(v.examination)
            # self.count += c-1
            self.add_text_condition("Examination: ", e)

        if v.tests:
            self.h2("Tests / בדיקות")
            c, e = self.convert_to_br(v.tests)
            # self.count += c-1
            self.add_text_condition("Test: ", e)

        if diags:
            self.h2("Diagnoses / אבחנות")
            for d in diags:
                if d[1]:
                    detail = " => " + d[1]
                else:
                    detail = ""
                self.add_text_condition("Diagnosis: ", d[0] + detail)

        if procs:
            self.h2("Procedures / טיפולים")
            for p in procs:
                if p[1]:
                    detail = " => " + p[1]
                else:
                    detail = ""
                self.add_text_condition("Procedure: ", p[0] + detail)

        if v.recommendation:
            self.h2("Recommendations / המלצות")
            c, e = self.convert_to_br(v.recommendation)
            # self.count += c-1
            self.add_text_condition("", e)

    def h1(self, x):
        self.s += f'<h1 class = "mtn">{x}</h1>'

    def h2(self, x):
        # self.s += f"<h2>{x}</h2>"
        self.s += f'<h2 class = "mtn">{x}</h2>'

    def h3(self, x):
        self.s += f'<h3 class = "mtn" >{x}</h3>'

    def h4(self, x):
        self.s += f'<h4 class = "mtn" >{x}</h4>'

    def add_text_condition(self, heading, addition):
        if addition:
            self.s += "<br>" + heading + self.replace_line_feed(addition)


    def replace_line_feed(self, input_string):
        return input_string.replace("\n", "\n<br>")

    def add_cb_text_condition(self, heading, condition, pos, neg, cb, text):
        if condition:
            self.s += "<br>" + heading
            if not cb:
                self.s += neg + " " + text
            else:
                self.s += pos + " " + text

    def limited_painful(self, heading, condition, limited, painful):
        if condition:
            self.s += "<br>" + heading
            if limited:
                self.s += "Limited "
            if painful:
                self.s += "Painfull"

    def concatenate_if_true(self, addition, condition, result, pos = "+ve", neg = "-ve"):
        if condition:
            self.s += "<br>" + addition
            if result:
                self.s += pos
            else:
                self.s += neg

    def concatenate_cb_if_true(self, addition, condition):
        if condition:
            # self.count += 1
            self.s += "<br>" + addition

    # def do_write(self):
    #     write_pdf(self.s)

    def get_string(self):
        return self.s

    def page_break(self):
        self.s += '<p style = "page-break-before: always;"> </p>'
        self.s += "===========   page break ==========="
        # self.count = 0

    def convert_to_br(self, text):
        c = text.count("\n")
        t = text.replace("\n", "<br>")
        return c, t
