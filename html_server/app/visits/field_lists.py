"""Visits field-name-to-position mapping.

Database.dbFuncs.save_visit(tz, date, cc, loc, back, knee, ankle, anklest,
hip, neck, shoulder, exam, tests, procs, diags, recommend) takes each exam
section as a plain positional tuple/list -- there's no named-field API on
that side. These lists are the authoritative field order for each group,
transcribed directly from dbFuncs.py's own `v.<field> = <group>[i]`
assignment statements (not from the Qt UI's widget-construction order,
which contains a couple of unrelated *display* bugs -- e.g. back_trend_l
and back_trend_l_pos values get swapped when Visits/visits.py repopulates
the form fields for an existing visit). Both this schema's GET (read) and
PUT (write) paths use these same lists, so they're self-consistent
regardless of what the desktop app's UI does when redisplaying a visit.

Verified against dbFuncs.save_visit with an isolated round-trip
(save then re-read every field) before being relied on here.

hip_resisted_flexion_l/r, hip_resisted_extension_l/r, and
hip_passive_med_rot_l/r + hip_passive_flexion_l/r (the boolean variants)
exist as columns on Visits but are never read or written by save_visit or
by the Qt UI -- they're vestigial. Left out here too, to stay an exact
equivalent of what the desktop app actually does today.
"""

CC_FIELDS = [
    "cc_onset", "cc_description", "cc_walking", "cc_walking_le",
    "cc_standing", "cc_standing_le", "cc_sitting", "cc_sitting_le",
    "cc_lying", "cc_lying_le", "cc_lifting", "cc_lifting_le",
    "cc_shoulder_move", "cc_shoulder_move_le",
]

LOC_FIELDS = [
    "cc_loc_neck", "cc_loc_spine", "cc_loc_back",
    "cc_loc_shoulder_l", "cc_loc_shoulder_r",
    "cc_loc_hips_l", "cc_loc_hips_r",
    "cc_loc_groin_l", "cc_loc_groin_r",
    "cc_loc_knee_l", "cc_loc_knee_r",
    "cc_loc_ankle_l", "cc_loc_ankle_r", "cc_loc_other",
    "cc_loc_radiates_le", "cc_loc_precise_le",
]

BACK_FIELDS = [
    "back_trend_l", "back_trend_r", "back_trend_l_pos", "back_trend_r_pos",
    "back_slr_l_le", "back_slr_r_le",
    "back_hip_l", "back_hip_l_pain", "back_hip_r", "back_hip_r_pain",
    "back_thigh_l", "back_thigh_l_pos", "back_thigh_r", "back_thigh_r_pos",
    "back_fabere_l", "back_fabere_l_pos", "back_fabere_r", "back_fabere_r_pos",
    "back_sensation", "back_sensation_equals", "back_sensation_le",
    "back_power", "back_power_equals", "back_power_le",
    "back_reflexes", "back_reflexes_equals", "back_reflexes_le",
    "back_abduction_l", "back_abduction_l_pos", "back_abduction_r", "back_abduction_r_pos",
    "back_lat_rot_l", "back_lat_rot_l_pos", "back_lat_rot_r", "back_lat_rot_r_pos",
    "back_adduction_l", "back_adduction_l_pos", "back_adduction_r", "back_adduction_r_pos",
    "back_flexion_l", "back_flexion_l_pos", "back_flexion_r", "back_flexion_r_pos",
    "back_tenderness_le",
    "back_tspine_rot_l", "back_tspine_rot_l_pain", "back_tspine_rot_r", "back_tspine_rot_r_pain",
    "back_tspine_tender_le",
    "back_movement_le", "back_fst_l", "back_fst_l_pos", "back_fst_r", "back_fst_r_pos",
]

HIP_FIELDS = [
    "hip_pelvic_tilt", "hip_pelvic_tilt_type",
    "hip_trend_l", "hip_trend_r", "hip_trend_l_pos", "hip_trend_r_pos",
    "hip_passive_lat_rot_l_le", "hip_passive_lat_rot_r_le",
    "hip_passive_medial_rot_l_le", "hip_passive_medial_rot_r_le",
    "hip_passive_flexion_l_le", "hip_passive_flexion_r_le",
    "hip_resisted_abd_l", "hip_resisted_abd_l_limit", "hip_resisted_abd_r", "hip_resisted_abd_r_limit",
    "hip_resisted_lat_rot_l", "hip_resisted_lat_rot_l_limit", "hip_resisted_lat_rot_r", "hip_resisted_lat_rot_r_limit",
    "hip_resisted_med_rot_l", "hip_resisted_med_rot_l_limit", "hip_resisted_med_rot_r", "hip_resisted_med_rot_r_limit",
    "hip_resisted_adduction_l", "hip_resisted_adduction_l_limit", "hip_resisted_adduction_r", "hip_resisted_adduction_r_limit",
    "hip_tenderness", "hip_other",
]

