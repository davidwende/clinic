from Config.config import host, connection
import datetime
import os
from pathlib import Path
from pony.orm import Database, PrimaryKey, Required,Optional, Set, db_session
from datetime import date  # Import the datetime module
from datetime import time  # Import the datetime module

file_name = "my_database.sqlite"
# Define the SQLite database

db = Database()
if connection['type'] == "sqlite":
    print("===> sqlite")
    db.bind("sqlite", file_name, create_db=True)

# POP = True
# POP = False

# Define the Patient Core table
class PatientCore(db.Entity):
    tz = PrimaryKey(str, 9)
    fname = Required(str, 20)
    surname = Required(str, 20)
    dob = Optional(date)  # You can use a Date type if you prefer
    male = Required(bool, default=True, sql_default='1')
    email = Optional(str, 30)
    phone_number = Required(str, 12)
    smoking = Required(bool, default=True, sql_default='1')
    visits = Set("Visits")
    consent = Optional(bool, default=False, sql_default='1')

# Define the Visits table
class Visits(db.Entity):
    # primaryKey = PrimaryKey(PatientCore, date)
    patient = Required(PatientCore)
    visit_date = Required(date)
    PrimaryKey(patient, visit_date)
    # visit_type = Required(str)

    cc_onset = Optional(str, 100)
    cc_description = Optional(str,2000)
    cc_walking = Optional(bool, default=False, sql_default='1')
    cc_walking_le = Optional(str, 50)
    cc_standing = Optional(bool, default=False, sql_default='1')
    cc_standing_le = Optional(str, 50)
    cc_sitting = Optional(bool, default=False, sql_default='1')
    cc_sitting_le = Optional(str, 50)
    cc_lying = Optional(bool, default=False, sql_default='1')
    cc_lying_le = Optional(str, 50)
    cc_lifting = Optional(bool, default=False, sql_default='1')
    cc_lifting_le = Optional(str, 50)
    cc_shoulder_move = Optional(bool, default=False, sql_default='1')
    cc_shoulder_move_le = Optional(str, 50)
    
    # Location
    cc_loc_neck = Optional(bool, default=False, sql_default='1')
    cc_loc_spine = Optional(bool, default=False, sql_default='1')
    cc_loc_back = Optional(bool, default=False, sql_default='1')
    cc_loc_shoulder_l = Optional(bool, default=False, sql_default='1')
    cc_loc_shoulder_r = Optional(bool, default=False, sql_default='1')
    cc_loc_hips_l = Optional(bool, default=False, sql_default='1')
    cc_loc_hips_r = Optional(bool, default=False, sql_default='1')
    cc_loc_groin_l = Optional(bool, default=False, sql_default='1')
    cc_loc_groin_r = Optional(bool, default=False, sql_default='1')
    cc_loc_knee_l = Optional(bool, default=False, sql_default='1')
    cc_loc_knee_r = Optional(bool, default=False, sql_default='1')
    cc_loc_ankle_l = Optional(bool, default=False, sql_default='1')
    cc_loc_ankle_r = Optional(bool, default=False, sql_default='1')
    cc_loc_other = Optional(bool, default=False, sql_default='1')
    cc_loc_precise_le = Optional(str, 100)
    cc_loc_radiates_le = Optional(str, 100)
    
    # Back Examinations
    back_movement_le = Optional(str, 100)

    back_trend_l = Optional(bool, default=False, sql_default='1')
    back_trend_r = Optional(bool, default=False, sql_default='1')
    back_trend_l_pos = Optional(bool, default=False, sql_default='1')
    back_trend_r_pos = Optional(bool, default=False, sql_default='1')

    back_slr_l_le = Optional(str, 50)
    back_slr_r_le = Optional(str, 50)

    back_fst_l = Optional(bool, default=False, sql_default='1')
    back_fst_l_pos = Optional(bool, default=False, sql_default='1')
    back_fst_r = Optional(bool, default=False, sql_default='1')
    back_fst_r_pos = Optional(bool, default=False, sql_default='1')

    back_hip_l = Optional(bool, default=False, sql_default='1')
    back_hip_l_pain = Optional(bool, default=False, sql_default='1')
    back_hip_r = Optional(bool, default=False, sql_default='1')
    back_hip_r_pain = Optional(bool, default=False, sql_default='1')

    back_thigh_l = Optional(bool, default=False, sql_default='1')
    back_thigh_l_pos = Optional(bool, default=False, sql_default='1')
    back_thigh_r = Optional(bool, default=False, sql_default='1')
    back_thigh_r_pos = Optional(bool, default=False, sql_default='1')
    
    back_fabere_l = Optional(bool, default=False, sql_default='1')
    back_fabere_l_pos = Optional(bool, default=False, sql_default='1')
    back_fabere_r = Optional(bool, default=False, sql_default='1')
    back_fabere_r_pos = Optional(bool, default=False, sql_default='1')

    back_sensation = Optional(bool, default=False, sql_default='1')
    back_sensation_equals = Optional(bool, default=False, sql_default='1')
    back_sensation_le = Optional(str, 50)

    back_power = Optional(bool, default=False, sql_default='1')
    back_power_equals = Optional(bool, default=False, sql_default='1')
    back_power_le = Optional(str, 50)

    back_reflexes = Optional(bool, default=False, sql_default='1')
    back_reflexes_equals = Optional(bool, default=False, sql_default='1')
    back_reflexes_le = Optional(str, 50)

    # Thoracic Spine
    back_tspine_rot_l = Optional(bool, default=False, sql_default='1')
    back_tspine_rot_l_pain = Optional(bool, default=False, sql_default='1')
    back_tspine_rot_r = Optional(bool, default=False, sql_default='1')
    back_tspine_rot_r_pain = Optional(bool, default=False, sql_default='1')
    back_tspine_tender_le = Optional(str, 100)


    # Back - resisted hip
    back_abduction_l = Optional(bool, default=False, sql_default='1')
    back_abduction_l_pos = Optional(bool, default=False, sql_default='1')
    back_abduction_r = Optional(bool, default=False, sql_default='1')
    back_abduction_r_pos = Optional(bool, default=False, sql_default='1')

    back_lat_rot_l = Optional(bool, default=False, sql_default='1')
    back_lat_rot_l_pos = Optional(bool, default=False, sql_default='1')
    back_lat_rot_r = Optional(bool, default=False, sql_default='1')
    back_lat_rot_r_pos = Optional(bool, default=False, sql_default='1')

    back_adduction_l = Optional(bool, default=False, sql_default='1')
    back_adduction_l_pos = Optional(bool, default=False, sql_default='1')
    back_adduction_r = Optional(bool, default=False, sql_default='1')
    back_adduction_r_pos = Optional(bool, default=False, sql_default='1')

    back_flexion_l = Optional(bool, default=False, sql_default='1')
    back_flexion_l_pos = Optional(bool, default=False, sql_default='1')
    back_flexion_r = Optional(bool, default=False, sql_default='1')
    back_flexion_r_pos = Optional(bool, default=False, sql_default='1')

    back_tenderness_le = Optional(str, 100)

    # Hip
    hip_pelvic_tilt = Optional(bool, default=False, sql_default='1')
    hip_pelvic_tilt_type = Optional(str, 10)

    hip_trend_l = Optional(bool, default=False, sql_default='1')
    hip_trend_l_pos = Optional(bool, default=False, sql_default='1')
    hip_trend_r = Optional(bool, default=False, sql_default='1')
    hip_trend_r_pos = Optional(bool, default=False, sql_default='1')

    hip_passive_lat_rot_l_le = Optional(str, 50)
    hip_passive_lat_rot_r_le = Optional(str, 50)
    hip_passive_medial_rot_l_le = Optional(str, 50)
    hip_passive_medial_rot_r_le = Optional(str, 50)
    hip_passive_flexion_l_le = Optional(str, 50)
    hip_passive_flexion_r_le = Optional(str, 50)

    hip_passive_med_rot_l = Optional(bool, default=False, sql_default='1')
    hip_passive_med_rot_l_limit = Optional(bool, default=False, sql_default='1')
    hip_passive_med_rot_r = Optional(bool, default=False, sql_default='1')
    hip_passive_med_rot_r_limit = Optional(bool, default=False, sql_default='1')

    hip_passive_flexion_l = Optional(bool, default=False, sql_default='1')
    hip_passive_flexion_l_limit = Optional(bool, default=False, sql_default='1')
    hip_passive_flexion_r = Optional(bool, default=False, sql_default='1')
    hip_passive_flexion_r_limit = Optional(bool, default=False, sql_default='1')

    hip_resisted_abd_l = Optional(bool, default=False, sql_default='1')
    hip_resisted_abd_l_limit = Optional(bool, default=False, sql_default='1')
    hip_resisted_abd_r = Optional(bool, default=False, sql_default='1')
    hip_resisted_abd_r_limit = Optional(bool, default=False, sql_default='1')

    hip_resisted_lat_rot_l = Optional(bool, default=False, sql_default='1')
    hip_resisted_lat_rot_l_limit = Optional(bool, default=False, sql_default='1')
    hip_resisted_lat_rot_r = Optional(bool, default=False, sql_default='1')
    hip_resisted_lat_rot_r_limit = Optional(bool, default=False, sql_default='1')

    hip_resisted_med_rot_l = Optional(bool, default=False, sql_default='1')
    hip_resisted_med_rot_l_limit = Optional(bool, default=False, sql_default='1')
    hip_resisted_med_rot_r = Optional(bool, default=False, sql_default='1')
    hip_resisted_med_rot_r_limit = Optional(bool, default=False, sql_default='1')

    hip_resisted_adduction_l = Optional(bool, default=False, sql_default='1')
    hip_resisted_adduction_l_limit = Optional(bool, default=False, sql_default='1')
    hip_resisted_adduction_r = Optional(bool, default=False, sql_default='1')
    hip_resisted_adduction_r_limit = Optional(bool, default=False, sql_default='1')

    hip_resisted_flexion_l = Optional(bool, default=False, sql_default='1')
    hip_resisted_flexion_l_limit = Optional(bool, default=False, sql_default='1')
    hip_resisted_flexion_r = Optional(bool, default=False, sql_default='1')
    hip_resisted_flexion_r_limit = Optional(bool, default=False, sql_default='1')

    hip_resisted_extension_l = Optional(bool, default=False, sql_default='1')
    hip_resisted_extension_l_limit = Optional(bool, default=False, sql_default='1')
    hip_resisted_extension_r = Optional(bool, default=False, sql_default='1')
    hip_resisted_extension_r_limit = Optional(bool, default=False, sql_default='1')

    hip_tenderness = Optional(str, 100)
    hip_other = Optional(str, 50)

    # Neck
    neck_extension_le = Optional(str, 50)
    neck_rotation_l_le = Optional(str, 50)
    neck_rotation_r_le = Optional(str, 50)
    neck_cranial_le = Optional(str, 50)

    neck_sensation = Optional(bool, default=False, sql_default='1')
    neck_sensation_equals = Optional(bool, default=False, sql_default='1')
    neck_sensation_le = Optional(str)

    neck_power = Optional(bool, default=False, sql_default='1')
    neck_power_equals = Optional(bool, default=False, sql_default='1')
    neck_power_le = Optional(str)

    neck_reflexes = Optional(bool, default=False, sql_default='1')
    neck_reflexes_equals = Optional(bool, default=False, sql_default='1')
    neck_reflexes_le = Optional(str)

    neck_tenderness_le = Optional(str, 100)
    neck_other_le = Optional(str, 100)

    # Shoulder
    shoulder_align_l = Optional(bool, default=False, sql_default='1')
    shoulder_align_l_ab = Optional(bool, default=False, sql_default='1')
    shoulder_align_l_le = Optional(str, 50)
    shoulder_align_r = Optional(bool, default=False, sql_default='1')
    shoulder_align_r_ab = Optional(bool, default=False, sql_default='1')
    shoulder_align_r_le = Optional(str, 50)

    shoulder_rom_l = Optional(bool, default=False, sql_default='1')
    shoulder_rom_l_full = Optional(bool, default=False, sql_default='1')
    shoulder_rom_r = Optional(bool, default=False, sql_default='1')
    shoulder_rom_r_full = Optional(bool, default=False, sql_default='1')

    shoulder_jobes_l = Optional(bool, default=False, sql_default='1')
    shoulder_jobes_l_pos = Optional(bool, default=False, sql_default='1')
    shoulder_jobes_r = Optional(bool, default=False, sql_default='1')
    shoulder_jobes_r_pos = Optional(bool, default=False, sql_default='1')

    shoulder_passive_abduction_l_le = Optional(str, 50)
    shoulder_passive_abduction_r_le = Optional(str, 50)

    shoulder_passive_lat_rot_l_le = Optional(str, 50)
    shoulder_passive_lat_rot_r_le = Optional(str, 50)

    shoulder_passive_med_rot_l = Optional(bool, default=False, sql_default='1')
    shoulder_passive_med_rot_l_limit = Optional(bool, default=False, sql_default='1')
    shoulder_passive_med_rot_l_pain = Optional(bool, default=False, sql_default='0')
    shoulder_passive_med_rot_r = Optional(bool, default=False, sql_default='1')
    shoulder_passive_med_rot_r_limit = Optional(bool, default=False, sql_default='1')
    shoulder_passive_med_rot_r_pain = Optional(bool, default=False, sql_default='0')

    shoulder_passive_adduction_l = Optional(bool, default=False, sql_default='1')
    shoulder_passive_adduction_l_limit = Optional(bool, default=False, sql_default='1')
    shoulder_passive_adduction_l_pain = Optional(bool, default=False, sql_default='0')
    shoulder_passive_adduction_r = Optional(bool, default=False, sql_default='1')
    shoulder_passive_adduction_r_limit = Optional(bool, default=False, sql_default='1')
    shoulder_passive_adduction_r_pain = Optional(bool, default=False, sql_default='0')

    shoulder_resisted_abduction_l_le = Optional(str, 50)
    shoulder_resisted_abduction_r_le = Optional(str, 50)

    shoulder_resisted_lat_rot_l_le = Optional(str, 50)
    shoulder_resisted_lat_rot_r_le = Optional(str, 50)

    shoulder_resisted_med_rot_l = Optional(bool, default=False, sql_default='1')
    shoulder_resisted_med_rot_l_limit = Optional(bool, default=False, sql_default='1')
    shoulder_resisted_med_rot_r = Optional(bool, default=False, sql_default='1')
    shoulder_resisted_med_rot_r_limit = Optional(bool, default=False, sql_default='1')

    shoulder_resisted_adduction_l = Optional(bool, default=False, sql_default='1')
    shoulder_resisted_adduction_l_limit = Optional(bool, default=False, sql_default='1')
    shoulder_resisted_adduction_r = Optional(bool, default=False, sql_default='1')
    shoulder_resisted_adduction_r_limit = Optional(bool, default=False, sql_default='1')

    examination = Optional(str, 512)
    recommendation = Optional(str, 2000)
    tests = Optional(str, 512)

    knee_scar_l = Optional(bool, default=False, sql_default='1')
    knee_scar_l_yes = Optional(bool, default=False, sql_default='1')
    knee_scar_r = Optional(bool, default=False, sql_default='1')
    knee_scar_r_yes = Optional(bool, default=False, sql_default='1')

    knee_align_l = Optional(bool, default=False, sql_default='1')
    knee_align_l_ab = Optional(bool, default=False, sql_default='1')
    knee_align_l_le = Optional(str, 50)
    knee_align_r = Optional(bool, default=False, sql_default='1')
    knee_align_r_ab = Optional(bool, default=False, sql_default='1')
    knee_align_r_le = Optional(str, 50)

    knee_muscle_l = Optional(bool, default=False, sql_default='1')
    knee_muscle_l_yes = Optional(bool, default=False, sql_default='1')
    knee_muscle_r = Optional(bool, default=False, sql_default='1')
    knee_muscle_r_yes = Optional(bool, default=False, sql_default='1')

    knee_effusion_l = Optional(bool, default=False, sql_default='1')
    knee_effusion_l_yes = Optional(bool, default=False, sql_default='1')
    knee_effusion_r = Optional(bool, default=False, sql_default='1')
    knee_effusion_r_yes = Optional(bool, default=False, sql_default='1')

    knee_rom_l = Optional(str, 50)
    knee_rom_r = Optional(str, 50)

    knee_res_ext_l = Optional(bool, default=False, sql_default='1')
    knee_res_ext_l_yes = Optional(bool, default=False, sql_default='1')
    knee_res_ext_r = Optional(bool, default=False, sql_default='1')
    knee_res_ext_r_yes = Optional(bool, default=False, sql_default='1')

    knee_res_flexion_l = Optional(bool, default=False, sql_default='1')
    knee_res_flexion_l_yes = Optional(bool, default=False, sql_default='1')
    knee_res_flexion_r = Optional(bool, default=False, sql_default='1')
    knee_res_flexion_r_yes = Optional(bool, default=False, sql_default='1')

    knee_macmurray_l = Optional(bool, default=False, sql_default='1')
    knee_macmurray_l_pos = Optional(bool, default=False, sql_default='1')
    knee_macmurray_r = Optional(bool, default=False, sql_default='1')
    knee_macmurray_r_pos = Optional(bool, default=False, sql_default='1')

    knee_grind_l = Optional(bool, default=False, sql_default='1')
    knee_grind_l_pos = Optional(bool, default=False, sql_default='1')
    knee_grind_r = Optional(bool, default=False, sql_default='1')
    knee_grind_r_pos = Optional(bool, default=False, sql_default='1')

    knee_mcl_l = Optional(bool, default=False, sql_default='1')
    knee_mcl_lax_l = Optional(bool, default=False, sql_default='1')
    knee_mcl_r = Optional(bool, default=False, sql_default='1')
    knee_mcl_lax_r = Optional(bool, default=False, sql_default='1')

    knee_lcl_l = Optional(bool, default=False, sql_default='1')
    knee_lcl_lax_l = Optional(bool, default=False, sql_default='1')
    knee_lcl_r = Optional(bool, default=False, sql_default='1')
    knee_lcl_lax_r = Optional(bool, default=False, sql_default='1')

    knee_tender_l_le = Optional(str, 100)
    knee_tender_r_le = Optional(str, 100)

    knee_other_le = Optional(str, 100)

    ankle_scar_l = Optional(bool, default=False, sql_default='1')
    ankle_scar_l_yes = Optional(bool, default=False, sql_default='1')
    ankle_scar_r = Optional(bool, default=False, sql_default='1')
    ankle_scar_r_yes = Optional(bool, default=False, sql_default='1')

    ankle_align_l = Optional(bool, default=False, sql_default='1')
    ankle_align_l_pronated = Optional(bool, default=False, sql_default='1')
    ankle_align_r = Optional(bool, default=False, sql_default='1')
    ankle_align_r_pronated = Optional(bool, default=False, sql_default='1')

    ankle_dors_l_le = Optional(str, 50)
    ankle_dors_r_le = Optional(str, 50)
    ankle_plant_l_le = Optional(str, 50)
    ankle_plant_r_le = Optional(str, 50)
    ankle_inversion_l_le = Optional(str, 50)
    ankle_inversion_r_le = Optional(str, 50)
    ankle_eversion_l_le = Optional(str, 50)
    ankle_eversion_r_le = Optional(str, 50)
    ankle_tender_le_l = Optional(str,100)
    ankle_tender_le_r = Optional(str,100)

    anklest_addpain_l = Optional(bool, default=False, sql_default='1')
    anklest_addpain_yes_l = Optional(bool, default=False, sql_default='1')
    anklest_addpain_r = Optional(bool, default=False, sql_default='1')
    anklest_addpain_yes_r = Optional(bool, default=False, sql_default='1')

    anklest_abcpain_l = Optional(bool, default=False, sql_default='1')
    anklest_abcpain_yes_l = Optional(bool, default=False, sql_default='1')
    anklest_abcpain_r = Optional(bool, default=False, sql_default='1')
    anklest_abcpain_yes_r = Optional(bool, default=False, sql_default='1')

    anklest_addlimited_l = Optional(bool, default=False, sql_default='1')
    anklest_addlimited_yes_l = Optional(bool, default=False, sql_default='1')
    anklest_addlimited_r = Optional(bool, default=False, sql_default='1')
    anklest_addlimited_yes_r = Optional(bool, default=False, sql_default='1')

    anklest_abclimited_l = Optional(bool, default=False, sql_default='1')
    anklest_abclimited_yes_l = Optional(bool, default=False, sql_default='1')
    anklest_abclimited_r = Optional(bool, default=False, sql_default='1')
    anklest_abclimited_yes_r = Optional(bool, default=False, sql_default='1')

    procedures = Set("Procedures")
    diagnoses = Set("Diagnoses")
    bloodpulse = Set("BloodPulse")


