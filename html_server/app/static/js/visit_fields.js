// Field/label/group data for the Visits form -- equivalent of
// Visits/UI/uiVisitsForm.py's hand-built Qt layout. Labels are transcribed
// from that file's widget constructors (e.g. QCheckBox("Trendelenberg, L")),
// not auto-generated, so the terminology matches what the Qt app shows.
//
// Each field descriptor is one of:
//   {type:"text", name, label}
//   {type:"textarea", name, label}
//   {type:"checkbox", name, label, children:[...]}  -- children are
//     disabled+reset when this checkbox is unchecked, enabled when checked
//     (equivalent of Qt's checkboxPairs / onCheckboxStateChanged pattern)
//   {type:"radio_bool", name, trueLabel, falseLabel}  -- only valid as a child
//   {type:"radio_string", name, options:[...], default}  -- only valid as a child
//
// Field names match Database.dbCreate's Visits entity columns exactly (see
// html_server/app/visits/field_lists.py, the Python-side source of truth
// for field order); this file only adds labels/grouping/UI structure on top.

const VISIT_TABS = [
  {
    id: "cc", label: "Current Complaint",
    groups: [
      { title: "General", fields: [
        { type: "text", name: "cc_onset", label: "Onset of Pain" },
        { type: "textarea", name: "cc_description", label: "Description of Pain" },
      ]},
      { title: "Aggravating Factors", fields: [
        { type: "checkbox", name: "cc_walking", label: "Walking", children: [
          { type: "text", name: "cc_walking_le", label: "" }] },
        { type: "checkbox", name: "cc_standing", label: "Standing", children: [
          { type: "text", name: "cc_standing_le", label: "" }] },
        { type: "checkbox", name: "cc_sitting", label: "Sitting", children: [
          { type: "text", name: "cc_sitting_le", label: "" }] },
        { type: "checkbox", name: "cc_lying", label: "Lying", children: [
          { type: "text", name: "cc_lying_le", label: "" }] },
        { type: "checkbox", name: "cc_lifting", label: "Lifting", children: [
          { type: "text", name: "cc_lifting_le", label: "" }] },
        { type: "checkbox", name: "cc_shoulder_move", label: "Shoulder Movement", children: [
          { type: "text", name: "cc_shoulder_move_le", label: "" }] },
      ]},
      { title: "Location", fields: [
        { type: "checkbox", name: "cc_loc_neck", label: "Neck" },
        { type: "checkbox", name: "cc_loc_spine", label: "Thoracic Spine" },
        { type: "checkbox", name: "cc_loc_back", label: "Lower Back" },
        { type: "checkbox", name: "cc_loc_shoulder_l", label: "Shoulder, L" },
        { type: "checkbox", name: "cc_loc_shoulder_r", label: "Shoulder, R" },
        { type: "checkbox", name: "cc_loc_hips_l", label: "Hip, L" },
        { type: "checkbox", name: "cc_loc_hips_r", label: "Hip, R" },
        { type: "checkbox", name: "cc_loc_groin_l", label: "Groin, L" },
        { type: "checkbox", name: "cc_loc_groin_r", label: "Groin, R" },
        { type: "checkbox", name: "cc_loc_knee_l", label: "Knee, L" },
        { type: "checkbox", name: "cc_loc_knee_r", label: "Knee, R" },
        { type: "checkbox", name: "cc_loc_ankle_l", label: "Ankle, L" },
        { type: "checkbox", name: "cc_loc_ankle_r", label: "Ankle, R" },
        { type: "checkbox", name: "cc_loc_other", label: "Other" },
        { type: "text", name: "cc_loc_radiates_le", label: "Radiates" },
        { type: "text", name: "cc_loc_precise_le", label: "Precise Location" },
      ]},
    ],
  },
  {
    id: "back", label: "Back",
    groups: [
      { title: "Examinations", fields: [
        { type: "text", name: "back_movement_le", label: "Movement" },
        { type: "checkbox", name: "back_trend_l", label: "Trendelenberg, L", children: [
          { type: "checkbox", name: "back_trend_l_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_trend_r", label: "Trendelenberg, R", children: [
          { type: "checkbox", name: "back_trend_r_pos", label: "+ve" }] },
        { type: "text", name: "back_slr_l_le", label: "SLR, L" },
        { type: "text", name: "back_slr_r_le", label: "SLR, R" },
        { type: "checkbox", name: "back_fst_l", label: "FST, L", children: [
          { type: "checkbox", name: "back_fst_l_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_fst_r", label: "FST, R", children: [
          { type: "checkbox", name: "back_fst_r_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_hip_l", label: "Passive Hip Flexion, L", children: [
          { type: "checkbox", name: "back_hip_l_pain", label: "Painful" }] },
        { type: "checkbox", name: "back_hip_r", label: "Passive Hip Flexion, R", children: [
          { type: "checkbox", name: "back_hip_r_pain", label: "Painful" }] },
        { type: "checkbox", name: "back_thigh_l", label: "Thigh Thrust, L", children: [
          { type: "checkbox", name: "back_thigh_l_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_thigh_r", label: "Thigh Thrust, R", children: [
          { type: "checkbox", name: "back_thigh_r_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_fabere_l", label: "Fabere, L", children: [
          { type: "checkbox", name: "back_fabere_l_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_fabere_r", label: "Fabere, R", children: [
          { type: "checkbox", name: "back_fabere_r_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_sensation", label: "Sensation", children: [
          { type: "checkbox", name: "back_sensation_equals", label: "L==R?" },
          { type: "text", name: "back_sensation_le", label: "" }] },
        { type: "checkbox", name: "back_power", label: "Power", children: [
          { type: "checkbox", name: "back_power_equals", label: "L==R?" },
          { type: "text", name: "back_power_le", label: "" }] },
        { type: "checkbox", name: "back_reflexes", label: "Reflexes", children: [
          { type: "checkbox", name: "back_reflexes_equals", label: "L==R?" },
          { type: "text", name: "back_reflexes_le", label: "" }] },
      ]},
      { title: "Resisted Hip", fields: [
        { type: "checkbox", name: "back_abduction_l", label: "Abduction, L", children: [
          { type: "checkbox", name: "back_abduction_l_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_abduction_r", label: "Abduction, R", children: [
          { type: "checkbox", name: "back_abduction_r_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_lat_rot_l", label: "Lateral Rotation, L", children: [
          { type: "checkbox", name: "back_lat_rot_l_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_lat_rot_r", label: "Lateral Rotation, R", children: [
          { type: "checkbox", name: "back_lat_rot_r_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_adduction_l", label: "Adduction, L", children: [
          { type: "checkbox", name: "back_adduction_l_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_adduction_r", label: "Adduction, R", children: [
          { type: "checkbox", name: "back_adduction_r_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_flexion_l", label: "Flexion, L", children: [
          { type: "checkbox", name: "back_flexion_l_pos", label: "+ve" }] },
        { type: "checkbox", name: "back_flexion_r", label: "Flexion, R", children: [
          { type: "checkbox", name: "back_flexion_r_pos", label: "+ve" }] },
        { type: "text", name: "back_tenderness_le", label: "Tenderness" },
      ]},
      { title: "Thoracic Spine", fields: [
        { type: "checkbox", name: "back_tspine_rot_l", label: "Thoracic Spine Rot L", children: [
          { type: "checkbox", name: "back_tspine_rot_l_pain", label: "Painful" }] },
        { type: "checkbox", name: "back_tspine_rot_r", label: "Thoracic Spine Rot R", children: [
          { type: "checkbox", name: "back_tspine_rot_r_pain", label: "Painful" }] },
        { type: "text", name: "back_tspine_tender_le", label: "Tenderness" },
      ]},
    ],
  },
  {
    id: "hip", label: "Hip",
    groups: [
      { title: "Hip Assessment", fields: [
        { type: "checkbox", name: "hip_pelvic_tilt", label: "Pelvic Tilt", children: [
          { type: "radio_string", name: "hip_pelvic_tilt_type",
            options: ["Normal", "Posterior", "Anterior"], default: "Normal" }] },
        { type: "checkbox", name: "hip_trend_l", label: "Trendelenberg, L", children: [
          { type: "checkbox", name: "hip_trend_l_pos", label: "+ve" }] },
        { type: "checkbox", name: "hip_trend_r", label: "Trendelenberg, R", children: [
          { type: "checkbox", name: "hip_trend_r_pos", label: "+ve" }] },
      ]},
      { title: "Hip Passive", fields: [
        { type: "text", name: "hip_passive_lat_rot_l_le", label: "Lateral Rotation, L" },
        { type: "text", name: "hip_passive_lat_rot_r_le", label: "Lateral Rotation, R" },
        { type: "text", name: "hip_passive_medial_rot_l_le", label: "Medial Rotation, L" },
        { type: "text", name: "hip_passive_medial_rot_r_le", label: "Medial Rotation, R" },
        { type: "text", name: "hip_passive_flexion_l_le", label: "Flexion, L" },
        { type: "text", name: "hip_passive_flexion_r_le", label: "Flexion, R" },
      ]},
      { title: "Hip Resisted", fields: [
        { type: "checkbox", name: "hip_resisted_abd_l", label: "Abduction, L", children: [
          { type: "checkbox", name: "hip_resisted_abd_l_limit", label: "Painful" }] },
        { type: "checkbox", name: "hip_resisted_abd_r", label: "Abduction, R", children: [
          { type: "checkbox", name: "hip_resisted_abd_r_limit", label: "Painful" }] },
        { type: "checkbox", name: "hip_resisted_lat_rot_l", label: "Lateral Rotation, L", children: [
          { type: "checkbox", name: "hip_resisted_lat_rot_l_limit", label: "Painful" }] },
        { type: "checkbox", name: "hip_resisted_lat_rot_r", label: "Lateral Rotation, R", children: [
          { type: "checkbox", name: "hip_resisted_lat_rot_r_limit", label: "Painful" }] },
        { type: "checkbox", name: "hip_resisted_med_rot_l", label: "Medial Rotation, L", children: [
          { type: "checkbox", name: "hip_resisted_med_rot_l_limit", label: "Painful" }] },
        { type: "checkbox", name: "hip_resisted_med_rot_r", label: "Medial Rotation, R", children: [
          { type: "checkbox", name: "hip_resisted_med_rot_r_limit", label: "Painful" }] },
        { type: "checkbox", name: "hip_resisted_adduction_l", label: "Adduction, L", children: [
          { type: "checkbox", name: "hip_resisted_adduction_l_limit", label: "Painful" }] },
        { type: "checkbox", name: "hip_resisted_adduction_r", label: "Adduction, R", children: [
          { type: "checkbox", name: "hip_resisted_adduction_r_limit", label: "Painful" }] },
      ]},
      { title: "Hip Other", fields: [
        { type: "text", name: "hip_tenderness", label: "Tenderness" },
        { type: "text", name: "hip_other", label: "Other" },
      ]},
    ],
  },
  {
    id: "neck", label: "Neck",
    groups: [
      { title: "Neck Examinations", fields: [
        { type: "text", name: "neck_extension_le", label: "Extension" },
        { type: "text", name: "neck_rotation_l_le", label: "Rotation, L" },
        { type: "text", name: "neck_rotation_r_le", label: "Rotation, R" },
        { type: "text", name: "neck_cranial_le", label: "Cranial Nerve" },
        { type: "checkbox", name: "neck_sensation", label: "Sensation", children: [
          { type: "checkbox", name: "neck_sensation_equals", label: "L==R" },
          { type: "text", name: "neck_sensation_le", label: "" }] },
        { type: "checkbox", name: "neck_power", label: "Power", children: [
          { type: "checkbox", name: "neck_power_equals", label: "L==R" },
          { type: "text", name: "neck_power_le", label: "" }] },
        { type: "checkbox", name: "neck_reflexes", label: "Reflexes", children: [
          { type: "checkbox", name: "neck_reflexes_equals", label: "L==R" },
          { type: "text", name: "neck_reflexes_le", label: "" }] },
        { type: "text", name: "neck_tenderness_le", label: "Tenderness" },
        { type: "text", name: "neck_other_le", label: "Other" },
      ]},
    ],
  },
  {
    id: "shoulder", label: "Shoulder",
    groups: [
      { title: "Scapular Motion", fields: [
        { type: "checkbox", name: "shoulder_align_l", label: "Alignment, L", children: [
          { type: "checkbox", name: "shoulder_align_l_ab", label: "Abnormal" },
          { type: "text", name: "shoulder_align_l_le", label: "" }] },
        { type: "checkbox", name: "shoulder_align_r", label: "Alignment, R", children: [
          { type: "checkbox", name: "shoulder_align_r_ab", label: "Abnormal" },
          { type: "text", name: "shoulder_align_r_le", label: "" }] },
        { type: "checkbox", name: "shoulder_rom_l", label: "ROM, L", children: [
          { type: "radio_bool", name: "shoulder_rom_l_full", trueLabel: "Full", falseLabel: "Limited" }] },
        { type: "checkbox", name: "shoulder_rom_r", label: "ROM, R", children: [
          { type: "radio_bool", name: "shoulder_rom_r_full", trueLabel: "Full", falseLabel: "Limited" }] },
      ]},
      { title: "Passive Shoulder Motion", fields: [
        { type: "text", name: "shoulder_passive_abduction_l_le", label: "Abduction, L" },
        { type: "text", name: "shoulder_passive_abduction_r_le", label: "Abduction, R" },
        { type: "text", name: "shoulder_passive_lat_rot_l_le", label: "Lat. Rotation, L" },
        { type: "text", name: "shoulder_passive_lat_rot_r_le", label: "Lat. Rotation, R" },
        { type: "checkbox", name: "shoulder_passive_med_rot_l", label: "Med. Rotation, L", children: [
          { type: "checkbox", name: "shoulder_passive_med_rot_l_limit", label: "Limited" },
          { type: "checkbox", name: "shoulder_passive_med_rot_l_pain", label: "Painful" }] },
        { type: "checkbox", name: "shoulder_passive_med_rot_r", label: "Med. Rotation, R", children: [
          { type: "checkbox", name: "shoulder_passive_med_rot_r_limit", label: "Limited" },
          { type: "checkbox", name: "shoulder_passive_med_rot_r_pain", label: "Painful" }] },
        { type: "checkbox", name: "shoulder_passive_adduction_l", label: "Adduction, L", children: [
          { type: "checkbox", name: "shoulder_passive_adduction_l_limit", label: "Limited" },
          { type: "checkbox", name: "shoulder_passive_adduction_l_pain", label: "Painful" }] },
        { type: "checkbox", name: "shoulder_passive_adduction_r", label: "Adduction, R", children: [
          { type: "checkbox", name: "shoulder_passive_adduction_r_limit", label: "Limited" },
          { type: "checkbox", name: "shoulder_passive_adduction_r_pain", label: "Painful" }] },
      ]},
      { title: "Resisted Shoulder Motion", fields: [
        { type: "text", name: "shoulder_resisted_abduction_l_le", label: "Abduction, L" },
        { type: "text", name: "shoulder_resisted_abduction_r_le", label: "Abduction, R" },
        { type: "text", name: "shoulder_resisted_lat_rot_l_le", label: "Lat. Rotation, L" },
        { type: "text", name: "shoulder_resisted_lat_rot_r_le", label: "Lat. Rotation, R" },
        { type: "checkbox", name: "shoulder_resisted_med_rot_l", label: "Med. Rotation, L", children: [
          { type: "checkbox", name: "shoulder_resisted_med_rot_l_limit", label: "Painful" }] },
        { type: "checkbox", name: "shoulder_resisted_med_rot_r", label: "Med. Rotation, R", children: [
          { type: "checkbox", name: "shoulder_resisted_med_rot_r_limit", label: "Painful" }] },
        { type: "checkbox", name: "shoulder_resisted_adduction_l", label: "Adduction, L", children: [
          { type: "checkbox", name: "shoulder_resisted_adduction_l_limit", label: "Painful" }] },
        { type: "checkbox", name: "shoulder_resisted_adduction_r", label: "Adduction, R", children: [
          { type: "checkbox", name: "shoulder_resisted_adduction_r_limit", label: "Painful" }] },
        { type: "checkbox", name: "shoulder_jobes_l", label: "Jobes, L", children: [
          { type: "checkbox", name: "shoulder_jobes_l_pos", label: "+ve" }] },
        { type: "checkbox", name: "shoulder_jobes_r", label: "Jobes, R", children: [
          { type: "checkbox", name: "shoulder_jobes_r_pos", label: "+ve" }] },
      ]},
    ],
  },
  {
    id: "knee_ankle", label: "Knee - Ankle",
    groups: [
      { title: "Knee", fields: [
        { type: "checkbox", name: "knee_scar_l", label: "Scarring Knee, L", children: [
          { type: "checkbox", name: "knee_scar_l_yes", label: "+ve" }] },
        { type: "checkbox", name: "knee_scar_r", label: "Scarring Knee, R", children: [
          { type: "checkbox", name: "knee_scar_r_yes", label: "+ve" }] },
        { type: "checkbox", name: "knee_align_l", label: "Alignment, L", children: [
          { type: "checkbox", name: "knee_align_l_ab", label: "Abnormal" },
          { type: "text", name: "knee_align_l_le", label: "" }] },
        { type: "checkbox", name: "knee_align_r", label: "Alignment, R", children: [
          { type: "checkbox", name: "knee_align_r_ab", label: "Abnormal" },
          { type: "text", name: "knee_align_r_le", label: "" }] },
        { type: "checkbox", name: "knee_muscle_l", label: "Muscle Wasting, L", children: [
          { type: "checkbox", name: "knee_muscle_l_yes", label: "+ve" }] },
        { type: "checkbox", name: "knee_muscle_r", label: "Muscle Wasting, R", children: [
          { type: "checkbox", name: "knee_muscle_r_yes", label: "+ve" }] },
        { type: "checkbox", name: "knee_effusion_l", label: "Effusion, L", children: [
          { type: "checkbox", name: "knee_effusion_l_yes", label: "+ve" }] },
        { type: "checkbox", name: "knee_effusion_r", label: "Effusion, R", children: [
          { type: "checkbox", name: "knee_effusion_r_yes", label: "+ve" }] },
        { type: "checkbox", name: "knee_res_ext_l", label: "Resisted Extension Pain, L", children: [
          { type: "checkbox", name: "knee_res_ext_l_yes", label: "+ve" }] },
        { type: "checkbox", name: "knee_res_ext_r", label: "Resisted Extension Pain, R", children: [
          { type: "checkbox", name: "knee_res_ext_r_yes", label: "+ve" }] },
        { type: "checkbox", name: "knee_res_flexion_l", label: "Resisted Flexion Pain, L", children: [
          { type: "checkbox", name: "knee_res_flexion_l_yes", label: "+ve" }] },
        { type: "checkbox", name: "knee_res_flexion_r", label: "Resisted Flexion Pain, R", children: [
          { type: "checkbox", name: "knee_res_flexion_r_yes", label: "+ve" }] },
        { type: "checkbox", name: "knee_macmurray_l", label: "Pos. McMurrays, L", children: [
          { type: "checkbox", name: "knee_macmurray_l_pos", label: "+ve" }] },
        { type: "checkbox", name: "knee_macmurray_r", label: "Pos. McMurrays, R", children: [
          { type: "checkbox", name: "knee_macmurray_r_pos", label: "+ve" }] },
        { type: "checkbox", name: "knee_grind_l", label: "Patelofemoral Grinding, L", children: [
          { type: "checkbox", name: "knee_grind_l_pos", label: "+ve" }] },
        { type: "checkbox", name: "knee_grind_r", label: "Patelofemoral Grinding, R", children: [
          { type: "checkbox", name: "knee_grind_r_pos", label: "+ve" }] },
        { type: "text", name: "knee_rom_l", label: "ROM, L" },
        { type: "text", name: "knee_rom_r", label: "ROM, R" },
        { type: "checkbox", name: "knee_mcl_l", label: "MCL, L", children: [
          { type: "checkbox", name: "knee_mcl_lax_l", label: "Lax." }] },
        { type: "checkbox", name: "knee_mcl_r", label: "MCL, R", children: [
          { type: "checkbox", name: "knee_mcl_lax_r", label: "Lax." }] },
        { type: "checkbox", name: "knee_lcl_l", label: "LCL, L", children: [
          { type: "checkbox", name: "knee_lcl_lax_l", label: "Lax." }] },
        { type: "checkbox", name: "knee_lcl_r", label: "LCL, R", children: [
          { type: "checkbox", name: "knee_lcl_lax_r", label: "Lax." }] },
        { type: "text", name: "knee_tender_l_le", label: "Tenderness L" },
        { type: "text", name: "knee_tender_r_le", label: "Tenderness R" },
        { type: "text", name: "knee_other_le", label: "Other" },
      ]},
      { title: "Ankle Joint", fields: [
        { type: "checkbox", name: "ankle_scar_l", label: "Scarring Ankle, L", children: [
          { type: "checkbox", name: "ankle_scar_l_yes", label: "+ve" }] },
        { type: "checkbox", name: "ankle_scar_r", label: "Scarring Ankle, R", children: [
          { type: "checkbox", name: "ankle_scar_r_yes", label: "+ve" }] },
        { type: "checkbox", name: "ankle_align_l", label: "Alignment L", children: [
          { type: "radio_bool", name: "ankle_align_l_pronated", trueLabel: "Pronated", falseLabel: "Supinated" }] },
        { type: "checkbox", name: "ankle_align_r", label: "Alignment R", children: [
          { type: "radio_bool", name: "ankle_align_r_pronated", trueLabel: "Pronated", falseLabel: "Supinated" }] },
        { type: "text", name: "ankle_dors_l_le", label: "Dorsflexion L" },
        { type: "text", name: "ankle_dors_r_le", label: "Dorsflexion R" },
        { type: "text", name: "ankle_plant_l_le", label: "Plantarflexion L" },
        { type: "text", name: "ankle_plant_r_le", label: "Plantarflexion R" },
        { type: "text", name: "ankle_inversion_l_le", label: "Inversion L" },
        { type: "text", name: "ankle_inversion_r_le", label: "Inversion R" },
        { type: "text", name: "ankle_eversion_l_le", label: "Eversion L" },
        { type: "text", name: "ankle_eversion_r_le", label: "Eversion R" },
        { type: "text", name: "ankle_tender_le_l", label: "Tender L" },
        { type: "text", name: "ankle_tender_le_r", label: "Tender R" },
      ]},
      { title: "Ankle Subtalar", fields: [
        { type: "checkbox", name: "anklest_addpain_l", label: "Adduction Painful, L", children: [
          { type: "checkbox", name: "anklest_addpain_yes_l", label: "+ve" }] },
        { type: "checkbox", name: "anklest_addpain_r", label: "Adduction Painful, R", children: [
          { type: "checkbox", name: "anklest_addpain_yes_r", label: "+ve" }] },
        { type: "checkbox", name: "anklest_abcpain_l", label: "Abduction Painful, L", children: [
          { type: "checkbox", name: "anklest_abcpain_yes_l", label: "+ve" }] },
        { type: "checkbox", name: "anklest_abcpain_r", label: "Abduction Painful, R", children: [
          { type: "checkbox", name: "anklest_abcpain_yes_r", label: "+ve" }] },
        { type: "checkbox", name: "anklest_addlimited_l", label: "Adduction Limited, L", children: [
          { type: "checkbox", name: "anklest_addlimited_yes_l", label: "+ve" }] },
        { type: "checkbox", name: "anklest_addlimited_r", label: "Adduction Limited, R", children: [
          { type: "checkbox", name: "anklest_addlimited_yes_r", label: "+ve" }] },
        { type: "checkbox", name: "anklest_abclimited_l", label: "Abduction Limited, L", children: [
          { type: "checkbox", name: "anklest_abclimited_yes_l", label: "+ve" }] },
        { type: "checkbox", name: "anklest_abclimited_r", label: "Abduction Limited, R", children: [
          { type: "checkbox", name: "anklest_abclimited_yes_r", label: "+ve" }] },
      ]},
    ],
  },
];

// Full-width single-textarea tabs, handled separately from VISIT_TABS in
// visits.js (each maps to one top-level VisitIn/VisitOut string field).
const VISIT_TEXT_TABS = [
  { id: "exam", label: "Examination", name: "examination" },
  { id: "tests", label: "Tests", name: "tests" },
  { id: "recommend", label: "Recommendations", name: "recommendation" },
];