NECK_FIELDS = [
    "neck_extension_le", "neck_rotation_l_le", "neck_rotation_r_le", "neck_cranial_le",
    "neck_sensation", "neck_sensation_equals", "neck_sensation_le",
    "neck_power", "neck_power_equals", "neck_power_le",
    "neck_reflexes", "neck_reflexes_equals", "neck_reflexes_le",
    "neck_tenderness_le", "neck_other_le",
]

SHOULDER_FIELDS = [
    "shoulder_align_l", "shoulder_align_l_ab", "shoulder_align_l_le",
    "shoulder_align_r", "shoulder_align_r_ab", "shoulder_align_r_le",
    "shoulder_rom_l", "shoulder_rom_l_full", "shoulder_rom_r", "shoulder_rom_r_full",
    "shoulder_passive_abduction_l_le", "shoulder_passive_abduction_r_le",
    "shoulder_passive_lat_rot_l_le", "shoulder_passive_lat_rot_r_le",
    "shoulder_passive_med_rot_l", "shoulder_passive_med_rot_l_limit",
    "shoulder_passive_med_rot_r", "shoulder_passive_med_rot_r_limit",
    "shoulder_passive_adduction_l", "shoulder_passive_adduction_l_limit",
    "shoulder_passive_adduction_r", "shoulder_passive_adduction_r_limit",
    "shoulder_resisted_abduction_l_le", "shoulder_resisted_abduction_r_le",
    "shoulder_resisted_lat_rot_l_le", "shoulder_resisted_lat_rot_r_le",
    "shoulder_resisted_med_rot_l", "shoulder_resisted_med_rot_l_limit",
    "shoulder_resisted_med_rot_r", "shoulder_resisted_med_rot_r_limit",
    "shoulder_resisted_adduction_l", "shoulder_resisted_adduction_l_limit",
    "shoulder_resisted_adduction_r", "shoulder_resisted_adduction_r_limit",
    "shoulder_jobes_l", "shoulder_jobes_l_pos", "shoulder_jobes_r", "shoulder_jobes_r_pos",
    "shoulder_passive_med_rot_l_pain", "shoulder_passive_med_rot_r_pain",
    "shoulder_passive_adduction_l_pain", "shoulder_passive_adduction_r_pain",
]

KNEE_FIELDS = [
    "knee_scar_l", "knee_scar_l_yes", "knee_scar_r", "knee_scar_r_yes",
    "knee_align_l", "knee_align_l_ab", "knee_align_l_le",
    "knee_align_r", "knee_align_r_ab", "knee_align_r_le",
    "knee_muscle_l", "knee_muscle_l_yes", "knee_muscle_r", "knee_muscle_r_yes",
    "knee_effusion_l", "knee_effusion_l_yes", "knee_effusion_r", "knee_effusion_r_yes",
    "knee_res_ext_l", "knee_res_ext_l_yes", "knee_res_ext_r", "knee_res_ext_r_yes",
    "knee_res_flexion_l", "knee_res_flexion_l_yes", "knee_res_flexion_r", "knee_res_flexion_r_yes",
    "knee_macmurray_l", "knee_macmurray_l_pos", "knee_macmurray_r", "knee_macmurray_r_pos",
    "knee_grind_l", "knee_grind_l_pos", "knee_grind_r", "knee_grind_r_pos",
    "knee_rom_l", "knee_rom_r",
    "knee_mcl_l", "knee_mcl_lax_l", "knee_mcl_r", "knee_mcl_lax_r",
    "knee_lcl_l", "knee_lcl_lax_l", "knee_lcl_r", "knee_lcl_lax_r",
    "knee_tender_l_le", "knee_tender_r_le", "knee_other_le",
]