class PastHistory(db.Entity):
    tz = PrimaryKey(str,9)
    # name = PrimaryKey(str)
    hypertension = Optional(bool, default=True, sql_default='1')
    diabetes = Optional(bool, default=True, sql_default='1')
    blood = Optional(bool, default=True, sql_default='1')
    blood_descr = Optional(str)
    malignancy = Optional(bool, default=True, sql_default='1')
    malignancy_date = Optional(str, 15)
    malignancy_details = Optional(str)
    malignancy_remiss = Optional(bool, default=True, sql_default='1')
    disable = Optional(bool, default=True, sql_default='1')
    disable_details = Optional(str)
    nacs = Set("Nac")
    acs = Set("Ac")
    operations = Optional(str)
    trauma = Optional(str)
    
class Nac(db.Entity):
    pasthistory = Required(PastHistory)
    nac = Required(str, 32)


class Ac(db.Entity):
    pasthistory = Required(PastHistory)
    ac = Required(str, 32)


class Procedures(db.Entity):
    visit = Required(Visits)
    procedure = Required(str, 50)
    detail=Optional(str)
    PrimaryKey(visit, procedure)

class Diagnoses(db.Entity):
    visit = Required(Visits)
    diagnosis = Required(str, 50)
    detail=Optional(str)
    PrimaryKey(visit, diagnosis)

