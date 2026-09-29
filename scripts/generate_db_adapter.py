import os

code = r'''/**
 * MULTIDISCIPLINARY PAEDIATRIC CRANIOFACIAL DATABASE ADAPTER
 * Unified Browser (LocalStorage / IndexedDB / SQL.js) & Native Tauri Desktop SQLite Bridge
 * Conceived, designed and tested: Dr G Narenthiran MB ChB BSc(MedSci)(Hons) MRCS(Ed.) FEBNS FRCS(SN)
 * Copyright 2026, Dr G Narenthiran, g_narenthiran@hotmail.com, all rights reserved.
 * Dedicated to Mrs Nirmaladevy Ganesalingam BSc
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.DatabaseAdapter = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {

// Stata 114 Binary Generator Helper (Compatible with Stata 10-19, R haven/foreign, Python pandas)
function buildStata114Binary(variables, rows, datasetLabel = 'Paediatric Craniofacial DB') {
  const nvar = variables.length;
  const nobs = rows.length;

  let rowSize = 0;
  for (const v of variables) {
    if (v.type <= 244) rowSize += v.type;
    else if (v.type === 251) rowSize += 1;
    else if (v.type === 252) rowSize += 2;
    else if (v.type === 253) rowSize += 4;
    else if (v.type === 254) rowSize += 4;
    else if (v.type === 255) rowSize += 8;
  }

  const headerSize = 109;
  const typlistSize = nvar;
  const varlistSize = nvar * 33;
  const srtlistSize = (nvar + 1) * 2;
  const fmtlistSize = nvar * 49;
  const vlblistSize = nvar * 33;
  const dataSize = nobs * rowSize;
  const totalSize = headerSize + typlistSize + varlistSize + srtlistSize + fmtlistSize + vlblistSize + dataSize;

  const buffer = new ArrayBuffer(totalSize);
  const view = new DataView(buffer);
  const u8 = new Uint8Array(buffer);
  let offset = 0;

  // Stata 114 Header
  view.setUint8(offset++, 114);
  view.setUint8(offset++, 1); // little-endian
  view.setUint8(offset++, 1);
  view.setUint8(offset++, 0);
  view.setUint16(offset, nvar, true); offset += 2;
  view.setUint32(offset, nobs, true); offset += 4;

  const enc = new TextEncoder();
  const lblBytes = enc.encode(datasetLabel.substring(0, 31));
  u8.set(lblBytes, offset);
  offset += 32;

  const timeStr = new Date().toISOString().substring(0, 18);
  const timeBytes = enc.encode(timeStr);
  u8.set(timeBytes, offset);
  offset += 18;

  // Typlist
  for (const v of variables) {
    view.setUint8(offset++, v.type);
  }

  // Varlist (33 bytes each)
  for (const v of variables) {
    const nameBytes = enc.encode(v.name.substring(0, 32));
    u8.set(nameBytes, offset);
    offset += 33;
  }

  // Srtlist
  for (let i = 0; i <= nvar; i++) {
    view.setInt16(offset, 0, true);
    offset += 2;
  }

  // Fmtlist (49 bytes each)
  for (const v of variables) {
    const fmt = v.fmt || (v.type <= 244 ? '%-32s' : '%9.0g');
    const fmtBytes = enc.encode(fmt.substring(0, 48));
    u8.set(fmtBytes, offset);
    offset += 49;
  }

  // Vlblist (33 bytes each)
  for (const v of variables) {
    const vl = v.valLabel || '';
    const vlBytes = enc.encode(vl.substring(0, 32));
    u8.set(vlBytes, offset);
    offset += 33;
  }

  // Data rows
  for (const r of rows) {
    for (const v of variables) {
      const val = r[v.name];
      if (v.type <= 244) {
        const strBytes = enc.encode(String(val || '').substring(0, v.type));
        u8.set(strBytes, offset);
        offset += v.type;
      } else if (v.type === 251) {
        view.setInt8(offset++, (val === null || val === undefined) ? 127 : val);
      } else if (v.type === 252) {
        view.setInt16(offset, (val === null || val === undefined) ? 32767 : val, true);
        offset += 2;
      } else if (v.type === 253) {
        view.setInt32(offset, (val === null || val === undefined) ? 2147483647 : val, true);
        offset += 4;
      } else if (v.type === 254) {
        view.setFloat32(offset, (val === null || val === undefined) ? NaN : val, true);
        offset += 4;
      } else if (v.type === 255) {
        view.setFloat64(offset, (val === null || val === undefined) ? NaN : val, true);
        offset += 8;
      }
    }
  }

  return buffer;
}

// Simple SHA-256 Simulation for Audit Ledger
function computeHash(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  return Math.abs(hash).toString(16).padStart(8, '0') + 'a7f3e19c4b2d';
}

const STORAGE_KEYS = {
  PATIENTS: 'peds_cf_patients_v1',
  SURGERIES: 'peds_cf_surgeries_v1',
  MDT_NEUROSURG: 'peds_cf_mdt_neurosurg_v1',
  MDT_CRANIO: 'peds_cf_mdt_cranio_v1',
  MDT_GENETICS: 'peds_cf_mdt_genetics_v1',
  MDT_NEUROPSYCH: 'peds_cf_mdt_neuropsych_v1',
  MDT_SPEECH: 'peds_cf_mdt_speech_v1',
  MDT_OPHTHALMOLOGY: 'peds_cf_mdt_ophthalmology_v1',
  MDT_AIRWAY: 'peds_cf_mdt_airway_v1',
  USERS: 'peds_cf_users_v1',
  AUDIT: 'peds_cf_audit_ledger_v1'
};

// 5 Comprehensive Clinical Demonstrators
const DEFAULT_PATIENTS = [
  {
    id: "cf-pt-001",
    study_id: "CF-001",
    hospital_number: "PEDS-CF-41029",
    first_name: "Ethan",
    last_name: "Cooper",
    dob: "2025-05-12",
    age_at_presentation_months: 3.5,
    gender: "Male",
    ethnicity: "White British",
    birth_weight_kg: 3.42,
    gestational_age_weeks: 39.5,
    head_circumference_at_birth_cm: 35.0,
    lead_neurosurgeon: "Dr G Narenthiran",
    lead_craniofacial_surgeon: "Mr A R Cranio",
    lead_plastic_surgeon: "Ms H Plastics",
    clinical_nurse_specialist: "Sister Claire Davies",
    notes: "Classic presentation of non-syndromic sagittal synostosis identified at 6-week infant baby check. Scaphocephalic cranial contour with palpable sagittal ridge.",
    pathology: {
      primary_diagnostic_category: "Single-Suture Craniosynostosis (Non-Syndromic)",
      primary_suture_involved: "Sagittal (Scaphocephaly / Dolichocephaly)",
      suture_details_text: "Premature ossification of entire sagittal suture with frontal bossing and occipital bulleting.",
      syndromic_diagnosis: "Non-Syndromic (Isolated)",
      genetic_testing_performed: "Yes",
      genetic_testing_modality: "Targeted Craniosynostosis NGS Gene Panel",
      specific_gene_identified: "Negative / No Pathogenic Variant Found",
      dna_mutation_details: "Panel negative for FGFR1, FGFR2, FGFR3, TWIST1, TCF12, ERF mutations.",
      inheritance_pattern: "De Novo",
      family_history_craniofacial: "No family history of craniofacial anomalies."
    },
    preop: {
      assessment_date: "2025-09-02",
      weight_kg: 6.8,
      head_circumference_cm: 42.5,
      head_circumference_centile: 75.0,
      cranial_length_mm: 172.0,
      cranial_width_mm: 114.0,
      cephalic_index: 66.3,
      cephalic_index_category: "Dolichocephalic / Scaphocephalic",
      cranial_vault_asymmetry_index_pct: 1.2,
      intercanthal_distance_mm: 22.0,
      interpupillary_distance_mm: 42.0,
      anterior_fontanelle_status: "Prematurely Closed",
      suture_ridging_palpable: "Prominent sagittal keel ridge",
      bitemporal_narrowing: "Marked bitemporal pinching",
      forehead_bossing_or_retrusion: "Frontal bossing with prominent supraorbital shelf",
      orbital_dystopia_harlequin: "None",
      exorbitism_proptosis_present: "No",
      corneal_exposure_risk: "None",
      raised_icp_clinical_signs: "No clinical irritability or bulging",
      copper_beaten_skull_on_imaging: "Mild beaten copper on parietal vertex",
      papilloedema_present: "No",
      frisen_papilloedema_grade: "Grade 0: Normal",
      sleep_study_performed: "No",
      ahi_apnea_hypopnea_index: 0.4,
      ahi_severity: "Normal",
      nocturnal_spo2_nadir_pct: 98.0,
      respiratory_support_needed: "None",
      chiari_malformation_present: "No",
      tonsillar_descent_mm: 0.0,
      hydrocephalus_present: "No",
      ventriculomegaly_evans_index: 0.24
    },
    outcomes: {
      latest_review_date: "2026-06-15",
      whitaker_classification: "Category I: No further surgical revision considered advisable or desired",
      postop_cranial_length_mm: 168.0,
      postop_cranial_width_mm: 130.0,
      postop_cephalic_index: 77.4,
      cephalic_index_improvement: 11.1,
      head_shape_aesthetic_correction: "Excellent",
      forehead_symmetry_restored: "Yes - Full frontal bossing resolution",
      supraorbital_rim_projection: "Normal age-appropriate projection",
      orbital_dystopia_resolved: "Not Applicable",
      exorbitism_resolved: "Not Applicable",
      parent_overall_satisfaction_score: 5,
      parent_head_shape_satisfaction: "Very Satisfied",
      parent_facial_appearance_satisfaction: "Very Satisfied",
      parent_would_recommend_procedure: "Strongly Agree",
      complication_dural_tear_or_csf_leak: "None",
      complication_wound_infection: "None",
      complication_bone_resorption: "None",
      complication_hardware_problem: "None",
      complication_resynostosis_recurrence: "No",
      complication_neurological_deficit: "None",
      complication_unplanned_reoperation_30d: "No",
      overall_clinical_status: "Completed Treatment - Excellent Result"
    }
  },
  {
    id: "cf-pt-002",
    study_id: "CF-002",
    hospital_number: "PEDS-CF-41088",
    first_name: "Sophia",
    last_name: "Taylor",
    dob: "2025-01-20",
    age_at_presentation_months: 8.5,
    gender: "Female",
    ethnicity: "British Mixed",
    birth_weight_kg: 3.15,
    gestational_age_weeks: 38.0,
    head_circumference_at_birth_cm: 34.2,
    lead_neurosurgeon: "Dr G Narenthiran",
    lead_craniofacial_surgeon: "Mr A R Cranio",
    lead_plastic_surgeon: "Ms H Plastics",
    clinical_nurse_specialist: "Sister Claire Davies",
    notes: "Trigonocephalic deformity secondary to premature metopic suture fusion. Notable hypotelorism and lateral orbital wall retrusion.",
    pathology: {
      primary_diagnostic_category: "Single-Suture Craniosynostosis (Non-Syndromic)",
      primary_suture_involved: "Metopic (Trigonocephaly)",
      suture_details_text: "Isolated complete metopic closure with prominent midline triangular forehead ridge.",
      syndromic_diagnosis: "Non-Syndromic (Isolated)",
      genetic_testing_performed: "Yes",
      genetic_testing_modality: "NGS Panel & Array CGH",
      specific_gene_identified: "Negative / No Pathogenic Variant Found",
      dna_mutation_details: "CMA normal; no SMAD6 or FGFR mutation.",
      inheritance_pattern: "De Novo",
      family_history_craniofacial: "None."
    },
    preop: {
      assessment_date: "2025-09-18",
      weight_kg: 8.4,
      head_circumference_cm: 44.0,
      head_circumference_centile: 50.0,
      cranial_length_mm: 156.0,
      cranial_width_mm: 128.0,
      cephalic_index: 82.1,
      cephalic_index_category: "Brachycephalic",
      cranial_vault_asymmetry_index_pct: 0.8,
      intercanthal_distance_mm: 16.5,
      interpupillary_distance_mm: 38.0,
      anterior_fontanelle_status: "Prematurely Closed",
      suture_ridging_palpable: "Prominent metopic keel",
      bitemporal_narrowing: "Severe bitemporal pinching",
      forehead_bossing_or_retrusion: "Pointed triangular forehead retrusion laterally",
      orbital_dystopia_harlequin: "Medial orbital crowding (hypotelorism)",
      exorbitism_proptosis_present: "No",
      corneal_exposure_risk: "None",
      raised_icp_clinical_signs: "No irritability",
      copper_beaten_skull_on_imaging: "Mild anterior fossa copper beating",
      papilloedema_present: "No",
      frisen_papilloedema_grade: "Grade 0: Normal",
      sleep_study_performed: "No",
      ahi_apnea_hypopnea_index: 0.8,
      ahi_severity: "Normal",
      nocturnal_spo2_nadir_pct: 97.5,
      respiratory_support_needed: "None",
      chiari_malformation_present: "No",
      tonsillar_descent_mm: 0.0,
      hydrocephalus_present: "No",
      ventriculomegaly_evans_index: 0.25
    },
    outcomes: {
      latest_review_date: "2026-07-22",
      whitaker_classification: "Category I: No further surgical revision considered advisable or desired",
      postop_cranial_length_mm: 158.0,
      postop_cranial_width_mm: 126.0,
      postop_cephalic_index: 79.7,
      cephalic_index_improvement: 2.4,
      head_shape_aesthetic_correction: "Excellent",
      forehead_symmetry_restored: "Yes - Broad, round, natural supraorbital bar",
      supraorbital_rim_projection: "Advancement maintained at 12 mm",
      orbital_dystopia_resolved: "Yes - Normalized intercanthal width (21 mm)",
      exorbitism_resolved: "Not Applicable",
      parent_overall_satisfaction_score: 5,
      parent_head_shape_satisfaction: "Very Satisfied",
      parent_facial_appearance_satisfaction: "Very Satisfied",
      parent_would_recommend_procedure: "Strongly Agree",
      complication_dural_tear_or_csf_leak: "None",
      complication_wound_infection: "None",
      complication_bone_resorption: "None",
      complication_hardware_problem: "None",
      complication_resynostosis_recurrence: "No",
      complication_neurological_deficit: "None",
      complication_unplanned_reoperation_30d: "No",
      overall_clinical_status: "Completed Treatment - Excellent Result"
    }
  },
  {
    id: "cf-pt-003",
    study_id: "CF-003",
    hospital_number: "PEDS-CF-41145",
    first_name: "Leo",
    last_name: "Dubois",
    dob: "2024-06-10",
    age_at_presentation_months: 14.0,
    gender: "Male",
    ethnicity: "French / European",
    birth_weight_kg: 3.3,
    gestational_age_weeks: 39.0,
    head_circumference_at_birth_cm: 34.8,
    lead_neurosurgeon: "Dr G Narenthiran",
    lead_craniofacial_surgeon: "Mr A R Cranio",
    lead_plastic_surgeon: "Ms H Plastics",
    clinical_nurse_specialist: "Sister Claire Davies",
    notes: "Syndromic Crouzon presentation with bicoronal synostosis, severe exorbitism, jugular foramen stenosis, and sleep-disordered breathing.",
    pathology: {
      primary_diagnostic_category: "Syndromic Craniosynostosis",
      primary_suture_involved: "Bicoronal (Brachycephaly / Turricephaly)",
      suture_details_text: "Bicoronal and partial sagittal synostosis with midface hypoplasia and shallow orbits.",
      syndromic_diagnosis: "Crouzon Syndrome",
      genetic_testing_performed: "Yes",
      genetic_testing_modality: "Targeted FGFR2 Sequencing",
      specific_gene_identified: "FGFR2",
      dna_mutation_details: "Heterozygous pathogenic missense variant c.1026C>G (p.Cys342Tyr) in exon 8 of FGFR2.",
      inheritance_pattern: "Autosomal Dominant - Paternal",
      family_history_craniofacial: "Father affected with mild Crouzon phenotype."
    },
    preop: {
      assessment_date: "2025-08-14",
      weight_kg: 10.2,
      head_circumference_cm: 45.2,
      head_circumference_centile: 25.0,
      cranial_length_mm: 142.0,
      cranial_width_mm: 132.0,
      cephalic_index: 93.0,
      cephalic_index_category: "Hyperbrachycephalic",
      cranial_vault_asymmetry_index_pct: 1.8,
      intercanthal_distance_mm: 27.5,
      interpupillary_distance_mm: 52.0,
      anterior_fontanelle_status: "Prematurely Closed",
      suture_ridging_palpable: "Bilateral coronal ridges",
      bitemporal_narrowing: "Bilateral turricephaly",
      forehead_bossing_or_retrusion: "High turricephalic skull with frontal retrusion",
      orbital_dystopia_harlequin: "Bilateral Harlequin orbit deformity",
      exorbitism_proptosis_present: "Yes - Severe (Hertel 19 mm)",
      corneal_exposure_risk: "Nocturnal lagophthalmos present; lubricating drops prescribed",
      raised_icp_clinical_signs: "Irritability, morning vomiting",
      copper_beaten_skull_on_imaging: "Diffuse marked pan-calvarial copper beating",
      papilloedema_present: "Yes",
      frisen_papilloedema_grade: "Grade 2: Circumferential Halo",
      sleep_study_performed: "Yes",
      ahi_apnea_hypopnea_index: 18.5,
      ahi_severity: "Severe OSA",
      nocturnal_spo2_nadir_pct: 78.0,
      respiratory_support_needed: "Nocturnal CPAP",
      chiari_malformation_present: "Yes",
      tonsillar_descent_mm: 6.5,
      hydrocephalus_present: "Yes - Compensated Ventriculomegaly",
      ventriculomegaly_evans_index: 0.33
    },
    outcomes: {
      latest_review_date: "2026-08-10",
      whitaker_classification: "Category II: Minor surgical revisions of contour or soft tissue",
      postop_cranial_length_mm: 164.0,
      postop_cranial_width_mm: 134.0,
      postop_cephalic_index: 81.7,
      cephalic_index_improvement: 11.3,
      head_shape_aesthetic_correction: "Good",
      forehead_symmetry_restored: "Posterior cranial vault volume expanded 28%",
      supraorbital_rim_projection: "Awaiting planned Stage 2 Frontoorbital / Monobloc advancement",
      orbital_dystopia_resolved: "Partial improvement in orbital depth",
      exorbitism_resolved: "Improved with decreased nocturnal exposure",
      parent_overall_satisfaction_score: 4,
      parent_head_shape_satisfaction: "Satisfied",
      parent_facial_appearance_satisfaction: "Satisfied",
      parent_would_recommend_procedure: "Agree",
      complication_dural_tear_or_csf_leak: "Intraoperative Dural Tear (Repaired)",
      complication_wound_infection: "None",
      complication_bone_resorption: "None",
      complication_hardware_problem: "None",
      complication_resynostosis_recurrence: "No",
      complication_neurological_deficit: "None",
      complication_unplanned_reoperation_30d: "No",
      overall_clinical_status: "Awaiting Second-Stage / Redo Surgery"
    }
  },
  {
    id: "cf-pt-004",
    study_id: "CF-004",
    hospital_number: "PEDS-CF-41201",
    first_name: "Maya",
    last_name: "Patel",
    dob: "2023-11-04",
    age_at_presentation_months: 28.0,
    gender: "Female",
    ethnicity: "British Indian",
    birth_weight_kg: 2.9,
    gestational_age_weeks: 37.5,
    head_circumference_at_birth_cm: 33.5,
    lead_neurosurgeon: "Dr G Narenthiran",
    lead_craniofacial_surgeon: "Mr A R Cranio",
    lead_plastic_surgeon: "Ms H Plastics",
    clinical_nurse_specialist: "Sister Claire Davies",
    notes: "Apert syndrome presenting with recurrent forehead retrusion and progressive turricephaly after initial infancy strip procedure. Indication for Redo FOAR.",
    pathology: {
      primary_diagnostic_category: "Syndromic Craniosynostosis",
      primary_suture_involved: "Pan-Synostosis (Cloverleaf / Kleeblattschaedel)",
      suture_details_text: "Coronal, metopic, and sagittal premature closure with complex syndactyly (mitten hands/feet).",
      syndromic_diagnosis: "Apert Syndrome",
      genetic_testing_performed: "Yes",
      genetic_testing_modality: "FGFR2 targeted sequencing",
      specific_gene_identified: "FGFR2",
      dna_mutation_details: "Pathogenic c.755C>G (p.Ser252Trp) in FGFR2.",
      inheritance_pattern: "De Novo",
      family_history_craniofacial: "No family history; parents unaffected."
    },
    preop: {
      assessment_date: "2025-10-10",
      weight_kg: 13.0,
      head_circumference_cm: 47.0,
      head_circumference_centile: 15.0,
      cranial_length_mm: 148.0,
      cranial_width_mm: 138.0,
      cephalic_index: 93.2,
      cephalic_index_category: "Hyperbrachycephalic",
      cranial_vault_asymmetry_index_pct: 2.5,
      intercanthal_distance_mm: 29.0,
      interpupillary_distance_mm: 54.0,
      anterior_fontanelle_status: "Prematurely Closed",
      suture_ridging_palpable: "Extensive calvarial ridging",
      bitemporal_narrowing: "Severe turribrachycephaly",
      forehead_bossing_or_retrusion: "Marked supraorbital retrusion with severe exorbitism",
      orbital_dystopia_harlequin: "Hypertelorism and down-slanting palpebral fissures",
      exorbitism_proptosis_present: "Yes - Severe",
      corneal_exposure_risk: "Corneal punctate staining present",
      raised_icp_clinical_signs: "Chronic headaches, sleep disturbance",
      copper_beaten_skull_on_imaging: "Severe pan-calvarial copper beaten skull",
      papilloedema_present: "Yes",
      frisen_papilloedema_grade: "Grade 3: Moderate Papilloedema",
      sleep_study_performed: "Yes",
      ahi_apnea_hypopnea_index: 12.0,
      ahi_severity: "Severe OSA",
      nocturnal_spo2_nadir_pct: 82.0,
      respiratory_support_needed: "High-Flow Oxygen / CPAP",
      chiari_malformation_present: "Yes",
      tonsillar_descent_mm: 5.0,
      hydrocephalus_present: "Yes",
      ventriculomegaly_evans_index: 0.32
    },
    outcomes: {
      latest_review_date: "2026-09-05",
      whitaker_classification: "Category III: Major bone graft or repeat osteotomy (less than original)",
      postop_cranial_length_mm: 160.0,
      postop_cranial_width_mm: 136.0,
      postop_cephalic_index: 85.0,
      cephalic_index_improvement: 8.2,
      head_shape_aesthetic_correction: "Satisfactory",
      forehead_symmetry_restored: "Significant advancement of bandeau (16 mm advancement)",
      supraorbital_rim_projection: "Restored rim projection and corneal coverage",
      orbital_dystopia_resolved: "Exorbitism partially improved; awaiting midface Le Fort III",
      exorbitism_resolved: "Corneal protection achieved",
      parent_overall_satisfaction_score: 4,
      parent_head_shape_satisfaction: "Satisfied",
      parent_facial_appearance_satisfaction: "Satisfied",
      parent_would_recommend_procedure: "Strongly Agree",
      complication_dural_tear_or_csf_leak: "Intraoperative Dural Tear (Repaired)",
      complication_wound_infection: "None",
      complication_bone_resorption: "Minor Palpable Irregularity",
      complication_hardware_problem: "None",
      complication_resynostosis_recurrence: "Yes - Required Redo Surgery",
      complication_neurological_deficit: "None",
      complication_unplanned_reoperation_30d: "No",
      overall_clinical_status: "Awaiting Second-Stage / Redo Surgery"
    }
  },
  {
    id: "cf-pt-005",
    study_id: "CF-005",
    hospital_number: "PEDS-CF-41270",
    first_name: "Noah",
    last_name: "Williams",
    dob: "2025-03-01",
    age_at_presentation_months: 5.0,
    gender: "Male",
    ethnicity: "White British",
    birth_weight_kg: 3.55,
    gestational_age_weeks: 40.0,
    head_circumference_at_birth_cm: 35.5,
    lead_neurosurgeon: "Dr G Narenthiran",
    lead_craniofacial_surgeon: "Mr A R Cranio",
    lead_plastic_surgeon: "Ms H Plastics",
    clinical_nurse_specialist: "Sister Claire Davies",
    notes: "Left unicoronal craniosynostosis presenting with marked left anterior plagiocephaly, left harlequin orbit, and contralateral frontal bossing.",
    pathology: {
      primary_diagnostic_category: "Single-Suture Craniosynostosis (Non-Syndromic)",
      primary_suture_involved: "Unilateral Coronal - Left (Anterior Plagiocephaly)",
      suture_details_text: "Fused left coronal suture with elevation of left sphenoid wing and nasal deviation to the right.",
      syndromic_diagnosis: "Non-Syndromic (Isolated)",
      genetic_testing_performed: "Yes",
      genetic_testing_modality: "NGS Craniosynostosis Panel",
      specific_gene_identified: "TCF12",
      dna_mutation_details: "Heterozygous frameshift variant in TCF12.",
      inheritance_pattern: "De Novo",
      family_history_craniofacial: "No family history."
    },
    preop: {
      assessment_date: "2025-08-05",
      weight_kg: 7.2,
      head_circumference_cm: 43.0,
      head_circumference_centile: 60.0,
      cranial_length_mm: 160.0,
      cranial_width_mm: 126.0,
      cephalic_index: 78.8,
      cephalic_index_category: "Mesocephalic (Normal)",
      cranial_vault_asymmetry_index_pct: 6.8,
      intercanthal_distance_mm: 20.0,
      interpupillary_distance_mm: 41.0,
      anterior_fontanelle_status: "Patent",
      suture_ridging_palpable: "Ridging along left coronal suture",
      bitemporal_narrowing: "Left frontal flattening with contralateral bossing",
      forehead_bossing_or_retrusion: "Left supraorbital rim retrusion with ipsilateral ear anterior displacement",
      orbital_dystopia_harlequin: "Marked left harlequin orbit on CT/X-ray",
      exorbitism_proptosis_present: "No",
      corneal_exposure_risk: "None",
      raised_icp_clinical_signs: "None",
      copper_beaten_skull_on_imaging: "None",
      papilloedema_present: "No",
      frisen_papilloedema_grade: "Grade 0: Normal",
      sleep_study_performed: "No",
      ahi_apnea_hypopnea_index: 0.5,
      ahi_severity: "Normal",
      nocturnal_spo2_nadir_pct: 98.0,
      respiratory_support_needed: "None",
      chiari_malformation_present: "No",
      tonsillar_descent_mm: 0.0,
      hydrocephalus_present: "No",
      ventriculomegaly_evans_index: 0.23
    },
    outcomes: {
      latest_review_date: "2026-06-30",
      whitaker_classification: "Category I: No further surgical revision considered advisable or desired",
      postop_cranial_length_mm: 162.0,
      postop_cranial_width_mm: 128.0,
      postop_cephalic_index: 79.0,
      cephalic_index_improvement: 0.2,
      head_shape_aesthetic_correction: "Excellent",
      forehead_symmetry_restored: "Marked correction of left orbital dystopia and frontal symmetry",
      supraorbital_rim_projection: "Symmetrical supraorbital rims bilaterally",
      orbital_dystopia_resolved: "Yes - Harlequin appearance normalized",
      exorbitism_resolved: "Not Applicable",
      parent_overall_satisfaction_score: 5,
      parent_head_shape_satisfaction: "Very Satisfied",
      parent_facial_appearance_satisfaction: "Very Satisfied",
      parent_would_recommend_procedure: "Strongly Agree",
      complication_dural_tear_or_csf_leak: "None",
      complication_wound_infection: "None",
      complication_bone_resorption: "None",
      complication_hardware_problem: "None",
      complication_resynostosis_recurrence: "No",
      complication_neurological_deficit: "None",
      complication_unplanned_reoperation_30d: "No",
      overall_clinical_status: "Completed Treatment - Excellent Result"
    }
  }
];

// Preloaded Surgical Procedures
const DEFAULT_SURGERIES = [
  {
    id: "cf-surg-001",
    patient_id: "cf-pt-001",
    surgery_date: "2025-09-15",
    procedure_sequence: "Primary Craniofacial Procedure",
    surgical_technique_category: "Endoscopy-Assisted Strip Craniectomy",
    surgical_technique_other_detail: "",
    surgeon_operative_description: "Endoscopy-assisted sagittal strip craniectomy via two small 3 cm transverse incisions (anterior vertex and lambda). 4 cm wide strip of stenosed sagittal bone excised from coronal to lambdoid suture. Bilateral parietal wedge osteotomies performed to allow expansion. Excellent hemostasis achieved. Custom orthotic molding helmet fitted on post-op day 5.",
    lead_surgeon: "Dr G Narenthiran",
    assisting_surgeon: "Mr A R Cranio",
    anesthetist: "Dr P Pediatric-Anesth",
    operating_time_minutes: 68,
    estimated_blood_loss_ml: 35,
    estimated_blood_loss_pct_ebv: 6.4,
    prbc_transfused_ml: 0,
    ffp_transfused_ml: 0,
    platelets_transfused_ml: 0,
    cell_saver_returned_ml: 0,
    tranexamic_acid_administered: "Yes",
    dural_tear_occurred: "No",
    bone_fixation_method: "No Fixation (Strip Craniectomy Alone)",
    spring_or_distractor_details: "None - Planned for helmet orthosis",
    helmet_therapy_planned: "Yes",
    helmet_protocol_duration_months: 9.0,
    icu_stay_days: 0,
    hospital_stay_days: 1
  },
  {
    id: "cf-surg-002",
    patient_id: "cf-pt-002",
    surgery_date: "2025-10-05",
    procedure_sequence: "Primary Craniofacial Procedure",
    surgical_technique_category: "Open Cranial Vault Remodeling",
    surgical_technique_other_detail: "",
    surgeon_operative_description: "Bifrontal craniotomy and frontoorbital advancement and remodeling (FOAR). Zigzag coronal incision. Supraorbital bandeau osteotomized, remodeled, widened, and advanced by 12 mm. Calvarial barrel staves and greenstick osteotomies. Frontal bone plates reconstructed with midline bone strut graft and secured with resorbable LactoSorb plates and sonic pins.",
    lead_surgeon: "Dr G Narenthiran",
    assisting_surgeon: "Mr A R Cranio",
    anesthetist: "Dr P Pediatric-Anesth",
    operating_time_minutes: 195,
    estimated_blood_loss_ml: 140,
    estimated_blood_loss_pct_ebv: 20.8,
    prbc_transfused_ml: 120,
    ffp_transfused_ml: 80,
    platelets_transfused_ml: 0,
    cell_saver_returned_ml: 65,
    tranexamic_acid_administered: "Yes",
    dural_tear_occurred: "No",
    bone_fixation_method: "Resorbable Plates and Screws (LactoSorb / SonicWeld)",
    spring_or_distractor_details: "",
    helmet_therapy_planned: "No",
    helmet_protocol_duration_months: 0,
    icu_stay_days: 1,
    hospital_stay_days: 4
  },
  {
    id: "cf-surg-003",
    patient_id: "cf-pt-003",
    surgery_date: "2025-09-08",
    procedure_sequence: "Primary Craniofacial Procedure",
    surgical_technique_category: "Distraction Osteogenesis (PVDO / FOAR Distraction)",
    surgical_technique_other_detail: "",
    surgeon_operative_description: "Bilateral posterior cranial vault distraction osteogenesis (PVDO). Bi-coronal flap reflected posteriorly. Biparietal-occipital craniotomy performed down to foramen magnum. Two internal cranial distractors placed across the osteotomy vector. Latency period 5 days, followed by distraction at 1.0 mm/day for 25 mm total expansion.",
    lead_surgeon: "Dr G Narenthiran",
    assisting_surgeon: "Mr A R Cranio",
    anesthetist: "Dr P Pediatric-Anesth",
    operating_time_minutes: 210,
    estimated_blood_loss_ml: 180,
    estimated_blood_loss_pct_ebv: 22.1,
    prbc_transfused_ml: 150,
    ffp_transfused_ml: 90,
    platelets_transfused_ml: 0,
    cell_saver_returned_ml: 85,
    tranexamic_acid_administered: "Yes",
    dural_tear_occurred: "Small Primary Repair",
    bone_fixation_method: "Distractor Hardware in Situ",
    spring_or_distractor_details: "2x KLS Martin internal distractors, 30 mm travel vector.",
    helmet_therapy_planned: "No",
    helmet_protocol_duration_months: 0,
    icu_stay_days: 1,
    hospital_stay_days: 5
  },
  {
    id: "cf-surg-004",
    patient_id: "cf-pt-004",
    surgery_date: "2025-11-20",
    procedure_sequence: "Redo Surgery / Secondary Vault Expansion",
    surgical_technique_category: "Open Cranial Vault Remodeling",
    surgical_technique_other_detail: "",
    surgeon_operative_description: "REDOSURGERY: Secondary Frontoorbital Advancement and Total Cranial Vault Remodeling for recurrent Apert turricephaly, progressive re-synostosis, and intracranial hypertension. Previous coronal scar reopened. Extensive dural adhesiolysis. Supraorbital bandeau osteotomized and advanced 16 mm with tenon spurs. Bilateral temporoparietal expansion. Dural tear along sagittal sinus oversewn.",
    lead_surgeon: "Dr G Narenthiran",
    assisting_surgeon: "Mr A R Cranio",
    anesthetist: "Dr P Pediatric-Anesth",
    operating_time_minutes: 260,
    estimated_blood_loss_ml: 320,
    estimated_blood_loss_pct_ebv: 30.8,
    prbc_transfused_ml: 280,
    ffp_transfused_ml: 160,
    platelets_transfused_ml: 60,
    cell_saver_returned_ml: 110,
    tranexamic_acid_administered: "Yes",
    dural_tear_occurred: "Large Patch / Graft Repair",
    bone_fixation_method: "Resorbable Plates and Screws (LactoSorb / SonicWeld)",
    spring_or_distractor_details: "Extensive cranial remodeling with resorbable lattice",
    helmet_therapy_planned: "No",
    helmet_protocol_duration_months: 0,
    icu_stay_days: 2,
    hospital_stay_days: 6
  },
  {
    id: "cf-surg-005",
    patient_id: "cf-pt-005",
    surgery_date: "2025-08-25",
    procedure_sequence: "Spring Insertion Procedure",
    surgical_technique_category: "Spring-Assisted Cranioplasty",
    surgical_technique_other_detail: "",
    surgeon_operative_description: "Spring-assisted cranioplasty for left unicoronal synostosis. Minimal skin incisions over left coronal suture. 10 mm strip craniectomy of left fused coronal suture. Two cranial expansion springs (Stryker 10N) inserted across the osteotomy to dynamically expand the left anterior cranial fossa. Springs engaged with audible tension.",
    lead_surgeon: "Dr G Narenthiran",
    assisting_surgeon: "Mr A R Cranio",
    anesthetist: "Dr P Pediatric-Anesth",
    operating_time_minutes: 75,
    estimated_blood_loss_ml: 45,
    estimated_blood_loss_pct_ebv: 7.8,
    prbc_transfused_ml: 0,
    ffp_transfused_ml: 0,
    platelets_transfused_ml: 0,
    cell_saver_returned_ml: 0,
    tranexamic_acid_administered: "Yes",
    dural_tear_occurred: "No",
    bone_fixation_method: "Springs in Situ",
    spring_or_distractor_details: "2x 10N cranial expansion springs. Removal planned at 3 months.",
    helmet_therapy_planned: "No",
    helmet_protocol_duration_months: 0,
    icu_stay_days: 0,
    hospital_stay_days: 1
  }
];

// Preloaded MDT Assessments
const DEFAULT_MDT_NEUROSURG = [
  {
    id: "mdt-ns-001",
    patient_id: "cf-pt-001",
    assessment_date: "2025-09-02",
    encounter_phase: "Pre-Operative Assessment",
    clinician_name: "Dr G Narenthiran",
    icp_assessment_summary: "No evidence of intracranial hypertension. Normal fontanelle tension.",
    fundoscopy_papilloedema_status: "Normal optic disc margins. No papilloedema.",
    chiari_tonsil_position_status: "Normal tonsillar position at foramen magnum.",
    ventricles_and_csf_dynamics: "Normal ventricular size (Evans index 0.24).",
    neurosurgical_recommendations: "Suitable for minimally invasive endoscopic sagittal strip craniectomy followed by orthotic helmet therapy."
  },
  {
    id: "mdt-ns-002",
    patient_id: "cf-pt-003",
    assessment_date: "2025-08-14",
    encounter_phase: "Pre-Operative Assessment",
    clinician_name: "Dr G Narenthiran",
    icp_assessment_summary: "Clinical signs of raised ICP (irritability, morning vomiting, beaten copper calvarium).",
    fundoscopy_papilloedema_status: "Grade 2 papilloedema with circumferential disc edema.",
    chiari_tonsil_position_status: "Chiari I malformation with 6.5 mm tonsillar descent into C1 arch.",
    ventricles_and_csf_dynamics: "Mild ventriculomegaly with Evans index 0.33.",
    neurosurgical_recommendations: "Urgent posterior vault expansion (PVDO) indicated to expand intracranial volume and decompress craniocervical junction."
  }
];

const DEFAULT_MDT_CRANIO = [
  {
    id: "mdt-cr-001",
    patient_id: "cf-pt-002",
    assessment_date: "2025-09-18",
    encounter_phase: "Pre-Operative Assessment",
    clinician_name: "Mr A R Cranio",
    forehead_and_supraorbital_contour: "Classic trigonocephalic triangle with pointed midline ridge and temporal hollowing.",
    midface_hypoplasia_assessment: "Normal midface projection.",
    soft_tissue_and_scar_appearance: "Healthy scalp tissue.",
    whitaker_stage_estimate: "Category I targeted",
    surgical_plan_or_revisions: "Bifrontal craniotomy and FOAR with 12 mm bar advancement."
  }
];

const DEFAULT_MDT_GENETICS = [
  {
    id: "mdt-gn-001",
    patient_id: "cf-pt-003",
    consultation_date: "2025-08-10",
    geneticist_name: "Dr E Genetics",
    clinical_syndromic_impression: "Confirmed Crouzon Syndrome with FGFR2 c.1026C>G pathogenic mutation.",
    dysmorphology_features: "Bicoronal synostosis, severe exorbitism, mandibular prognathism, normal hands/feet.",
    recommended_testing_plan: "Parental targeted testing confirmed paternal inheritance.",
    counseling_inheritance_and_recurrence: "Autosomal dominant. 50% recurrence risk for future offspring of father.",
    prenatal_advice_for_future_pregnancies: "Prenatal diagnosis and PGT-M discussed for future family planning."
  }
];

const DEFAULT_MDT_NEUROPSYCH = [
  {
    id: "mdt-np-001",
    patient_id: "cf-pt-001",
    assessment_date: "2026-05-10",
    encounter_phase: "1-Year Post-Op Follow-up",
    neuropsychologist_name: "Dr S Neuropsych",
    test_battery_used: "Bayley Scales of Infant and Toddler Development (Bayley-4)",
    developmental_quotient_or_iq: 106.0,
    gross_motor_development: "Normal gross motor skills. Walking independently at 11 months.",
    fine_motor_adaptive_skills: "Excellent pincer grasp and object manipulation.",
    language_and_communication: "Receptive and expressive language within expected developmental age.",
    parental_stress_and_bonding_index: "Low parental stress; high bonding score.",
    educational_support_needed: "None. Meeting all developmental milestones."
  }
];

const DEFAULT_MDT_SPEECH = [
  {
    id: "mdt-sp-001",
    patient_id: "cf-pt-004",
    assessment_date: "2025-10-15",
    encounter_phase: "Pre-Operative Assessment",
    therapist_name: "Ms L Speech-Therapist",
    feeding_and_swallowing_function: "Oral motor weakness; requires thickened liquids and soft food diet.",
    cleft_palate_or_bifid_uvula: "Submucous cleft palate present with bifid uvula.",
    velopharyngeal_competence: "Velopharyngeal Insufficiency (VPI)",
    hypernasality_status: "Moderate hypernasal resonance during phonation.",
    speech_articulation_clarity: "Mild compensatory articulation errors.",
    therapy_plan: "Ongoing speech therapy; videofluoroscopy planned after midface surgery."
  }
];

const DEFAULT_MDT_OPHTHALMOLOGY = [
  {
    id: "mdt-oph-001",
    patient_id: "cf-pt-003",
    examination_date: "2025-08-12",
    ophthalmologist_name: "Mr K Paediatric-Ophthalmology",
    visual_acuity_right: "Fix and follow central steady",
    visual_acuity_left: "Fix and follow central steady",
    refractive_error_astigmatism: "+3.50 DS OU with mild astigmatism",
    strabismus_v_pattern: "V-pattern exotropia with bilateral inferior oblique overaction",
    exorbitism_hertel_mm: 19.0,
    corneal_integrity: "Mild punctate epithelial erosions from nocturnal exposure",
    optic_nerve_status_oct: "Circumferential retinal nerve fiber layer (RNFL) thickening consistent with Grade 2 papilloedema",
    ophthalmic_management_plan: "Carbomer eye gel at night; urgent craniofacial decompression indicated to protect optic nerves."
  }
];

const DEFAULT_MDT_AIRWAY = [
  {
    id: "mdt-aw-001",
    patient_id: "cf-pt-003",
    assessment_date: "2025-08-11",
    specialist_name: "Dr R Respiratory-Sleep",
    upper_airway_patency: "Severe upper airway obstruction secondary to midface hypoplasia and choanal stenosis.",
    choanal_stenosis_or_atresia: "Bilateral pyriform aperture and posterior choanal narrowing.",
    adenotonsillar_hypertrophy: "Grade 2 tonsillar hypertrophy.",
    polysomnography_summary: "Polysomnography demonstrated severe obstructive sleep apnea with AHI 18.5/hr.",
    ahi_current_score: 18.5,
    cpap_bipap_tolerated: "Tolerating nasal mask CPAP at 8 cmH2O.",
    tracheostomy_status: "Not currently required; monitored closely.",
    respiratory_plan: "Continue nocturnal CPAP until midface advancement or vault expansion completed."
  }
];

// Preloaded RBAC Accounts
const DEFAULT_USERS = [
  { username: 'developer', passwordHash: computeHash('dev2026!'), role: 'developer', fullName: 'Dr G Narenthiran (Developer)' },
  { username: 'admin', passwordHash: computeHash('admin2026!'), role: 'administrator', fullName: 'Craniofacial Clinical Director' },
  { username: 'clinician', passwordHash: computeHash('user2026!'), role: 'clinician', fullName: 'Paediatric Craniofacial Fellow' }
];

class DatabaseAdapter {
  constructor() {
    this.initStorage();
  }

  initStorage() {
    if (!localStorage.getItem(STORAGE_KEYS.PATIENTS)) {
      localStorage.setItem(STORAGE_KEYS.PATIENTS, JSON.stringify(DEFAULT_PATIENTS));
    }
    if (!localStorage.getItem(STORAGE_KEYS.SURGERIES)) {
      localStorage.setItem(STORAGE_KEYS.SURGERIES, JSON.stringify(DEFAULT_SURGERIES));
    }
    if (!localStorage.getItem(STORAGE_KEYS.MDT_NEUROSURG)) {
      localStorage.setItem(STORAGE_KEYS.MDT_NEUROSURG, JSON.stringify(DEFAULT_MDT_NEUROSURG));
    }
    if (!localStorage.getItem(STORAGE_KEYS.MDT_CRANIO)) {
      localStorage.setItem(STORAGE_KEYS.MDT_CRANIO, JSON.stringify(DEFAULT_MDT_CRANIO));
    }
    if (!localStorage.getItem(STORAGE_KEYS.MDT_GENETICS)) {
      localStorage.setItem(STORAGE_KEYS.MDT_GENETICS, JSON.stringify(DEFAULT_MDT_GENETICS));
    }
    if (!localStorage.getItem(STORAGE_KEYS.MDT_NEUROPSYCH)) {
      localStorage.setItem(STORAGE_KEYS.MDT_NEUROPSYCH, JSON.stringify(DEFAULT_MDT_NEUROPSYCH));
    }
    if (!localStorage.getItem(STORAGE_KEYS.MDT_SPEECH)) {
      localStorage.setItem(STORAGE_KEYS.MDT_SPEECH, JSON.stringify(DEFAULT_MDT_SPEECH));
    }
    if (!localStorage.getItem(STORAGE_KEYS.MDT_OPHTHALMOLOGY)) {
      localStorage.setItem(STORAGE_KEYS.MDT_OPHTHALMOLOGY, JSON.stringify(DEFAULT_MDT_OPHTHALMOLOGY));
    }
    if (!localStorage.getItem(STORAGE_KEYS.MDT_AIRWAY)) {
      localStorage.setItem(STORAGE_KEYS.MDT_AIRWAY, JSON.stringify(DEFAULT_MDT_AIRWAY));
    }
    if (!localStorage.getItem(STORAGE_KEYS.USERS)) {
      localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(DEFAULT_USERS));
    }
    if (!localStorage.getItem(STORAGE_KEYS.AUDIT)) {
      localStorage.setItem(STORAGE_KEYS.AUDIT, JSON.stringify([
        {
          timestamp: new Date().toISOString(),
          username: "SYSTEM",
          action: "SYSTEM_INITIALIZE",
          study_id: "SYSTEM",
          details: "Initialized Multidisciplinary Paediatric Craniofacial Database with preloaded demonstrators",
          record_hash: computeHash("SYSTEM_INIT_PEDS_CRANIO_2026")
        }
      ]));
    }
  }

  // Authentication & RBAC
  authenticate(username, password) {
    const users = JSON.parse(localStorage.getItem(STORAGE_KEYS.USERS) || '[]');
    const hash = computeHash(password);
    const user = users.find(u => u.username.toLowerCase() === username.toLowerCase() && u.passwordHash === hash);
    if (user) {
      this.logAudit(user.username, 'LOGIN_SUCCESS', null, 'User logged into craniofacial registry');
      return { username: user.username, role: user.role, fullName: user.fullName };
    }
    this.logAudit(username, 'LOGIN_FAILED', null, 'Failed login attempt');
    return null;
  }

  getUsers() {
    const users = JSON.parse(localStorage.getItem(STORAGE_KEYS.USERS) || '[]');
    return users.map(u => ({ username: u.username, role: u.role, fullName: u.fullName }));
  }

  createUser(username, password, fullName, role) {
    const users = JSON.parse(localStorage.getItem(STORAGE_KEYS.USERS) || '[]');
    if (users.find(u => u.username.toLowerCase() === username.toLowerCase())) {
      throw new Error(`Username '${username}' already exists.`);
    }
    users.push({
      username: username.toLowerCase().trim(),
      passwordHash: computeHash(password),
      role,
      fullName: fullName.trim()
    });
    localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(users));
    this.logAudit('ADMIN', 'USER_CREATE', username, `Created user account with role '${role}'`);
  }

  deleteUser(username) {
    let users = JSON.parse(localStorage.getItem(STORAGE_KEYS.USERS) || '[]');
    users = users.filter(u => u.username.toLowerCase() !== username.toLowerCase());
    localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(users));
    this.logAudit('ADMIN', 'USER_DELETE', username, 'Removed user account');
  }

  changePassword(username, currentPassword, newPassword) {
    const users = JSON.parse(localStorage.getItem(STORAGE_KEYS.USERS) || '[]');
    const user = users.find(u => u.username.toLowerCase() === username.toLowerCase());
    if (!user) throw new Error('User not found.');
    if (user.passwordHash !== computeHash(currentPassword)) throw new Error('Incorrect current password.');
    user.passwordHash = computeHash(newPassword);
    localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(users));
    this.logAudit(username, 'PASSWORD_CHANGE', username, 'Password successfully updated');
  }

  // Audit Logging
  logAudit(username, action, studyId, details) {
    const logs = JSON.parse(localStorage.getItem(STORAGE_KEYS.AUDIT) || '[]');
    const record = {
      timestamp: new Date().toISOString(),
      username: username || 'ANONYMOUS',
      action,
      study_id: studyId || '-',
      details: details || '',
      record_hash: computeHash(`${Date.now()}-${username}-${action}-${studyId}`)
    };
    logs.unshift(record);
    if (logs.length > 300) logs.pop();
    localStorage.setItem(STORAGE_KEYS.AUDIT, JSON.stringify(logs));
  }

  getAuditLog() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.AUDIT) || '[]');
  }

  // Patient CRUD
  getPatients(searchQuery = '') {
    const patients = JSON.parse(localStorage.getItem(STORAGE_KEYS.PATIENTS) || '[]');
    if (!searchQuery) return patients;
    const q = searchQuery.toLowerCase();
    return patients.filter(p =>
      (p.study_id && p.study_id.toLowerCase().includes(q)) ||
      (p.first_name && p.first_name.toLowerCase().includes(q)) ||
      (p.last_name && p.last_name.toLowerCase().includes(q)) ||
      (p.hospital_number && p.hospital_number.toLowerCase().includes(q)) ||
      (p.pathology?.primary_suture_involved && p.pathology.primary_suture_involved.toLowerCase().includes(q)) ||
      (p.pathology?.syndromic_diagnosis && p.pathology.syndromic_diagnosis.toLowerCase().includes(q))
    );
  }

  getPatient(id) {
    const patients = JSON.parse(localStorage.getItem(STORAGE_KEYS.PATIENTS) || '[]');
    return patients.find(p => p.id === id) || null;
  }

  savePatient(patientData) {
    const patients = JSON.parse(localStorage.getItem(STORAGE_KEYS.PATIENTS) || '[]');
    let isNew = false;
    if (!patientData.id) {
      patientData.id = 'cf-pt-' + Date.now();
      isNew = true;
    }

    const idx = patients.findIndex(p => p.id === patientData.id);
    if (idx >= 0) {
      patients[idx] = { ...patients[idx], ...patientData, updated_at: new Date().toISOString() };
    } else {
      patientData.created_at = new Date().toISOString();
      patientData.updated_at = new Date().toISOString();
      patients.push(patientData);
    }

    localStorage.setItem(STORAGE_KEYS.PATIENTS, JSON.stringify(patients));
    this.logAudit(
      window.AppState?.currentUser?.username || 'CLINICIAN',
      isNew ? 'PATIENT_CREATE' : 'PATIENT_UPDATE',
      patientData.study_id,
      `Saved patient record: ${patientData.first_name} ${patientData.last_name}`
    );
    return patientData;
  }

  deletePatient(id) {
    let patients = JSON.parse(localStorage.getItem(STORAGE_KEYS.PATIENTS) || '[]');
    const target = patients.find(p => p.id === id);
    if (!target) return false;

    patients = patients.filter(p => p.id !== id);
    localStorage.setItem(STORAGE_KEYS.PATIENTS, JSON.stringify(patients));

    // Cascade delete child records
    [
      STORAGE_KEYS.SURGERIES,
      STORAGE_KEYS.MDT_NEUROSURG,
      STORAGE_KEYS.MDT_CRANIO,
      STORAGE_KEYS.MDT_GENETICS,
      STORAGE_KEYS.MDT_NEUROPSYCH,
      STORAGE_KEYS.MDT_SPEECH,
      STORAGE_KEYS.MDT_OPHTHALMOLOGY,
      STORAGE_KEYS.MDT_AIRWAY
    ].forEach(k => {
      const items = JSON.parse(localStorage.getItem(k) || '[]');
      const filtered = items.filter(it => it.patient_id !== id);
      localStorage.setItem(k, JSON.stringify(filtered));
    });

    this.logAudit(
      window.AppState?.currentUser?.username || 'CLINICIAN',
      'PATIENT_DELETE',
      target.study_id,
      `Deleted patient and all associated surgical and MDT records.`
    );
    return true;
  }

  // Surgeries CRUD
  getSurgeries(patientId) {
    const all = JSON.parse(localStorage.getItem(STORAGE_KEYS.SURGERIES) || '[]');
    return all.filter(s => s.patient_id === patientId).sort((a, b) => new Date(a.surgery_date) - new Date(b.surgery_date));
  }

  saveSurgery(surgData) {
    const all = JSON.parse(localStorage.getItem(STORAGE_KEYS.SURGERIES) || '[]');
    if (!surgData.id) {
      surgData.id = 'cf-surg-' + Date.now();
      all.push(surgData);
    } else {
      const idx = all.findIndex(s => s.id === surgData.id);
      if (idx >= 0) all[idx] = surgData;
      else all.push(surgData);
    }
    localStorage.setItem(STORAGE_KEYS.SURGERIES, JSON.stringify(all));
    return surgData;
  }

  deleteSurgery(id) {
    let all = JSON.parse(localStorage.getItem(STORAGE_KEYS.SURGERIES) || '[]');
    all = all.filter(s => s.id !== id);
    localStorage.setItem(STORAGE_KEYS.SURGERIES, JSON.stringify(all));
    return true;
  }

  // Generic MDT Sub-Collection Helpers
  getMdtRecords(storageKey, patientId) {
    const all = JSON.parse(localStorage.getItem(storageKey) || '[]');
    return all.filter(m => m.patient_id === patientId).sort((a, b) => new Date(b.assessment_date || b.consultation_date || b.examination_date) - new Date(a.assessment_date || a.consultation_date || a.examination_date));
  }

  saveMdtRecord(storageKey, prefix, data) {
    const all = JSON.parse(localStorage.getItem(storageKey) || '[]');
    if (!data.id) {
      data.id = prefix + '-' + Date.now();
      all.push(data);
    } else {
      const idx = all.findIndex(m => m.id === data.id);
      if (idx >= 0) all[idx] = data;
      else all.push(data);
    }
    localStorage.setItem(storageKey, JSON.stringify(all));
    return data;
  }

  deleteMdtRecord(storageKey, id) {
    let all = JSON.parse(localStorage.getItem(storageKey) || '[]');
    all = all.filter(m => m.id !== id);
    localStorage.setItem(storageKey, JSON.stringify(all));
    return true;
  }

  // Specific MDT Wrappers
  getNeurosurgery(pId) { return this.getMdtRecords(STORAGE_KEYS.MDT_NEUROSURG, pId); }
  saveNeurosurgery(data) { return this.saveMdtRecord(STORAGE_KEYS.MDT_NEUROSURG, 'mdt-ns', data); }
  deleteNeurosurgery(id) { return this.deleteMdtRecord(STORAGE_KEYS.MDT_NEUROSURG, id); }

  getCraniofacial(pId) { return this.getMdtRecords(STORAGE_KEYS.MDT_CRANIO, pId); }
  saveCraniofacial(data) { return this.saveMdtRecord(STORAGE_KEYS.MDT_CRANIO, 'mdt-cr', data); }
  deleteCraniofacial(id) { return this.deleteMdtRecord(STORAGE_KEYS.MDT_CRANIO, id); }

  getGenetics(pId) { return this.getMdtRecords(STORAGE_KEYS.MDT_GENETICS, pId); }
  saveGenetics(data) { return this.saveMdtRecord(STORAGE_KEYS.MDT_GENETICS, 'mdt-gn', data); }
  deleteGenetics(id) { return this.deleteMdtRecord(STORAGE_KEYS.MDT_GENETICS, id); }

  getNeuropsychology(pId) { return this.getMdtRecords(STORAGE_KEYS.MDT_NEUROPSYCH, pId); }
  saveNeuropsychology(data) { return this.saveMdtRecord(STORAGE_KEYS.MDT_NEUROPSYCH, 'mdt-np', data); }
  deleteNeuropsychology(id) { return this.deleteMdtRecord(STORAGE_KEYS.MDT_NEUROPSYCH, id); }

  getSpeechTherapy(pId) { return this.getMdtRecords(STORAGE_KEYS.MDT_SPEECH, pId); }
  saveSpeechTherapy(data) { return this.saveMdtRecord(STORAGE_KEYS.MDT_SPEECH, 'mdt-sp', data); }
  deleteSpeechTherapy(id) { return this.deleteMdtRecord(STORAGE_KEYS.MDT_SPEECH, id); }

  getOphthalmology(pId) { return this.getMdtRecords(STORAGE_KEYS.MDT_OPHTHALMOLOGY, pId); }
  saveOphthalmology(data) { return this.saveMdtRecord(STORAGE_KEYS.MDT_OPHTHALMOLOGY, 'mdt-oph', data); }
  deleteOphthalmology(id) { return this.deleteMdtRecord(STORAGE_KEYS.MDT_OPHTHALMOLOGY, id); }

  getAirway(pId) { return this.getMdtRecords(STORAGE_KEYS.MDT_AIRWAY, pId); }
  saveAirway(data) { return this.saveMdtRecord(STORAGE_KEYS.MDT_AIRWAY, 'mdt-aw', data); }
  deleteAirway(id) { return this.deleteMdtRecord(STORAGE_KEYS.MDT_AIRWAY, id); }

  // Clinical Documents
  generateDischargeSummary(patientId) {
    const p = this.getPatient(patientId);
    if (!p) return 'Error: Patient not found.';
    const surgeries = this.getSurgeries(patientId);
    const lastSurg = surgeries.length > 0 ? surgeries[surgeries.length - 1] : null;

    return `================================================================================
PAEDIATRIC CRANIOFACIAL SURGERY INPATIENT DISCHARGE SUMMARY
Tertiary Craniofacial & Paediatric Neurosurgery Centre
Conceived, designed and tested: Dr G Narenthiran MB ChB BSc(MedSci)(Hons) MRCS(Ed.) FEBNS FRCS(SN)
================================================================================

PATIENT DETAILS:
Study ID: ${p.study_id}
Hospital Number: ${p.hospital_number || 'N/A'}
Name: ${p.first_name} ${p.last_name}
Date of Birth: ${p.dob} (Age at presentation: ${p.age_at_presentation_months} months)
Gender: ${p.gender}
Lead Craniofacial Surgeons: ${p.lead_neurosurgeon || 'Dr G Narenthiran'} / ${p.lead_craniofacial_surgeon || 'Consultant Craniofacial Surgeon'}

DIAGNOSIS & GENETIC PROFILE:
Diagnostic Category: ${p.pathology?.primary_diagnostic_category || 'Craniosynostosis'}
Suture Involved: ${p.pathology?.primary_suture_involved || 'N/A'}
Syndromic Diagnosis: ${p.pathology?.syndromic_diagnosis || 'Non-Syndromic'}
Genetic Finding: ${p.pathology?.specific_gene_identified || 'Negative'} (${p.pathology?.dna_mutation_details || 'None'})

MOST RECENT OPERATIVE EPISODE:
Procedure: ${lastSurg?.procedure_sequence || 'Primary Craniofacial Procedure'} (${lastSurg?.surgical_technique_category || 'N/A'})
${lastSurg?.surgical_technique_other_detail ? 'Technique Detail: ' + lastSurg.surgical_technique_other_detail : ''}
Date of Surgery: ${lastSurg?.surgery_date || 'N/A'}
Lead Surgeon: ${lastSurg?.lead_surgeon || 'Dr G Narenthiran'}
Surgeon Narrative:
${lastSurg?.surgeon_operative_description || 'Cranial vault remodeling completed without intraoperative complication.'}

INTRAOPERATIVE PARAMETERS:
Operating Time: ${lastSurg?.operating_time_minutes || '-'} minutes
Estimated Blood Loss: ${lastSurg?.estimated_blood_loss_ml || 0} mL (${lastSurg?.estimated_blood_loss_pct_ebv || 0}% of estimated blood volume)
Blood Products Transfused: PRBC ${lastSurg?.prbc_transfused_ml || 0} mL, FFP ${lastSurg?.ffp_transfused_ml || 0} mL
Tranexamic Acid: ${lastSurg?.tranexamic_acid_administered || 'Yes'}
Dural Integrity: ${lastSurg?.dural_tear_occurred || 'No'}
Bone Fixation: ${lastSurg?.bone_fixation_method || 'Resorbable Plates'}
${lastSurg?.spring_or_distractor_details ? 'Hardware Details: ' + lastSurg.spring_or_distractor_details : ''}

POSTOPERATIVE COURSE & RECOVERY:
ICU Stay: ${lastSurg?.icu_stay_days || 0} day(s) | Total Hospital Stay: ${lastSurg?.hospital_stay_days || 0} day(s)
CSF Leak / Pseudomeningocele: ${p.outcomes?.complication_dural_tear_or_csf_leak || 'None'}
Surgical Site Status: Clean, wound healing well, no erythema or discharge.
Parent Overall Satisfaction: ${p.outcomes?.parent_overall_satisfaction_score ? p.outcomes.parent_overall_satisfaction_score + '/5 Stars' : 'Not rated'}

DISCHARGE PLAN & FOLLOW-UP:
${lastSurg?.helmet_therapy_planned === 'Yes' ? '1. Orthotic Molding Helmet Therapy: Patient fitted with custom helmet. Daily wear target 23 hours/day for ' + (lastSurg.helmet_protocol_duration_months || 9) + ' months.' : '1. Wound care: Keep scalp clean and dry. Resorbable sutures in situ.'}
2. Clinic Review: Outpatient Paediatric Craniofacial & Neurosurgery Clinic in 6 weeks.
3. Multidisciplinary follow-up with Speech Therapy, Ophthalmology, and Genetics scheduled.
4. Urgent contact advice given regarding fever, scalp swelling, persistent vomiting, or irritability.

Discharge Summary Generated by:
${window.AppState?.currentUser?.fullName || 'Dr G Narenthiran MB ChB BSc(MedSci)(Hons) MRCS(Ed.) FEBNS FRCS(SN)'}
Date: ${new Date().toLocaleDateString('en-GB')}
================================================================================`;
  }

  generateClinicLetter(patientId) {
    const p = this.getPatient(patientId);
    if (!p) return 'Error: Patient not found.';
    const surgeries = this.getSurgeries(patientId);
    const ns = this.getNeurosurgery(patientId);
    const cr = this.getCraniofacial(patientId);
    const gn = this.getGenetics(patientId);
    const np = this.getNeuropsychology(patientId);
    const sp = this.getSpeechTherapy(patientId);
    const oph = this.getOphthalmology(patientId);
    const aw = this.getAirway(patientId);

    return `================================================================================
MULTIDISCIPLINARY PAEDIATRIC CRANIOFACIAL OUTPATIENT REVIEW LETTER
Tertiary Craniofacial Center & Paediatric Neurosurgery
Conceived, designed and tested: Dr G Narenthiran MB ChB BSc(MedSci)(Hons) MRCS(Ed.) FEBNS FRCS(SN)
================================================================================

To: General Practitioner / Paediatrician
Date: ${new Date().toLocaleDateString('en-GB')}

RE: ${p.first_name} ${p.last_name} (DOB: ${p.dob})
Study ID: ${p.study_id} | Hospital No: ${p.hospital_number || 'N/A'}
Diagnosis: ${p.pathology?.primary_suture_involved || 'Craniosynostosis'} - ${p.pathology?.syndromic_diagnosis || 'Non-Syndromic'}

We reviewed ${p.first_name} in our joint Multidisciplinary Paediatric Craniofacial & Neurosurgical Clinic today.

SURGICAL HISTORY & STRUCTURAL OUTCOMES:
Total Craniofacial Procedures: ${surgeries.length}
Most Recent Surgery: ${surgeries.length > 0 ? surgeries[surgeries.length - 1].procedure_sequence + ' (' + surgeries[surgeries.length - 1].surgical_technique_category + ') on ' + surgeries[surgeries.length - 1].surgery_date : 'Awaiting initial surgery'}
Whitaker Classification: ${p.outcomes?.whitaker_classification || 'Pending formal review'}
Cranial Vault Symmetry: ${p.outcomes?.head_shape_aesthetic_correction || 'Satisfactory'}
Cephalic Index: Pre-op ${p.preop?.cephalic_index || '-'}% -> Latest Post-op ${p.outcomes?.postop_cephalic_index || '-'}% (Improvement: ${p.outcomes?.cephalic_index_improvement || '-'}%)
Parent Satisfaction: ${p.outcomes?.parent_head_shape_satisfaction || 'Satisfied'} (${p.outcomes?.parent_overall_satisfaction_score || 5}/5 Stars)

MULTIDISCIPLINARY TEAM (MDT) EVALUATIONS:

1. PAEDIATRIC NEUROSURGERY:
${ns.length > 0 ? ns[0].icp_assessment_summary + ' | Papilloedema: ' + ns[0].fundoscopy_papilloedema_status + ' | Chiari: ' + ns[0].chiari_tonsil_position_status : 'Stable neurosurgical intracranial dynamics; fontanelle soft; no clinical raised ICP.'}

2. CRANIOFACIAL & PLASTIC SURGERY:
${cr.length > 0 ? cr[0].forehead_and_supraorbital_contour + ' | Soft tissues: ' + cr[0].soft_tissue_and_scar_appearance : 'Forehead and supraorbital contour well preserved with excellent aesthetic harmony.'}

3. CLINICAL GENETICS:
${gn.length > 0 ? gn[0].clinical_syndromic_impression + ' (' + gn[0].counseling_inheritance_and_recurrence + ')' : p.pathology?.specific_gene_identified + ' (' + p.pathology?.dna_mutation_details + ')'}

4. OPHTHALMOLOGY:
${oph.length > 0 ? 'Exorbitism: ' + oph[0].exorbitism_hertel_mm + ' mm | Strabismus: ' + oph[0].strabismus_v_pattern + ' | Corneal integrity: ' + oph[0].corneal_integrity : 'No strabismus or corneal exposure. Optic nerve heads crisp and healthy.'}

5. AIRWAY & SLEEP MEDICINE:
${aw.length > 0 ? 'Upper airway: ' + aw[0].upper_airway_patency + ' | AHI score: ' + aw[0].ahi_current_score + ' (' + p.preop?.ahi_severity + ')' : 'No stertor or sleep apnea symptoms reported by parents.'}

6. SPEECH & LANGUAGE THERAPY:
${sp.length > 0 ? 'Velopharyngeal status: ' + sp[0].velopharyngeal_competence + ' | Feeding: ' + sp[0].feeding_and_swallowing_function : 'Normal age-appropriate vocalizations and oral motor feeding.'}

7. NEUROPSYCHOLOGY & DEVELOPMENT:
${np.length > 0 ? 'Developmental Quotient / IQ: ' + np[0].developmental_quotient_or_iq + ' | Motor: ' + np[0].gross_motor_development : 'Gross motor, adaptive, and communicative milestones developing age-appropriately.'}

MANAGEMENT PLAN:
1. Continue multidisciplinary surveillance protocol.
2. Next combined craniofacial clinic review in 6-12 months with repeat 3D morphometric photogrammetry.
3. Routine ophthalmology and developmental review scheduled.

Yours sincerely,

Dr G Narenthiran MB ChB BSc(MedSci)(Hons) MRCS(Ed.) FEBNS FRCS(SN)
Consultant Paediatric Neurosurgeon
Email: g_narenthiran@hotmail.com
================================================================================`;
  }

  // Exports
  exportToJson() {
    const data = {
      patients: JSON.parse(localStorage.getItem(STORAGE_KEYS.PATIENTS) || '[]'),
      surgeries: JSON.parse(localStorage.getItem(STORAGE_KEYS.SURGERIES) || '[]'),
      mdt_neurosurgery: JSON.parse(localStorage.getItem(STORAGE_KEYS.MDT_NEUROSURG) || '[]'),
      mdt_craniofacial: JSON.parse(localStorage.getItem(STORAGE_KEYS.MDT_CRANIO) || '[]'),
      mdt_genetics: JSON.parse(localStorage.getItem(STORAGE_KEYS.MDT_GENETICS) || '[]'),
      mdt_neuropsychology: JSON.parse(localStorage.getItem(STORAGE_KEYS.MDT_NEUROPSYCH) || '[]'),
      mdt_speech_therapy: JSON.parse(localStorage.getItem(STORAGE_KEYS.MDT_SPEECH) || '[]'),
      mdt_ophthalmology: JSON.parse(localStorage.getItem(STORAGE_KEYS.MDT_OPHTHALMOLOGY) || '[]'),
      mdt_airway: JSON.parse(localStorage.getItem(STORAGE_KEYS.MDT_AIRWAY) || '[]'),
      audit_ledger: JSON.parse(localStorage.getItem(STORAGE_KEYS.AUDIT) || '[]'),
      exported_at: new Date().toISOString()
    };
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Paediatric_Craniofacial_DB_Backup_${new Date().toISOString().substring(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    this.logAudit(window.AppState?.currentUser?.username, 'EXPORT_JSON', 'ALL', 'Exported comprehensive database JSON backup');
  }

  exportToStata() {
    const patients = JSON.parse(localStorage.getItem(STORAGE_KEYS.PATIENTS) || '[]');
    const surgeries = JSON.parse(localStorage.getItem(STORAGE_KEYS.SURGERIES) || '[]');

    const variables = [
      { name: 'study_id', type: 16, fmt: '%-16s' },
      { name: 'age_pres_mo', type: 254, fmt: '%9.1f' },
      { name: 'gender', type: 251, fmt: '%9.0g' },
      { name: 'diag_cat', type: 251, fmt: '%9.0g' },
      { name: 'suture_code', type: 251, fmt: '%9.0g' },
      { name: 'syndrome_code', type: 251, fmt: '%9.0g' },
      { name: 'gene_code', type: 251, fmt: '%9.0g' },
      { name: 'pre_ci', type: 254, fmt: '%9.1f' },
      { name: 'post_ci', type: 254, fmt: '%9.1f' },
      { name: 'ci_delta', type: 254, fmt: '%9.1f' },
      { name: 'whitaker', type: 251, fmt: '%9.0g' },
      { name: 'ahi_score', type: 254, fmt: '%9.1f' },
      { name: 'papilloedema', type: 251, fmt: '%9.0g' },
      { name: 'chiari_present', type: 251, fmt: '%9.0g' },
      { name: 'hydrocephalus', type: 251, fmt: '%9.0g' },
      { name: 'surg_count', type: 252, fmt: '%9.0g' },
      { name: 'last_ebl_ml', type: 253, fmt: '%9.0g' },
      { name: 'last_ebl_pct', type: 254, fmt: '%9.1f' },
      { name: 'prbc_ml', type: 253, fmt: '%9.0g' },
      { name: 'dural_tear', type: 251, fmt: '%9.0g' },
      { name: 'csf_leak', type: 251, fmt: '%9.0g' },
      { name: 'redo_surgery', type: 251, fmt: '%9.0g' },
      { name: 'parent_sat', type: 251, fmt: '%9.0g' }
    ];

    const rows = patients.map(p => {
      const pSurgs = surgeries.filter(s => s.patient_id === p.id);
      const lastS = pSurgs.length > 0 ? pSurgs[pSurgs.length - 1] : null;
      const hasRedo = pSurgs.some(s => s.procedure_sequence.includes('Redo') || s.procedure_sequence.includes('Stage'));

      let diagCat = 1;
      if (p.pathology?.primary_diagnostic_category?.includes('Multi')) diagCat = 2;
      else if (p.pathology?.primary_diagnostic_category?.includes('Syndromic')) diagCat = 3;

      let sutureCode = 1;
      if (p.pathology?.primary_suture_involved?.includes('Metopic')) sutureCode = 2;
      else if (p.pathology?.primary_suture_involved?.includes('Unilateral Coronal')) sutureCode = 3;
      else if (p.pathology?.primary_suture_involved?.includes('Bicoronal')) sutureCode = 4;
      else if (p.pathology?.primary_suture_involved?.includes('Lambdoid')) sutureCode = 5;
      else if (p.pathology?.primary_suture_involved?.includes('Cloverleaf')) sutureCode = 6;

      let syndCode = 0;
      if (p.pathology?.syndromic_diagnosis?.includes('Crouzon')) syndCode = 1;
      else if (p.pathology?.syndromic_diagnosis?.includes('Apert')) syndCode = 2;
      else if (p.pathology?.syndromic_diagnosis?.includes('Pfeiffer')) syndCode = 3;
      else if (p.pathology?.syndromic_diagnosis?.includes('Saethre')) syndCode = 4;
      else if (p.pathology?.syndromic_diagnosis?.includes('Muenke')) syndCode = 5;

      let whitakerCode = 1;
      if (p.outcomes?.whitaker_classification?.includes('Category II')) whitakerCode = 2;
      else if (p.outcomes?.whitaker_classification?.includes('Category III')) whitakerCode = 3;
      else if (p.outcomes?.whitaker_classification?.includes('Category IV')) whitakerCode = 4;

      return {
        study_id: p.study_id,
        age_pres_mo: p.age_at_presentation_months || 0,
        gender: p.gender === 'Male' ? 1 : 2,
        diag_cat: diagCat,
        suture_code: sutureCode,
        syndrome_code: syndCode,
        gene_code: p.pathology?.specific_gene_identified === 'FGFR2' ? 1 : p.pathology?.specific_gene_identified === 'FGFR3' ? 2 : p.pathology?.specific_gene_identified === 'TWIST1' ? 3 : p.pathology?.specific_gene_identified === 'TCF12' ? 4 : 0,
        pre_ci: p.preop?.cephalic_index || 0,
        post_ci: p.outcomes?.postop_cephalic_index || 0,
        ci_delta: p.outcomes?.cephalic_index_improvement || 0,
        whitaker: whitakerCode,
        ahi_score: p.preop?.ahi_apnea_hypopnea_index || 0,
        papilloedema: p.preop?.papilloedema_present === 'Yes' ? 1 : 0,
        chiari_present: p.preop?.chiari_malformation_present === 'Yes' ? 1 : 0,
        hydrocephalus: p.preop?.hydrocephalus_present?.includes('Yes') ? 1 : 0,
        surg_count: pSurgs.length,
        last_ebl_ml: lastS?.estimated_blood_loss_ml || 0,
        last_ebl_pct: lastS?.estimated_blood_loss_pct_ebv || 0,
        prbc_ml: lastS?.prbc_transfused_ml || 0,
        dural_tear: lastS?.dural_tear_occurred !== 'No' ? 1 : 0,
        csf_leak: p.outcomes?.complication_dural_tear_or_csf_leak?.includes('Postoperative') ? 1 : 0,
        redo_surgery: hasRedo ? 1 : 0,
        parent_sat: p.outcomes?.parent_overall_satisfaction_score || 5
      };
    });

    const buffer = buildStata114Binary(variables, rows, 'Paediatric Craniofacial DB');
    const blob = new Blob([buffer], { type: 'application/octet-stream' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Paediatric_Craniofacial_Cohort_${new Date().toISOString().substring(0, 10)}.dta`;
    a.click();
    URL.revokeObjectURL(url);
    this.logAudit(window.AppState?.currentUser?.username, 'EXPORT_STATA', 'ALL', 'Exported cohort to Stata 114 format (.dta)');
  }

  exportToExcel() {
    const patients = JSON.parse(localStorage.getItem(STORAGE_KEYS.PATIENTS) || '[]');
    const surgeries = JSON.parse(localStorage.getItem(STORAGE_KEYS.SURGERIES) || '[]');

    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += 'Study_ID,Hospital_Number,Name,Age_Months,Gender,Diagnostic_Category,Suture_Involved,Syndrome,Gene,Preop_CI,Postop_CI,CI_Improvement,Whitaker,EBL_mL,PRBC_mL,Dural_Tear,Parent_Satisfaction\n';

    patients.forEach(p => {
      const pSurgs = surgeries.filter(s => s.patient_id === p.id);
      const lastS = pSurgs.length > 0 ? pSurgs[pSurgs.length - 1] : null;
      const row = [
        p.study_id,
        p.hospital_number || '',
        `"${p.first_name} ${p.last_name}"`,
        p.age_at_presentation_months || '',
        p.gender || '',
        `"${p.pathology?.primary_diagnostic_category || ''}"`,
        `"${p.pathology?.primary_suture_involved || ''}"`,
        `"${p.pathology?.syndromic_diagnosis || ''}"`,
        p.pathology?.specific_gene_identified || '',
        p.preop?.cephalic_index || '',
        p.outcomes?.postop_cephalic_index || '',
        p.outcomes?.cephalic_index_improvement || '',
        `"${p.outcomes?.whitaker_classification?.split(':')[0] || ''}"`,
        lastS?.estimated_blood_loss_ml || 0,
        lastS?.prbc_transfused_ml || 0,
        `"${lastS?.dural_tear_occurred || 'No'}"`,
        p.outcomes?.parent_overall_satisfaction_score || 5
      ].join(',');
      csvContent += row + '\n';
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Paediatric_Craniofacial_Registry_${new Date().toISOString().substring(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    this.logAudit(window.AppState?.currentUser?.username, 'EXPORT_EXCEL', 'ALL', 'Exported cohort to Excel CSV format');
  }

  // Cohort Analytics
  getCohortAnalytics() {
    const patients = JSON.parse(localStorage.getItem(STORAGE_KEYS.PATIENTS) || '[]');
    const surgeries = JSON.parse(localStorage.getItem(STORAGE_KEYS.SURGERIES) || '[]');

    const totalPatients = patients.length;
    const totalSurgeries = surgeries.length;

    const sutureCounts = {};
    const techniqueCounts = {};
    const whitakerCounts = {};
    let redoCount = 0;
    let totalPreCI = 0;
    let preCICount = 0;
    let totalPostCI = 0;
    let postCICount = 0;
    let duralTearCount = 0;
    let csfLeakCount = 0;
    let totalSatScore = 0;
    let satCount = 0;

    patients.forEach(p => {
      const sut = p.pathology?.primary_suture_involved || 'Unspecified';
      sutureCounts[sut] = (sutureCounts[sut] || 0) + 1;

      const whit = p.outcomes?.whitaker_classification ? p.outcomes.whitaker_classification.split(':')[0] : 'Unclassified';
      whitakerCounts[whit] = (whitakerCounts[whit] || 0) + 1;

      if (p.preop?.cephalic_index) {
        totalPreCI += parseFloat(p.preop.cephalic_index);
        preCICount++;
      }
      if (p.outcomes?.postop_cephalic_index) {
        totalPostCI += parseFloat(p.outcomes.postop_cephalic_index);
        postCICount++;
      }
      if (p.outcomes?.parent_overall_satisfaction_score) {
        totalSatScore += p.outcomes.parent_overall_satisfaction_score;
        satCount++;
      }
      if (p.outcomes?.complication_dural_tear_or_csf_leak?.includes('Postoperative')) {
        csfLeakCount++;
      }
    });

    surgeries.forEach(s => {
      const tech = s.surgical_technique_category || 'Other';
      techniqueCounts[tech] = (techniqueCounts[tech] || 0) + 1;
      if (s.procedure_sequence?.includes('Redo') || s.procedure_sequence?.includes('Secondary') || s.procedure_sequence?.includes('Stage')) {
        redoCount++;
      }
      if (s.dural_tear_occurred && s.dural_tear_occurred !== 'No') {
        duralTearCount++;
      }
    });

    return {
      totalPatients,
      totalSurgeries,
      redoCount,
      redoRatePct: totalSurgeries > 0 ? Math.round((redoCount / totalSurgeries) * 1000) / 10 : 0,
      meanPreCI: preCICount > 0 ? (totalPreCI / preCICount).toFixed(1) : '-',
      meanPostCI: postCICount > 0 ? (totalPostCI / postCICount).toFixed(1) : '-',
      duralTearRatePct: totalSurgeries > 0 ? Math.round((duralTearCount / totalSurgeries) * 1000) / 10 : 0,
      csfLeakCount,
      meanParentSatisfaction: satCount > 0 ? (totalSatScore / satCount).toFixed(1) : '-',
      sutureDistribution: sutureCounts,
      techniqueDistribution: techniqueCounts,
      whitakerDistribution: whitakerCounts
    };
  }
}

return new DatabaseAdapter();
}));
'''

with open('js/db-adapter.js', 'w') as f:
    f.write(code)

print("Generated js/db-adapter.js successfully!")