ANKLE_FIELDS = [
    "ankle_scar_l", "ankle_scar_l_yes", "ankle_scar_r", "ankle_scar_r_yes",
    "ankle_align_l", "ankle_align_l_pronated", "ankle_align_r", "ankle_align_r_pronated",
    "ankle_dors_l_le", "ankle_dors_r_le", "ankle_plant_l_le", "ankle_plant_r_le",
    "ankle_inversion_l_le", "ankle_inversion_r_le", "ankle_eversion_l_le", "ankle_eversion_r_le",
    "ankle_tender_le_l", "ankle_tender_le_r",
]

ANKLEST_FIELDS = [
    "anklest_addpain_l", "anklest_addpain_yes_l", "anklest_addpain_r", "anklest_addpain_yes_r",
    "anklest_abcpain_l", "anklest_abcpain_yes_l", "anklest_abcpain_r", "anklest_abcpain_yes_r",
    "anklest_addlimited_l", "anklest_addlimited_yes_l", "anklest_addlimited_r", "anklest_addlimited_yes_r",
    "anklest_abclimited_l", "anklest_abclimited_yes_l", "anklest_abclimited_r", "anklest_abclimited_yes_r",
]

GROUPED_FIELDS = {
    "cc": CC_FIELDS,
    "loc": LOC_FIELDS,
    "back": BACK_FIELDS,
    "hip": HIP_FIELDS,
    "neck": NECK_FIELDS,
    "shoulder": SHOULDER_FIELDS,
    "knee": KNEE_FIELDS,
    "ankle": ANKLE_FIELDS,
    "anklest": ANKLEST_FIELDS,
}

ALL_SCALAR_FIELDS = [f for fields in GROUPED_FIELDS.values() for f in fields]

# Explicit string-typed fields (everything else in ALL_SCALAR_FIELDS is bool).
# Transcribed field-by-field from the Visits entity declarations in
# Database/dbCreate.py -- not inferred from naming, since a couple of
# fields (knee_rom_l/r, ankle_tender_le_l/r) don't follow the "_le" suffix
# convention the rest of the schema uses for free-text fields.
STR_FIELDS = {
    "cc_onset", "cc_description", "cc_walking_le", "cc_standing_le", "cc_sitting_le",
    "cc_lying_le", "cc_lifting_le", "cc_shoulder_move_le",
    "cc_loc_radiates_le", "cc_loc_precise_le",
    "back_slr_l_le", "back_slr_r_le", "back_sensation_le", "back_power_le", "back_reflexes_le",
    "back_tenderness_le", "back_tspine_tender_le", "back_movement_le",
    "hip_pelvic_tilt_type",
    "hip_passive_lat_rot_l_le", "hip_passive_lat_rot_r_le",
    "hip_passive_medial_rot_l_le", "hip_passive_medial_rot_r_le",
    "hip_passive_flexion_l_le", "hip_passive_flexion_r_le",
    "hip_tenderness", "hip_other",
    "neck_extension_le", "neck_rotation_l_le", "neck_rotation_r_le", "neck_cranial_le",
    "neck_sensation_le", "neck_power_le", "neck_reflexes_le", "neck_tenderness_le", "neck_other_le",
    "shoulder_align_l_le", "shoulder_align_r_le",
    "shoulder_passive_abduction_l_le", "shoulder_passive_abduction_r_le",
    "shoulder_passive_lat_rot_l_le", "shoulder_passive_lat_rot_r_le",
    "shoulder_resisted_abduction_l_le", "shoulder_resisted_abduction_r_le",
    "shoulder_resisted_lat_rot_l_le", "shoulder_resisted_lat_rot_r_le",
    "knee_align_l_le", "knee_align_r_le", "knee_rom_l", "knee_rom_r",
    "knee_tender_l_le", "knee_tender_r_le", "knee_other_le",
    "ankle_dors_l_le", "ankle_dors_r_le", "ankle_plant_l_le", "ankle_plant_r_le",
    "ankle_inversion_l_le", "ankle_inversion_r_le", "ankle_eversion_l_le", "ankle_eversion_r_le",
    "ankle_tender_le_l", "ankle_tender_le_r",
}

assert STR_FIELDS <= set(ALL_SCALAR_FIELDS)


def field_type(name: str) -> type:
    return str if name in STR_FIELDS else bool


def field_default(name: str):
    return "" if name in STR_FIELDS else False