class Tests(db.Entity):
    name = Required(str)
    side = Optional(bool, default=True, sql_default='1') # Test also L and R ?
    result_type = Optional(str) # Yes/No, L=R, etc


class BloodPulse(db.Entity):
    visit = Required(Visits)
    time = Required(time)
    pulse = Optional(int, size=8)
    systolic = Optional(int, size=8)
    diastolic = Optional(int, size=8)
    PrimaryKey(visit, time)


if connection['type'] == "mysql":
    db.bind(provider='mysql', host=host['ip'], user='dowende', passwd='', db='clinic2')
    if connection['create'] == 'yes':
        db.generate_mapping(create_tables=True, check_tables=True)
    else:
        db.generate_mapping(create_tables=False, check_tables=True)
if connection['type'] == 'sqlite':
    db.generate_mapping(create_tables=True)


# Create the database tables

@db_session
def my_init_db():
    if not PatientCore.exists(tz="012345678"):
        print("===> writing db file <=====")
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        yesterday2 = today - datetime.timedelta(days=2, hours=4)

        with db_session:
            patient1 = PatientCore(
                tz = "012345678",
                fname="Jenny",
                surname="Doe",
                dob=date(2013, 1, 18),
                male=False,
                email="ssohn@example.com",
                smoking = False,
                phone_number="052-1336432",
            )
            patient2 = PatientCore(
                tz = "987654321",
                fname="Jim",
                surname="Doeussfjlsdf",
                dob=date(1936, 12, 8),
                male=True,
                email="jim@example.com",
                smoking = True,
                phone_number="054-2346479",
            )
            patient3 = PatientCore(
                tz = "440000565",
                fname="Harry",
                surname="Greenblack",
                dob=date(2023, 11, 28),
                male=True,
                email="john@example.com",
                smoking = True,
                phone_number="054-2346479",
            )
            v1 = Visits(
                patient = patient1,
                visit_date = today,
                cc_onset="bad pain",
                cc_walking = True,
                cc_walking_le = "hello walk"
            )
            v2 = Visits(
                patient = patient1,
                visit_date = yesterday,
                cc_lying=True,
                cc_lying_le = "hurts lying on side"
            )
            v3 = Visits(
                patient = patient2,
                visit_date = yesterday2
            )
            d1 = Diagnoses(
                visit = v2,
                diagnosis = "Herpes",
                detail = "pretty sure"
            )
            d2 = Diagnoses(
                visit = v2,
                diagnosis = "Skin Disease",
                detail = "unlikely"
            )
            d3 = Diagnoses(
                visit = v2,
                diagnosis = "Inflated Lung",
                detail = ""
            )


#my_init_db()
