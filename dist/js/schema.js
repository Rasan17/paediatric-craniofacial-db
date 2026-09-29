/**
 * MULTIDISCIPLINARY PAEDIATRIC CRANIOFACIAL DATABASE
 * SQLite Database Schema Definitions & Preloaded Clinical Demonstrators
 * Conceived, designed and tested: Dr G Narenthiran MB ChB BSc(MedSci)(Hons) MRCS(Ed.) FEBNS FRCS(SN)
 * Copyright 2026, Dr G Narenthiran, g_narenthiran@hotmail.com, all rights reserved.
 * Dedicated to Mrs Nirmaladevy Ganesalingam BSc
 */

export const SCHEMA_SQL = `
-- 1. Patients Master Craniofacial Registry
CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    study_id TEXT UNIQUE NOT NULL,
    hospital_number TEXT,
    first_name TEXT,
    last_name TEXT,
    dob DATE,
    age_at_presentation_months REAL,
    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other', 'Unknown')),
    ethnicity TEXT,
    birth_weight_kg REAL,
    gestational_age_weeks REAL,
    head_circumference_at_birth_cm REAL,
    lead_neurosurgeon TEXT,
    lead_craniofacial_surgeon TEXT,
    lead_plastic_surgeon TEXT,
    clinical_nurse_specialist TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Craniofacial Pathology & Genetics
CREATE TABLE IF NOT EXISTS craniofacial_pathology_genetics (
    id TEXT PRIMARY KEY,
    patient_id TEXT UNIQUE NOT NULL,
    primary_diagnostic_category TEXT CHECK(primary_diagnostic_category IN (
        'Single-Suture Craniosynostosis (Non-Syndromic)',
        'Multi-Suture Craniosynostosis (Non-Syndromic)',
        'Syndromic Craniosynostosis',
        'Craniofacial Cleft (Tessier)',
        'Craniofacial Encephalocoele',
        'Hypertelorism / Orbital Dystopia',
        'Deformational / Positional Plagiocephaly',
        'Other Craniofacial Anomaly'
    )),
    primary_suture_involved TEXT CHECK(primary_suture_involved IN (
        'Sagittal (Scaphocephaly / Dolichocephaly)',
        'Metopic (Trigonocephaly)',
        'Unilateral Coronal - Right (Anterior Plagiocephaly)',
        'Unilateral Coronal - Left (Anterior Plagiocephaly)',
        'Bicoronal (Brachycephaly / Turricephaly)',
        'Unilateral Lambdoid - Right (Posterior Plagiocephaly)',
        'Unilateral Lambdoid - Left (Posterior Plagiocephaly)',
        'Bilateral Lambdoid',
        'Squamosal',
        'Pan-Synostosis (Cloverleaf / Kleeblattschaedel)',
        'None / Not Applicable',
        'Other Complex Combination'
    )),
    suture_details_text TEXT,
    syndromic_diagnosis TEXT CHECK(syndromic_diagnosis IN (
        'Non-Syndromic (Isolated)',
        'Crouzon Syndrome',
        'Apert Syndrome',
        'Pfeiffer Syndrome (Type 1)',
        'Pfeiffer Syndrome (Type 2 / Cloverleaf)',
        'Pfeiffer Syndrome (Type 3)',
        'Saethre-Chotzen Syndrome',
        'Muenke Syndrome',
        'Craniofrontonasal Dysplasia (CFND)',
        'Carpenter Syndrome',
        'Jackson-Weiss Syndrome',
        'Antley-Bixler Syndrome',
        'Opitz G/BBB Syndrome',
        'Cleidocranial Dysplasia',
        'Under Investigation / Suspected Syndrome',
        'Other Rare Syndrome'
    )),
    genetic_testing_performed TEXT CHECK(genetic_testing_performed IN ('Yes', 'No', 'Planned / In Progress', 'Declined')),
    genetic_testing_modality TEXT,
    specific_gene_identified TEXT CHECK(specific_gene_identified IN (
        'FGFR2',
        'FGFR3',
        'FGFR1',
        'TWIST1',
        'EFNB1',
        'TCF12',
        'ERF',
        'SMAD6',
        'RAB23',
        'ALX1 / ALX3 / ALX4',
        'POR',
        'RUNX2',
        'Negative / No Pathogenic Variant Found',
        'Variant of Uncertain Significance (VUS)',
        'Not Tested / Pending'
    )),
    dna_mutation_details TEXT,
    inheritance_pattern TEXT CHECK(inheritance_pattern IN (
        'De Novo',
        'Autosomal Dominant - Maternal',
        'Autosomal Dominant - Paternal',
        'Autosomal Recessive',
        'X-Linked Dominant',
        'Unknown / Under Evaluation'
    )),
    family_history_craniofacial TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 3. Craniofacial Preoperative Assessment
CREATE TABLE IF NOT EXISTS preop_assessment (
    id TEXT PRIMARY KEY,
    patient_id TEXT UNIQUE NOT NULL,
    assessment_date DATE,
    weight_kg REAL,
    head_circumference_cm REAL,
    head_circumference_centile REAL,
    cranial_length_mm REAL,
    cranial_width_mm REAL,
    cephalic_index REAL, -- (width / length) * 100
    cephalic_index_category TEXT,
    cranial_vault_asymmetry_index_pct REAL,
    intercanthal_distance_mm REAL,
    interpupillary_distance_mm REAL,
    anterior_fontanelle_status TEXT,
    suture_ridging_palpable TEXT,
    bitemporal_narrowing TEXT,
    forehead_bossing_or_retrusion TEXT,
    orbital_dystopia_harlequin TEXT,
    exorbitism_proptosis_present TEXT,
    corneal_exposure_risk TEXT,
    raised_icp_clinical_signs TEXT,
    copper_beaten_skull_on_imaging TEXT,
    papilloedema_present TEXT,
    frisen_papilloedema_grade TEXT,
    sleep_study_performed TEXT,
    ahi_apnea_hypopnea_index REAL,
    ahi_severity TEXT,
    nocturnal_spo2_nadir_pct REAL,
    respiratory_support_needed TEXT,
    chiari_malformation_present TEXT,
    tonsillar_descent_mm REAL,
    hydrocephalus_present TEXT,
    ventriculomegaly_evans_index REAL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 4. Surgical Procedures & Operative Log (Supports Primary, Redo, Revision)
CREATE TABLE IF NOT EXISTS surgeries (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    surgery_date DATE NOT NULL,
    procedure_sequence TEXT CHECK(procedure_sequence IN (
        'Primary Craniofacial Procedure',
        'Redo Surgery / Secondary Vault Expansion',
        'Staged Craniofacial Procedure (Stage 2 / 3)',
        'Spring Insertion Procedure',
        'Spring Removal Procedure',
        'Distractor Insertion Procedure',
        'Distractor Removal Procedure',
        'Secondary Frontoorbital Advancement',
        'Secondary Minor Contouring / Bone Grafting',
        'Hardware Removal Alone',
        'Wound Debridement / Re-exploration',
        'Other Redo / Revision'
    )),
    surgical_technique_category TEXT CHECK(surgical_technique_category IN (
        'Open Cranial Vault Remodeling',
        'Minimally Invasive / Minimal Access',
        'Spring-Assisted Cranioplasty',
        'Endoscopy-Assisted Strip Craniectomy',
        'Helmet Therapy Alone (Orthotic Molding)',
        'Distraction Osteogenesis (PVDO / FOAR Distraction)',
        'Monobloc / Le Fort III Advancement',
        'Other'
    )),
    surgical_technique_other_detail TEXT,
    surgeon_operative_description TEXT NOT NULL,
    lead_surgeon TEXT,
    assisting_surgeon TEXT,
    anesthetist TEXT,
    operating_time_minutes INTEGER,
    estimated_blood_loss_ml INTEGER,
    estimated_blood_loss_pct_ebv REAL, -- % of estimated blood volume
    prbc_transfused_ml INTEGER,
    ffp_transfused_ml INTEGER,
    platelets_transfused_ml INTEGER,
    cell_saver_returned_ml INTEGER,
    tranexamic_acid_administered TEXT,
    dural_tear_occurred TEXT CHECK(dural_tear_occurred IN ('No', 'Small Primary Repair', 'Large Patch / Graft Repair', 'Sagittal Sinus Tear')),
    bone_fixation_method TEXT CHECK(bone_fixation_method IN (
        'Resorbable Plates and Screws (LactoSorb / SonicWeld)',
        'Titanium Miniplates / Screws',
        'Wire Sutures',
        'Suture Suspensions Alone',
        'Springs in Situ',
        'Distractor Hardware in Situ',
        'No Fixation (Strip Craniectomy Alone)',
        'Other'
    )),
    spring_or_distractor_details TEXT,
    helmet_therapy_planned TEXT CHECK(helmet_therapy_planned IN ('Yes', 'No', 'Not Applicable')),
    helmet_protocol_duration_months REAL,
    icu_stay_days INTEGER,
    hospital_stay_days INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 5. Craniofacial Outcomes, Complications & Parent Satisfaction
CREATE TABLE IF NOT EXISTS craniofacial_outcomes (
    id TEXT PRIMARY KEY,
    patient_id TEXT UNIQUE NOT NULL,
    latest_review_date DATE,
    whitaker_classification TEXT CHECK(whitaker_classification IN (
        'Category I: No further surgical revision considered advisable or desired',
        'Category II: Minor surgical revisions of contour or soft tissue',
        'Category III: Major bone graft or repeat osteotomy (less than original)',
        'Category IV: Major craniofacial reoperation duplicating original extent'
    )),
    postop_cranial_length_mm REAL,
    postop_cranial_width_mm REAL,
    postop_cephalic_index REAL,
    cephalic_index_improvement REAL,
    head_shape_aesthetic_correction TEXT CHECK(head_shape_aesthetic_correction IN ('Excellent', 'Good', 'Satisfactory', 'Poor / Under-corrected', 'Over-corrected')),
    forehead_symmetry_restored TEXT,
    supraorbital_rim_projection TEXT,
    orbital_dystopia_resolved TEXT,
    exorbitism_resolved TEXT,
    parent_overall_satisfaction_score INTEGER, -- 1 to 5 Stars
    parent_head_shape_satisfaction TEXT CHECK(parent_head_shape_satisfaction IN ('Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied')),
    parent_facial_appearance_satisfaction TEXT CHECK(parent_facial_appearance_satisfaction IN ('Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied')),
    parent_would_recommend_procedure TEXT CHECK(parent_would_recommend_procedure IN ('Strongly Agree', 'Agree', 'Unsure', 'Disagree')),
    complication_dural_tear_or_csf_leak TEXT CHECK(complication_dural_tear_or_csf_leak IN ('None', 'Intraoperative Dural Tear (Repaired)', 'Postoperative CSF Leak', 'Pseudomeningocele / Subgaleal Collection')),
    complication_wound_infection TEXT CHECK(complication_wound_infection IN ('None', 'Superficial Surgical Site Infection', 'Deep Infection / Bone Flap Osteomyelitis')),
    complication_bone_resorption TEXT CHECK(complication_bone_resorption IN ('None', 'Minor Palpable Irregularity', 'Major Resorption / Cranial Defect')),
    complication_hardware_problem TEXT CHECK(complication_hardware_problem IN ('None', 'Palpable Plates', 'Hardware Extrusion / Exposure', 'Hardware Infection')),
    complication_resynostosis_recurrence TEXT CHECK(complication_resynostosis_recurrence IN ('No', 'Yes - Required Redo Surgery', 'Yes - Managed Conservatively')),
    complication_neurological_deficit TEXT,
    complication_unplanned_reoperation_30d TEXT,
    overall_clinical_status TEXT CHECK(overall_clinical_status IN ('Completed Treatment - Excellent Result', 'Under Routine Clinical Follow-up', 'Awaiting Second-Stage / Redo Surgery', 'Under Active Helmet Therapy', 'Under Observation')),
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 6. MDT Input: Paediatric Neurosurgery
CREATE TABLE IF NOT EXISTS mdt_neurosurgery (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    assessment_date DATE NOT NULL,
    encounter_phase TEXT CHECK(encounter_phase IN ('Pre-Operative Assessment', 'Early Post-Op Follow-up (0-3m)', 'Intermediate Follow-up (6-12m)', 'Long-Term Surveillance (>12m)')),
    clinician_name TEXT,
    icp_assessment_summary TEXT,
    fundoscopy_papilloedema_status TEXT,
    chiari_tonsil_position_status TEXT,
    ventricles_and_csf_dynamics TEXT,
    neurosurgical_recommendations TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 7. MDT Input: Craniofacial & Plastic Surgery
CREATE TABLE IF NOT EXISTS mdt_craniofacial_plastic (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    assessment_date DATE NOT NULL,
    encounter_phase TEXT CHECK(encounter_phase IN ('Pre-Operative Assessment', 'Early Post-Op Follow-up (0-3m)', 'Intermediate Follow-up (6-12m)', 'Long-Term Surveillance (>12m)')),
    clinician_name TEXT,
    forehead_and_supraorbital_contour TEXT,
    midface_hypoplasia_assessment TEXT,
    soft_tissue_and_scar_appearance TEXT,
    whitaker_stage_estimate TEXT,
    surgical_plan_or_revisions TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 8. MDT Input: Clinical Genetics
CREATE TABLE IF NOT EXISTS mdt_genetics (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    consultation_date DATE NOT NULL,
    geneticist_name TEXT,
    clinical_syndromic_impression TEXT,
    dysmorphology_features TEXT,
    recommended_testing_plan TEXT,
    counseling_inheritance_and_recurrence TEXT,
    prenatal_advice_for_future_pregnancies TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 9. MDT Input: Neuropsychology & Development
CREATE TABLE IF NOT EXISTS mdt_neuropsychology (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    assessment_date DATE NOT NULL,
    encounter_phase TEXT CHECK(encounter_phase IN ('Pre-Operative Assessment', '1-Year Post-Op Follow-up', '3-Year Post-Op Follow-up', 'School-Age Follow-up')),
    neuropsychologist_name TEXT,
    test_battery_used TEXT,
    developmental_quotient_or_iq REAL,
    gross_motor_development TEXT,
    fine_motor_adaptive_skills TEXT,
    language_and_communication TEXT,
    parental_stress_and_bonding_index TEXT,
    educational_support_needed TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 10. MDT Input: Speech & Language Therapy (SLT)
CREATE TABLE IF NOT EXISTS mdt_speech_therapy (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    assessment_date DATE NOT NULL,
    encounter_phase TEXT CHECK(encounter_phase IN ('Pre-Operative Assessment', 'Post-Op Follow-up', 'Routine Annual Surveillance')),
    therapist_name TEXT,
    feeding_and_swallowing_function TEXT,
    cleft_palate_or_bifid_uvula TEXT,
    velopharyngeal_competence TEXT CHECK(velopharyngeal_competence IN ('Normal / Competent', 'Borderline Incompetent', 'Velopharyngeal Insufficiency (VPI)', 'Not Tested / Infant')),
    hypernasality_status TEXT,
    speech_articulation_clarity TEXT,
    therapy_plan TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 11. MDT Input: Ophthalmology
CREATE TABLE IF NOT EXISTS mdt_ophthalmology (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    examination_date DATE NOT NULL,
    ophthalmologist_name TEXT,
    visual_acuity_right TEXT,
    visual_acuity_left TEXT,
    refractive_error_astigmatism TEXT,
    strabismus_v_pattern TEXT,
    exorbitism_hertel_mm REAL,
    corneal_integrity TEXT,
    optic_nerve_status_oct TEXT,
    ophthalmic_management_plan TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 12. MDT Input: ENT & Respiratory / Sleep Medicine
CREATE TABLE IF NOT EXISTS mdt_airway_respiratory (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    assessment_date DATE NOT NULL,
    specialist_name TEXT,
    upper_airway_patency TEXT,
    choanal_stenosis_or_atresia TEXT,
    adenotonsillar_hypertrophy TEXT,
    polysomnography_summary TEXT,
    ahi_current_score REAL,
    cpap_bipap_tolerated TEXT,
    tracheostomy_status TEXT,
    respiratory_plan TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);
`;

if (typeof window !== "undefined") {
    window.SCHEMA_SQL = SCHEMA_SQL;
}
