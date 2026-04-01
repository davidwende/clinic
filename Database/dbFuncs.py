from pony.orm import select, flush, count, delete, exists
from datetime import date  # Import the datetime module
from Database.dbCreate import PatientCore, PastHistory,\
    Nac, Ac, db_session, Visits, Procedures, BloodPulse, Diagnoses
from PySide6.QtCore import QDate
import error_codes
import error_codes

@db_session
def get_all_patients():
    return select((len(p.visits), p.tz, p.fname, p.surname ) for p in PatientCore)[:]

@db_session
def get_patient_by_id(tz):
    print("In get_patient_by_id with : ", tz )
    print("Type is : ", type(tz), len(tz))
    # pp = select((len(p.visits), p.tz, p.fname, p.surname ) for p in PatientCore if (tz == p.tz))[:][0]
    # print(pp[1], type(pp[1]), len(pp[1]))
    p = PatientCore[tz]
    print(p)
    return p.dob,p.male, p.email, p.phone_number, p.smoking, p.consent
    # res = select( (p.dob, p.male, p.email, p.phone_number, p.smoking, p.consent ) for p in PatientCore if p.tz == tz)[:][0]
    # return res


def validate_tz(tz: str) -> bool:
    """
    Validates an Israeli ID number (Teudat Zehut) using the Luhn-like algorithm.

    The algorithm:
    1. The ID must be exactly 9 digits.
    2. Multiply each digit by 1 or 2 alternately (starting with 1).
    3. If the result of a multiplication is >= 10, sum its two digits (e.g. 14 -> 1+4 = 5).
    4. Sum all the results — a valid ID has a total divisible by 10.
    """
    # Remove whitespace and leading zeros padding, but keep as string
    tz = tz.strip()

    # Must be exactly 9 digits
    if not tz.isdigit() or len(tz) != 9:
        return False

    total = 0
    for i, digit in enumerate(tz):
        n = int(digit) * (1 if i % 2 == 0 else 2)
        if n >= 10:
            n = (n // 10) + (n % 10)
        total += n

    return total % 10 == 0


@db_session
def save_new_patient(tz, fname, surname, email, phone, smoker, dob, male, consent):
    PatientCore(tz = tz,
                fname = fname,
                surname = surname,
                email = email,
                phone_number = phone,
                dob = dob,
                smoking = smoker,
                male = male,
                consent = consent)

@db_session
def modify_patient(tz, fname, surname, email, phone, smoker, dob, male, consent):
    p = PatientCore[tz]
    p.fname = fname
    p.surname = surname
    p.email = email
    p.phone_number = phone
    p.dob = dob
    p.smoking = smoker
    p.male = male
    p.consent = consent

@db_session
def get_past_history(tz):
    if PastHistory.exists(tz=tz):
        return select(ph for ph in PastHistory if ph.tz==tz)[:][0]
    else:
        return None


@db_session
def save_patient_history(tz, hyper, diabetes, blood, blood_desc,
                         malig, malig_date, malig_details, malig_remiss,
                         disable, disable_details,
                         operations, trauma):
    if not PastHistory.exists(tz=tz):
        ph = PastHistory(tz=tz)
    # Now do a modify
    else:
        print("mod old PH")
        ph = PastHistory[tz]
    ph.hypertension = hyper
    ph.diabetes = diabetes
    ph.blood = blood
    ph.blood_descr = blood_desc
    ph.malignancy = malig
    ph.malignancy_date = malig_date
    ph.malignancy_details = malig_details
    ph.malignancy_remiss = malig_remiss
    ph.disable = disable
    ph.disable_details = disable_details
    ph.operations = operations
    ph.trauma = trauma

@db_session
def get_nacs(tz):
    if PastHistory.exists(tz=tz):
        ph = PastHistory[tz]
        return select(ph.nacs.nac for ph in PastHistory if ph.tz == tz )[:]
    else:
        return []

@db_session
def get_acs(tz):
    try:
        ph = PastHistory[tz]
        return select(ph.acs.ac for ph in PastHistory if ph.tz == tz )[:]
    except:
        return []

@db_session
def get_all_nacs():
    return select(nac.nac for nac in Nac).distinct().order_by(1)[:]

@db_session
def get_all_acs():
    return select(ac.ac for ac in Ac).distinct().order_by(1)[:]

@db_session
def save_nacs(tz, nacs):
    ph = PastHistory[tz]
    ph.nacs = []
    for nac in nacs:
        Nac(pasthistory = ph, nac = nac)

@db_session
def save_acs(tz, acs):
    ph = PastHistory[tz]
    ph.acs = []
    for ac in acs:
        Ac(pasthistory = ph, ac = ac)

@db_session
def patient_exists(tz):
    return PatientCore.exists(tz=tz)

@db_session
def visit_exists(tz, d):
    p = PatientCore[tz]
    # print("Patient is {}".format(p))
    e = Visits.exists(patient=p, visit_date=d)
    # print("In visit_exists with tz {} and date {}, Exists {}".format(tz,d,e))
    return e

@db_session
def num_visits(tz):
    p = PatientCore[tz]
    return select(v for v in Visits if v.patient == p).count()

@db_session
def delete_patient(tz):
    print("In delete patient with ", tz)
    if PastHistory.exists(tz=tz):
        PastHistory[tz].delete()
    PatientCore[tz].delete()


@db_session
def save_visit(tz, d, cc, loc, back, knee, ankle,anklest,
               hip, neck, shoulder, exam, tests, procs, diags, recommend ):
    try:
        p = PatientCore[tz]
        print("Date is : ", d)
        if visit_exists(tz, d):
            v = Visits[p, d]
        else:
            v = Visits(patient=p, visit_date=d)
    except Exception as error:
        print("An error occurred:", type(error).__name__,"-", error)
        return error_codes.ERR_BAD
    v.cc_onset       = cc[0]
    v.cc_description = cc[1]
    v.cc_walking     = cc[2]
    v.cc_walking_le  = cc[3]
    v.cc_standing    = cc[4]
    v.cc_standing_le = cc[5]
    v.cc_sitting     = cc[6]
    v.cc_sitting_le  = cc[7]
    v.cc_lying       = cc[8]
    v.cc_lying_le    = cc[9]
    v.cc_lifting       = cc[10]
    v.cc_lifting_le    = cc[11]
    v.cc_shoulder_move       = cc[12]
    v.cc_shoulder_move_le    = cc[13]
    # Location
    v.cc_loc_neck         = loc[0]
    v.cc_loc_spine        = loc[1]
    v.cc_loc_back         = loc[2]
    v.cc_loc_shoulder_l   = loc[3]
    v.cc_loc_shoulder_r   = loc[4]
    v.cc_loc_hips_l       = loc[5]
    v.cc_loc_hips_r       = loc[6]
    v.cc_loc_groin_l      = loc[7]
    v.cc_loc_groin_r      = loc[8]
    v.cc_loc_knee_l       = loc[9]
    v.cc_loc_knee_r       = loc[10]
    v.cc_loc_ankle_l      = loc[11]
    v.cc_loc_ankle_r      = loc[12]
    v.cc_loc_other        = loc[13]
    v.cc_loc_radiates_le  = loc[14]
    v.cc_loc_precise_le   = loc[15]
    # Back
    v.back_trend_l                        = back[0]
    v.back_trend_r                        = back[1]
    v.back_trend_l_pos                    = back[2] and back[0]
    v.back_trend_r_pos                    = back[3] and back[1]
    v.back_slr_l_le                       = back[4][:49]
    v.back_slr_r_le                       = back[5][:49]
    v.back_hip_l                          = back[6]
    v.back_hip_l_pain                     = back[7] and back[6]
    v.back_hip_r                          = back[8]
    v.back_hip_r_pain                     = back[9] and back[8]
    v.back_thigh_l                        = back[10]
    v.back_thigh_l_pos                    = back[11]
    v.back_thigh_r                        = back[12]
    v.back_thigh_r_pos                    = back[13]
    v.back_fabere_l                       = back[14]
    v.back_fabere_l_pos                   = back[15]
    v.back_fabere_r                       = back[16]
    v.back_fabere_r_pos                   = back[17]
    v.back_sensation                      = back[18]
    v.back_sensation_equals               = back[19] and back[18]
    v.back_sensation_le                   = back[20][:49]
    v.back_power                          = back[21]
    v.back_power_equals                   = back[22]
    v.back_power_le                       = back[23][:49]
    v.back_reflexes                       = back[24]
    v.back_reflexes_equals                = back[25]
    v.back_reflexes_le                    = back[26][:49]

    v.back_abduction_l                    = back[27]
    v.back_abduction_l_pos                = back[28]
    v.back_abduction_r                    = back[29]
    v.back_abduction_r_pos                = back[30]
    v.back_lat_rot_l                      = back[31]
    v.back_lat_rot_l_pos                  = back[32]
    v.back_lat_rot_r                      = back[33]
    v.back_lat_rot_r_pos                  = back[34]
    v.back_adduction_l                    = back[35]
    v.back_adduction_l_pos                = back[36]
    v.back_adduction_r                    = back[37]
    v.back_adduction_r_pos                = back[38]
    v.back_flexion_l                      = back[39]
    v.back_flexion_l_pos                  = back[40]
    v.back_flexion_r                      = back[41]
    v.back_flexion_r_pos                  = back[42]
    v.back_tenderness_le                  = back[43][:99]

    v.back_tspine_rot_l                   = back[44]
    v.back_tspine_rot_l_pain              = back[45]
    v.back_tspine_rot_r                   = back[46]
    v.back_tspine_rot_r_pain              = back[47]
    v.back_tspine_tender                  = back[48]

    v.back_movement_le                     = back[49]
    v.back_fst_l                           = back[50]
    v.back_fst_l_pos                       = back[51]
    v.back_fst_r                           = back[52]
    v.back_fst_r_pos                       = back[53]

    v.hip_pelvic_tilt                     = hip[0]
    v.hip_pelvic_tilt_type                = hip[1]
    v.hip_trend_l                         = hip[2]
    v.hip_trend_r                         = hip[3]
    v.hip_trend_l_pos                     = hip[4]
    v.hip_trend_r_pos                     = hip[5]

    v.hip_passive_lat_rot_l_le            = hip[6]
    v.hip_passive_lat_rot_r_le            = hip[7]
    v.hip_passive_medial_rot_l_le            = hip[8]
    v.hip_passive_medial_rot_r_le            = hip[9]
    v.hip_passive_flexion_l_le            = hip[10]
    v.hip_passive_flexion_r_le            = hip[11]

    v.hip_resisted_abd_l              = hip[12]
    v.hip_resisted_abd_l_limit        = hip[13]
    v.hip_resisted_abd_r              = hip[14]
    v.hip_resisted_abd_r_limit        = hip[15]

    v.hip_resisted_lat_rot_l              = hip[16]
    v.hip_resisted_lat_rot_l_limit        = hip[17]
    v.hip_resisted_lat_rot_r              = hip[18]
    v.hip_resisted_lat_rot_r_limit        = hip[19]

    v.hip_resisted_med_rot_l              = hip[20]
    v.hip_resisted_med_rot_l_limit        = hip[21]
    v.hip_resisted_med_rot_r              = hip[22]
    v.hip_resisted_med_rot_r_limit        = hip[23]

    v.hip_resisted_adduction_l            = hip[24]
    v.hip_resisted_adduction_l_limit      = hip[25]
    v.hip_resisted_adduction_r            = hip[26]
    v.hip_resisted_adduction_r_limit      = hip[27]
    v.hip_tenderness                      = hip[28]
    v.hip_other                           = hip[29]

    v.neck_extension_le                   = neck[0]
    v.neck_rotation_l_le                  = neck[1]
    v.neck_rotation_r_le                  = neck[2]
    v.neck_cranial_le                     = neck[3]

    v.neck_sensation                      = neck[4]
    v.neck_sensation_equals               = neck[5]
    v.neck_sensation_le                   = neck[6]

    v.neck_power                          = neck[7]
    v.neck_power_equals                   = neck[8]
    v.neck_power_le                       = neck[9]

    v.neck_reflexes                       = neck[10]
    v.neck_reflexes_equals                = neck[11]
    v.neck_reflexes_le                    = neck[12]
    v.neck_tenderness_le                  = neck[13]
    v.neck_other_le                       = neck[14]

    v.shoulder_align_l                    = shoulder[0]
    v.shoulder_align_l_ab                 = shoulder[1]
    v.shoulder_align_l_le                 = shoulder[2]
    v.shoulder_align_r                    = shoulder[3]
    v.shoulder_align_r_ab                 = shoulder[4]
    v.shoulder_align_r_le                 = shoulder[5]
    v.shoulder_rom_l                      = shoulder[6]
    v.shoulder_rom_l_full                 = shoulder[7]
    v.shoulder_rom_r                      = shoulder[8]
    v.shoulder_rom_r_full                 = shoulder[9]
    v.shoulder_passive_abduction_l_le     = shoulder[10]
    v.shoulder_passive_abduction_r_le     = shoulder[11]
    v.shoulder_passive_lat_rot_l_le       = shoulder[12]
    v.shoulder_passive_lat_rot_r_le       = shoulder[13]
    v.shoulder_passive_med_rot_l          = shoulder[14]
    v.shoulder_passive_med_rot_l_limit    = shoulder[15]
    v.shoulder_passive_med_rot_r          = shoulder[16]
    v.shoulder_passive_med_rot_r_limit    = shoulder[17]
    v.shoulder_passive_adduction_l        = shoulder[18]
    v.shoulder_passive_adduction_l_limit  = shoulder[19]
    v.shoulder_passive_adduction_r        = shoulder[20]
    v.shoulder_passive_adduction_r_limit  = shoulder[21]
    v.shoulder_resisted_abduction_l_le    = shoulder[22][:49]
    v.shoulder_resisted_abduction_r_le    = shoulder[23][:49]
    v.shoulder_resisted_lat_rot_l_le      = shoulder[24][:49]
    v.shoulder_resisted_lat_rot_r_le      = shoulder[25][:49]
    v.shoulder_resisted_med_rot_l         = shoulder[26]
    v.shoulder_resisted_med_rot_l_limit   = shoulder[27]
    v.shoulder_resisted_med_rot_r         = shoulder[28]
    v.shoulder_resisted_med_rot_r_limit   = shoulder[29]
    v.shoulder_resisted_adduction_l       = shoulder[30]
    v.shoulder_resisted_adduction_l_limit = shoulder[31]
    v.shoulder_resisted_adduction_r       = shoulder[32]
    v.shoulder_resisted_adduction_r_limit = shoulder[33]
    v.shoulder_jobes_l                    = shoulder[34]
    v.shoulder_jobes_l_pos                = shoulder[35]
    v.shoulder_jobes_r                    = shoulder[36]
    v.shoulder_jobes_r_pos                = shoulder[37]
    v.shoulder_passive_med_rot_l_pain     = shoulder[38]
    v.shoulder_passive_med_rot_r_pain     = shoulder[39]
    v.shoulder_passive_adduction_l_pain     = shoulder[40]
    v.shoulder_passive_adduction_r_pain     = shoulder[41]

    v.examination                         = exam[0]
    v.recommendation                      = recommend[0]
    v.tests                               = tests[0]

    v.knee_scar_l            = knee[0]
    v.knee_scar_l_yes        = knee[1]
    v.knee_scar_r            = knee[2]
    v.knee_scar_r_yes        = knee[3]
    v.knee_align_l           = knee[4]
    v.knee_align_l_ab        = knee[5]
    v.knee_align_l_le        = knee[6][:49]
    v.knee_align_r           = knee[7]
    v.knee_align_r_ab        = knee[8]
    v.knee_align_r_le        = knee[9][:49]
    v.knee_muscle_l          = knee[10]
    v.knee_muscle_l_yes      = knee[11]
    v.knee_muscle_r          = knee[12]
    v.knee_muscle_r_yes      = knee[13]
    v.knee_effusion_l        = knee[14]
    v.knee_effusion_l_yes    = knee[15]
    v.knee_effusion_r        = knee[16]
    v.knee_effusion_r_yes    = knee[17]
    v.knee_res_ext_l         = knee[18]
    v.knee_res_ext_l_yes     = knee[19]
    v.knee_res_ext_r         = knee[20]
    v.knee_res_ext_r_yes     = knee[21]
    v.knee_res_flexion_l     = knee[22]
    v.knee_res_flexion_l_yes = knee[23]
    v.knee_res_flexion_r     = knee[24]
    v.knee_res_flexion_r_yes = knee[25]
    v.knee_macmurray_l       = knee[26]
    v.knee_macmurray_l_pos   = knee[27]
    v.knee_macmurray_r       = knee[28]
    v.knee_macmurray_r_pos   = knee[29]
    v.knee_grind_l           = knee[30]
    v.knee_grind_l_pos       = knee[31]
    v.knee_grind_r           = knee[32]
    v.knee_grind_r_pos       = knee[33]
    v.knee_rom_l             = knee[34]
    v.knee_rom_r             = knee[35]
    v.knee_mcl_l             = knee[36]
    v.knee_mcl_lax_l         = knee[37]
    v.knee_mcl_r             = knee[38]
    v.knee_mcl_lax_r         = knee[39]
    v.knee_lcl_l             = knee[40]
    v.knee_lcl_lax_l         = knee[41]
    v.knee_lcl_r             = knee[42]
    v.knee_lcl_lax_r         = knee[43]
    v.knee_tender_l_le       = knee[44][:99]
    v.knee_tender_r_le       = knee[45][:99]
    v.knee_other_le          = knee[46][:99]

    v.ankle_scar_l                        = ankle[0]
    v.ankle_scar_l_yes                    = ankle[1]
    v.ankle_scar_r                        = ankle[2]
    v.ankle_scar_r_yes                    = ankle[3]
    v.ankle_align_l                       = ankle[4]
    v.ankle_align_l_pronated              = ankle[5]
    v.ankle_align_r                       = ankle[6]
    v.ankle_align_r_pronated              = ankle[7]
    v.ankle_dors_l_le                 = ankle[8][:49]
    v.ankle_dors_r_le                 = ankle[9][:49]
    v.ankle_plant_l_le                = ankle[10][:49]
    v.ankle_plant_r_le                = ankle[11][:49]
    v.ankle_inversion_l_le                = ankle[12][:49]
    v.ankle_inversion_r_le                = ankle[13][:49]
    v.ankle_eversion_l_le                = ankle[14][:49]
    v.ankle_eversion_r_le                = ankle[15][:49]
    v.ankle_tender_le_l                = ankle[16][:99]
    v.ankle_tender_le_r                = ankle[17][:99]

    v.anklest_addpain_l        = anklest[0]
    v.anklest_addpain_yes_l    = anklest[1]
    v.anklest_addpain_r        = anklest[2]
    v.anklest_addpain_yes_r    = anklest[3]

    v.anklest_abcpain_l        = anklest[4]
    v.anklest_abcpain_yes_l    = anklest[5]
    v.anklest_abcpain_r        = anklest[6]
    v.anklest_abcpain_yes_r    = anklest[7]

    v.anklest_addlimited_l     = anklest[8]
    v.anklest_addlimited_yes_l = anklest[9]
    v.anklest_addlimited_r     = anklest[10]
    v.anklest_addlimited_yes_r = anklest[11]
    v.anklest_abclimited_l     = anklest[12]
    v.anklest_abclimited_yes_l = anklest[13]
    v.anklest_abclimited_r     = anklest[14]
    v.anklest_abclimited_yes_r = anklest[15]
    #
    # cp = count(p for p in Procedures if p.visit==v)
    # cd = count(p for p in Diagnoses if p.visit==v)
    # print(cp, cd)
    #
    delete(p for p in Procedures if p.visit==v)
    delete(d for d in Diagnoses if d.visit==v)
    # cp = count(p for p in Procedures if p.visit==v)
    # cd = count(p for p in Diagnoses if p.visit==v)
    # print(cp, cd)
    flush()
    for proc in procs:
        print("in save with proc ", proc)
        Procedures(visit=v, procedure=proc, detail=procs[proc])
    for diag in diags:
        print("in save with diag ", diag)
        Diagnoses(visit=v, diagnosis=diag, detail=diags[diag])
    return error_codes.ERR_OK

@db_session
def get_all_procedures():
    return select(p.procedure for p in Procedures).distinct().order_by(1)[:]

@db_session
def get_all_diagnoses():
    return select((d.diagnosis, d.detail) for d in Diagnoses).distinct().order_by(1)[:]


@db_session
def get_all_blood(tz, visit_date):
    print("== get all bloods==", tz, visit_date)
    print("date type is ", type(visit_date))
    p = PatientCore[tz]
    if visit_exists(tz, visit_date):
        print("Blood: Visit exists")
        v = Visits[p, visit_date]
    else:
        v = Visits(patient=p, visit_date=visit_date)

    bloods = [(b.time, b.pulse, b.systolic, b.diastolic) for b in v.bloodpulse]
    print("returning ", bloods)
    bloods.sort(key=lambda a: a[0])
    print("returning as sorted", bloods)
    return bloods


@db_session
def add_blood_to_db(tz, visit_date, time, pulse, systolic, diastolic):
    print("add_blood_to_db:")
    print("tz ", tz)
    print("visit date ", visit_date)
    print("time ", time)
    print("pulse ", pulse)
    print("systolic ", systolic)
    print("diastolic ", diastolic)


    v = Visits[tz, visit_date]
    BloodPulse(visit=v,
               time=time,
               pulse=pulse,
               systolic=systolic,
               diastolic=diastolic)

@db_session
def get_visit_dates(tz):
    p = PatientCore[tz]
    # print(p.fname)
    # print(p.dob)
    return select(v.visit_date for v in Visits if v.patient == p).order_by(1)[:]
    # dd = select(v.visit_date for v in Visits if v.patient == p)
    # print(dd)
    # return []
    # return select(v.visit_date for v in Visits if v.patient == p).order_by(1)[:]

@db_session
def get_visit(tz, date):
    p = PatientCore[tz]
    if Visits.exists(patient=p, visit_date=date):
        visit_data = select(v for v in Visits if v.patient == p and v.visit_date == date)[:][0]
        procs = [(x.procedure, x.detail) for x in visit_data.procedures]
        diags = [(x.diagnosis, x.detail) for x in visit_data.diagnoses]
        return visit_data, procs, diags
    else:
        print("In get_visit - not found patient")
        return error_codes.ERR_BAD, error_codes.ERR_BAD, error_codes.ERR_BAD

@db_session
def delete_visit(tz, date):
    p = PatientCore[tz]
    if Visits.exists(patient=p, visit_date=date):
        Visits[tz, date].delete()
        return error_codes.ERR_OK
    else:
        return error_codes.ERR_BAD


@db_session
def visits_between_dates(start_date, end_date):
    return count(v for v in Visits if v.visit_date >= start_date
                 and v.visit_date <= end_date)
    # return 0

@db_session
def visits_with_procedures_between_dates(start_date, end_date):
    return count(v for v in Visits if v.visit_date >= start_date
                 and v.visit_date <= end_date
                 and exists(proc for proc in v.procedures))
    # return 0

@db_session
def modify_patient_tz(old_tz, new_tz):
    if patient_exists(new_tz):
        return False  # new tz exists
    old_patient = PatientCore[old_tz]
    # Create new patient
    new_patient = PatientCore(tz=new_tz,
                              fname=old_patient.fname,
                              surname=old_patient.surname,
                              dob=old_patient.dob,
                              male=old_patient.male,
                              email=old_patient.email,
                              phone_number=old_patient.phone_number,
                              smoking=old_patient.smoking,
                              consent=old_patient.consent)
    # Copy visits
    for visit in old_patient.visits:
        # Create new visit with new patient
        new_visit = Visits(patient=new_patient, visit_date=visit.visit_date)
        # Copy all fields
        new_visit.cc_onset = visit.cc_onset
        new_visit.cc_description = visit.cc_description
        new_visit.cc_walking = visit.cc_walking
        new_visit.cc_walking_le = visit.cc_walking_le
        new_visit.cc_standing = visit.cc_standing
        new_visit.cc_standing_le = visit.cc_standing_le
        new_visit.cc_sitting = visit.cc_sitting
        new_visit.cc_sitting_le = visit.cc_sitting_le
        new_visit.cc_lying = visit.cc_lying
        new_visit.cc_lying_le = visit.cc_lying_le
        new_visit.cc_lifting = visit.cc_lifting
        new_visit.cc_lifting_le = visit.cc_lifting_le
        new_visit.cc_shoulder_move = visit.cc_shoulder_move
        new_visit.cc_shoulder_move_le = visit.cc_shoulder_move_le
        # Location
        new_visit.cc_loc_neck = visit.cc_loc_neck
        new_visit.cc_loc_spine = visit.cc_loc_spine
        new_visit.cc_loc_back = visit.cc_loc_back
        new_visit.cc_loc_shoulder_l = visit.cc_loc_shoulder_l
        new_visit.cc_loc_shoulder_r = visit.cc_loc_shoulder_r
        new_visit.cc_loc_hips_l = visit.cc_loc_hips_l
        new_visit.cc_loc_hips_r = visit.cc_loc_hips_r
        new_visit.cc_loc_groin_l = visit.cc_loc_groin_l
        new_visit.cc_loc_groin_r = visit.cc_loc_groin_r
        new_visit.cc_loc_knee_l = visit.cc_loc_knee_l
        new_visit.cc_loc_knee_r = visit.cc_loc_knee_r
        new_visit.cc_loc_ankle_l = visit.cc_loc_ankle_l
        new_visit.cc_loc_ankle_r = visit.cc_loc_ankle_r
        new_visit.cc_loc_other = visit.cc_loc_other
        new_visit.cc_loc_precise_le = visit.cc_loc_precise_le
        new_visit.cc_loc_radiates_le = visit.cc_loc_radiates_le
        # Back
        new_visit.back_movement_le = visit.back_movement_le
        new_visit.back_trend_l = visit.back_trend_l
        new_visit.back_trend_r = visit.back_trend_r
        new_visit.back_trend_l_pos = visit.back_trend_l_pos
        new_visit.back_trend_r_pos = visit.back_trend_r_pos
        new_visit.back_slr_l_le = visit.back_slr_l_le
        new_visit.back_slr_r_le = visit.back_slr_r_le
        new_visit.back_fst_l = visit.back_fst_l
        new_visit.back_fst_l_pos = visit.back_fst_l_pos
        new_visit.back_fst_r = visit.back_fst_r
        new_visit.back_fst_r_pos = visit.back_fst_r_pos
        new_visit.back_hip_l = visit.back_hip_l
        new_visit.back_hip_l_pain = visit.back_hip_l_pain
        new_visit.back_hip_r = visit.back_hip_r
        new_visit.back_hip_r_pain = visit.back_hip_r_pain
        new_visit.back_thigh_l = visit.back_thigh_l
        new_visit.back_thigh_l_pos = visit.back_thigh_l_pos
        new_visit.back_thigh_r = visit.back_thigh_r
        new_visit.back_thigh_r_pos = visit.back_thigh_r_pos
        new_visit.back_fabere_l = visit.back_fabere_l
        new_visit.back_fabere_l_pos = visit.back_fabere_l_pos
        new_visit.back_fabere_r = visit.back_fabere_r
        new_visit.back_fabere_r_pos = visit.back_fabere_r_pos
        new_visit.back_sensation = visit.back_sensation
        new_visit.back_sensation_equals = visit.back_sensation_equals
        new_visit.back_sensation_le = visit.back_sensation_le
        new_visit.back_power = visit.back_power
        new_visit.back_power_equals = visit.back_power_equals
        new_visit.back_power_le = visit.back_power_le
        new_visit.back_reflexes = visit.back_reflexes
        new_visit.back_reflexes_equals = visit.back_reflexes_equals
        new_visit.back_reflexes_le = visit.back_reflexes_le
        new_visit.back_tspine_rot_l = visit.back_tspine_rot_l
        new_visit.back_tspine_rot_l_pain = visit.back_tspine_rot_l_pain
        new_visit.back_tspine_rot_r = visit.back_tspine_rot_r
        new_visit.back_tspine_rot_r_pain = visit.back_tspine_rot_r_pain
        new_visit.back_tspine_tender_le = visit.back_tspine_tender_le
        new_visit.back_abduction_l = visit.back_abduction_l
        new_visit.back_abduction_l_pos = visit.back_abduction_l_pos
        new_visit.back_abduction_r = visit.back_abduction_r
        new_visit.back_abduction_r_pos = visit.back_abduction_r_pos
        new_visit.back_lat_rot_l = visit.back_lat_rot_l
        new_visit.back_lat_rot_l_pos = visit.back_lat_rot_l_pos
        new_visit.back_lat_rot_r = visit.back_lat_rot_r
        new_visit.back_lat_rot_r_pos = visit.back_lat_rot_r_pos
        new_visit.back_adduction_l = visit.back_adduction_l
        new_visit.back_adduction_l_pos = visit.back_adduction_l_pos
        new_visit.back_adduction_r = visit.back_adduction_r
        new_visit.back_adduction_r_pos = visit.back_adduction_r_pos
        new_visit.back_flexion_l = visit.back_flexion_l
        new_visit.back_flexion_l_pos = visit.back_flexion_l_pos
        new_visit.back_flexion_r = visit.back_flexion_r
        new_visit.back_flexion_r_pos = visit.back_flexion_r_pos
        new_visit.back_tenderness_le = visit.back_tenderness_le
        # Hip
        new_visit.hip_pelvic_tilt = visit.hip_pelvic_tilt
        new_visit.hip_pelvic_tilt_type = visit.hip_pelvic_tilt_type
        new_visit.hip_trend_l = visit.hip_trend_l
        new_visit.hip_trend_r = visit.hip_trend_r
        new_visit.hip_trend_l_pos = visit.hip_trend_l_pos
        new_visit.hip_trend_r_pos = visit.hip_trend_r_pos
        new_visit.hip_passive_lat_rot_l_le = visit.hip_passive_lat_rot_l_le
        new_visit.hip_passive_lat_rot_r_le = visit.hip_passive_lat_rot_r_le
        new_visit.hip_passive_medial_rot_l_le = visit.hip_passive_medial_rot_l_le
        new_visit.hip_passive_medial_rot_r_le = visit.hip_passive_medial_rot_r_le
        new_visit.hip_passive_flexion_l_le = visit.hip_passive_flexion_l_le
        new_visit.hip_passive_flexion_r_le = visit.hip_passive_flexion_r_le
        new_visit.hip_passive_med_rot_l = visit.hip_passive_med_rot_l
        new_visit.hip_passive_med_rot_l_limit = visit.hip_passive_med_rot_l_limit
        new_visit.hip_passive_med_rot_r = visit.hip_passive_med_rot_r
        new_visit.hip_passive_med_rot_r_limit = visit.hip_passive_med_rot_r_limit
        new_visit.hip_passive_flexion_l = visit.hip_passive_flexion_l
        new_visit.hip_passive_flexion_l_limit = visit.hip_passive_flexion_l_limit
        new_visit.hip_passive_flexion_r = visit.hip_passive_flexion_r
        new_visit.hip_passive_flexion_r_limit = visit.hip_passive_flexion_r_limit
        new_visit.hip_resisted_abd_l = visit.hip_resisted_abd_l
        new_visit.hip_resisted_abd_l_limit = visit.hip_resisted_abd_l_limit
        new_visit.hip_resisted_abd_r = visit.hip_resisted_abd_r
        new_visit.hip_resisted_abd_r_limit = visit.hip_resisted_abd_r_limit
        new_visit.hip_resisted_lat_rot_l = visit.hip_resisted_lat_rot_l
        new_visit.hip_resisted_lat_rot_l_limit = visit.hip_resisted_lat_rot_l_limit
        new_visit.hip_resisted_lat_rot_r = visit.hip_resisted_lat_rot_r
        new_visit.hip_resisted_lat_rot_r_limit = visit.hip_resisted_lat_rot_r_limit
        new_visit.hip_resisted_med_rot_l = visit.hip_resisted_med_rot_l
        new_visit.hip_resisted_med_rot_l_limit = visit.hip_resisted_med_rot_l_limit
        new_visit.hip_resisted_med_rot_r = visit.hip_resisted_med_rot_r
        new_visit.hip_resisted_med_rot_r_limit = visit.hip_resisted_med_rot_r_limit
        new_visit.hip_resisted_adduction_l = visit.hip_resisted_adduction_l
        new_visit.hip_resisted_adduction_l_limit = visit.hip_resisted_adduction_l_limit
        new_visit.hip_resisted_adduction_r = visit.hip_resisted_adduction_r
        new_visit.hip_resisted_adduction_r_limit = visit.hip_resisted_adduction_r_limit
        new_visit.hip_resisted_flexion_l = visit.hip_resisted_flexion_l
        new_visit.hip_resisted_flexion_l_limit = visit.hip_resisted_flexion_l_limit
        new_visit.hip_resisted_flexion_r = visit.hip_resisted_flexion_r
        new_visit.hip_resisted_flexion_r_limit = visit.hip_resisted_flexion_r_limit
        new_visit.hip_resisted_extension_l = visit.hip_resisted_extension_l
        new_visit.hip_resisted_extension_l_limit = visit.hip_resisted_extension_l_limit
        new_visit.hip_resisted_extension_r = visit.hip_resisted_extension_r
        new_visit.hip_resisted_extension_r_limit = visit.hip_resisted_extension_r_limit
        new_visit.hip_tenderness = visit.hip_tenderness
        new_visit.hip_other = visit.hip_other
        # Neck
        new_visit.neck_extension_le = visit.neck_extension_le
        new_visit.neck_rotation_l_le = visit.neck_rotation_l_le
        new_visit.neck_rotation_r_le = visit.neck_rotation_r_le
        new_visit.neck_cranial_le = visit.neck_cranial_le
        new_visit.neck_sensation = visit.neck_sensation
        new_visit.neck_sensation_equals = visit.neck_sensation_equals
        new_visit.neck_sensation_le = visit.neck_sensation_le
        new_visit.neck_power = visit.neck_power
        new_visit.neck_power_equals = visit.neck_power_equals
        new_visit.neck_power_le = visit.neck_power_le
        new_visit.neck_reflexes = visit.neck_reflexes
        new_visit.neck_reflexes_equals = visit.neck_reflexes_equals
        new_visit.neck_reflexes_le = visit.neck_reflexes_le
        new_visit.neck_tenderness_le = visit.neck_tenderness_le
        new_visit.neck_other_le = visit.neck_other_le
        # Shoulder
        new_visit.shoulder_align_l = visit.shoulder_align_l
        new_visit.shoulder_align_l_ab = visit.shoulder_align_l_ab
        new_visit.shoulder_align_l_le = visit.shoulder_align_l_le
        new_visit.shoulder_align_r = visit.shoulder_align_r
        new_visit.shoulder_align_r_ab = visit.shoulder_align_r_ab
        new_visit.shoulder_align_r_le = visit.shoulder_align_r_le
        new_visit.shoulder_rom_l = visit.shoulder_rom_l
        new_visit.shoulder_rom_l_full = visit.shoulder_rom_l_full
        new_visit.shoulder_rom_r = visit.shoulder_rom_r
        new_visit.shoulder_rom_r_full = visit.shoulder_rom_r_full
        new_visit.shoulder_jobes_l = visit.shoulder_jobes_l
        new_visit.shoulder_jobes_l_pos = visit.shoulder_jobes_l_pos
        new_visit.shoulder_jobes_r = visit.shoulder_jobes_r
        new_visit.shoulder_jobes_r_pos = visit.shoulder_jobes_r_pos
        new_visit.shoulder_passive_abduction_l_le = visit.shoulder_passive_abduction_l_le
        new_visit.shoulder_passive_abduction_r_le = visit.shoulder_passive_abduction_r_le
        new_visit.shoulder_passive_lat_rot_l_le = visit.shoulder_passive_lat_rot_l_le
        new_visit.shoulder_passive_lat_rot_r_le = visit.shoulder_passive_lat_rot_r_le
        new_visit.shoulder_passive_med_rot_l = visit.shoulder_passive_med_rot_l
        new_visit.shoulder_passive_med_rot_l_limit = visit.shoulder_passive_med_rot_l_limit
        new_visit.shoulder_passive_med_rot_l_pain = visit.shoulder_passive_med_rot_l_pain
        new_visit.shoulder_passive_med_rot_r = visit.shoulder_passive_med_rot_r
        new_visit.shoulder_passive_med_rot_r_limit = visit.shoulder_passive_med_rot_r_limit
        new_visit.shoulder_passive_med_rot_r_pain = visit.shoulder_passive_med_rot_r_pain
        new_visit.shoulder_passive_adduction_l = visit.shoulder_passive_adduction_l
        new_visit.shoulder_passive_adduction_l_limit = visit.shoulder_passive_adduction_l_limit
        new_visit.shoulder_passive_adduction_l_pain = visit.shoulder_passive_adduction_l_pain
        new_visit.shoulder_passive_adduction_r = visit.shoulder_passive_adduction_r
        new_visit.shoulder_passive_adduction_r_limit = visit.shoulder_passive_adduction_r_limit
        new_visit.shoulder_passive_adduction_r_pain = visit.shoulder_passive_adduction_r_pain
        new_visit.shoulder_resisted_abduction_l_le = visit.shoulder_resisted_abduction_l_le
        new_visit.shoulder_resisted_abduction_r_le = visit.shoulder_resisted_abduction_r_le
        new_visit.shoulder_resisted_lat_rot_l_le = visit.shoulder_resisted_lat_rot_l_le
        new_visit.shoulder_resisted_lat_rot_r_le = visit.shoulder_resisted_lat_rot_r_le
        new_visit.shoulder_resisted_med_rot_l = visit.shoulder_resisted_med_rot_l
        new_visit.shoulder_resisted_med_rot_l_limit = visit.shoulder_resisted_med_rot_l_limit
        new_visit.shoulder_resisted_med_rot_r = visit.shoulder_resisted_med_rot_r
        new_visit.shoulder_resisted_med_rot_r_limit = visit.shoulder_resisted_med_rot_r_limit
        new_visit.shoulder_resisted_adduction_l = visit.shoulder_resisted_adduction_l
        new_visit.shoulder_resisted_adduction_l_limit = visit.shoulder_resisted_adduction_l_limit
        new_visit.shoulder_resisted_adduction_r = visit.shoulder_resisted_adduction_r
        new_visit.shoulder_resisted_adduction_r_limit = visit.shoulder_resisted_adduction_r_limit
        # Examination, recommendation, tests
        new_visit.examination = visit.examination
        new_visit.recommendation = visit.recommendation
        new_visit.tests = visit.tests
        # Knee
        new_visit.knee_scar_l = visit.knee_scar_l
        new_visit.knee_scar_l_yes = visit.knee_scar_l_yes
        new_visit.knee_scar_r = visit.knee_scar_r
        new_visit.knee_scar_r_yes = visit.knee_scar_r_yes
        new_visit.knee_align_l = visit.knee_align_l
        new_visit.knee_align_l_ab = visit.knee_align_l_ab
        new_visit.knee_align_l_le = visit.knee_align_l_le
        new_visit.knee_align_r = visit.knee_align_r
        new_visit.knee_align_r_ab = visit.knee_align_r_ab
        new_visit.knee_align_r_le = visit.knee_align_r_le
        new_visit.knee_muscle_l = visit.knee_muscle_l
        new_visit.knee_muscle_l_yes = visit.knee_muscle_l_yes
        new_visit.knee_muscle_r = visit.knee_muscle_r
        new_visit.knee_muscle_r_yes = visit.knee_muscle_r_yes
        new_visit.knee_effusion_l = visit.knee_effusion_l
        new_visit.knee_effusion_l_yes = visit.knee_effusion_l_yes
        new_visit.knee_effusion_r = visit.knee_effusion_r
        new_visit.knee_effusion_r_yes = visit.knee_effusion_r_yes
        new_visit.knee_rom_l = visit.knee_rom_l
        new_visit.knee_rom_r = visit.knee_rom_r
        new_visit.knee_res_ext_l = visit.knee_res_ext_l
        new_visit.knee_res_ext_l_yes = visit.knee_res_ext_l_yes
        new_visit.knee_res_ext_r = visit.knee_res_ext_r
        new_visit.knee_res_ext_r_yes = visit.knee_res_ext_r_yes
        new_visit.knee_res_flexion_l = visit.knee_res_flexion_l
        new_visit.knee_res_flexion_l_yes = visit.knee_res_flexion_l_yes
        new_visit.knee_res_flexion_r = visit.knee_res_flexion_r
        new_visit.knee_res_flexion_r_yes = visit.knee_res_flexion_r_yes
        new_visit.knee_macmurray_l = visit.knee_macmurray_l
        new_visit.knee_macmurray_l_pos = visit.knee_macmurray_l_pos
        new_visit.knee_macmurray_r = visit.knee_macmurray_r
        new_visit.knee_macmurray_r_pos = visit.knee_macmurray_r_pos
        new_visit.knee_grind_l = visit.knee_grind_l
        new_visit.knee_grind_l_pos = visit.knee_grind_l_pos
        new_visit.knee_grind_r = visit.knee_grind_r
        new_visit.knee_grind_r_pos = visit.knee_grind_r_pos
        new_visit.knee_mcl_l = visit.knee_mcl_l
        new_visit.knee_mcl_lax_l = visit.knee_mcl_lax_l
        new_visit.knee_mcl_r = visit.knee_mcl_r
        new_visit.knee_mcl_lax_r = visit.knee_mcl_lax_r
        new_visit.knee_lcl_l = visit.knee_lcl_l
        new_visit.knee_lcl_lax_l = visit.knee_lcl_lax_l
        new_visit.knee_lcl_r = visit.knee_lcl_r
        new_visit.knee_lcl_lax_r = visit.knee_lcl_lax_r
        new_visit.knee_tender_l_le = visit.knee_tender_l_le
        new_visit.knee_tender_r_le = visit.knee_tender_r_le
        new_visit.knee_other_le = visit.knee_other_le
        # Ankle
        new_visit.ankle_scar_l = visit.ankle_scar_l
        new_visit.ankle_scar_l_yes = visit.ankle_scar_l_yes
        new_visit.ankle_scar_r = visit.ankle_scar_r
        new_visit.ankle_scar_r_yes = visit.ankle_scar_r_yes
        new_visit.ankle_align_l = visit.ankle_align_l
        new_visit.ankle_align_l_pronated = visit.ankle_align_l_pronated
        new_visit.ankle_align_r = visit.ankle_align_r
        new_visit.ankle_align_r_pronated = visit.ankle_align_r_pronated
        new_visit.ankle_dors_l_le = visit.ankle_dors_l_le
        new_visit.ankle_dors_r_le = visit.ankle_dors_r_le
        new_visit.ankle_plant_l_le = visit.ankle_plant_l_le
        new_visit.ankle_plant_r_le = visit.ankle_plant_r_le
        new_visit.ankle_inversion_l_le = visit.ankle_inversion_l_le
        new_visit.ankle_inversion_r_le = visit.ankle_inversion_r_le
        new_visit.ankle_eversion_l_le = visit.ankle_eversion_l_le
        new_visit.ankle_eversion_r_le = visit.ankle_eversion_r_le
        new_visit.ankle_tender_le_l = visit.ankle_tender_le_l
        new_visit.ankle_tender_le_r = visit.ankle_tender_le_r
        new_visit.anklest_addpain_l = visit.anklest_addpain_l
        new_visit.anklest_addpain_yes_l = visit.anklest_addpain_yes_l
        new_visit.anklest_addpain_r = visit.anklest_addpain_r
        new_visit.anklest_addpain_yes_r = visit.anklest_addpain_yes_r
        new_visit.anklest_abcpain_l = visit.anklest_abcpain_l
        new_visit.anklest_abcpain_yes_l = visit.anklest_abcpain_yes_l
        new_visit.anklest_abcpain_r = visit.anklest_abcpain_r
        new_visit.anklest_abcpain_yes_r = visit.anklest_abcpain_yes_r
        new_visit.anklest_addlimited_l = visit.anklest_addlimited_l
        new_visit.anklest_addlimited_yes_l = visit.anklest_addlimited_yes_l
        new_visit.anklest_addlimited_r = visit.anklest_addlimited_r
        new_visit.anklest_addlimited_yes_r = visit.anklest_addlimited_yes_r
        new_visit.anklest_abclimited_l = visit.anklest_abclimited_l
        new_visit.anklest_abclimited_yes_l = visit.anklest_abclimited_yes_l
        new_visit.anklest_abclimited_r = visit.anklest_abclimited_r
        new_visit.anklest_abclimited_yes_r = visit.anklest_abclimited_yes_r
        # Copy procedures and diagnoses
        for proc in visit.procedures:
            Procedures(visit=new_visit, procedure=proc.procedure, detail=proc.detail)
        for diag in visit.diagnoses:
            Diagnoses(visit=new_visit, diagnosis=diag.diagnosis, detail=diag.detail)
        # Copy bloodpulse
        for bp in visit.bloodpulse:
            BloodPulse(visit=new_visit, time=bp.time, pulse=bp.pulse, systolic=bp.systolic, diastolic=bp.diastolic)
    # Handle PastHistory
    if PastHistory.exists(tz=old_tz):
        old_ph = PastHistory[old_tz]
        new_ph = PastHistory(tz=new_tz,
                             hypertension=old_ph.hypertension,
                             diabetes=old_ph.diabetes,
                             blood=old_ph.blood,
                             blood_descr=old_ph.blood_descr,
                             malignancy=old_ph.malignancy,
                             malignancy_date=old_ph.malignancy_date,
                             malignancy_details=old_ph.malignancy_details,
                             malignancy_remiss=old_ph.malignancy_remiss,
                             disable=old_ph.disable,
                             disable_details=old_ph.disable_details,
                             operations=old_ph.operations,
                             trauma=old_ph.trauma)
        # Update nacs and acs
        for nac in old_ph.nacs:
            Nac(pasthistory=new_ph, nac=nac.nac)
        for ac in old_ph.acs:
            Ac(pasthistory=new_ph, ac=ac.ac)
        old_ph.delete()
    # Delete old visits (after copying)
    delete(v for v in Visits if v.patient == old_patient)
    # Delete old patient
    old_patient.delete()
    return True
