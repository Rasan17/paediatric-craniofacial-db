#!/usr/bin/env python3
"""
MULTIDISCIPLINARY PAEDIATRIC CRANIOFACIAL DATABASE - Stata (.dta) Exporter
Conceived, designed and tested: Dr G Narenthiran MB ChB BSc(MedSci)(Hons) MRCS(Ed.) FEBNS FRCS(SN)
Copyright 2026, Dr G Narenthiran, g_narenthiran@hotmail.com, all rights reserved.
Dedicated to Mrs Nirmaladevy Ganesalingam BSc

This script reads an exported JSON registry backup or SQLite database and exports
native Stata (.dta format 114 / 118) datasets for craniofacial biostatistical modeling,
longitudinal morphometric analysis, and surgical outcome evaluation.
"""

import sys
import os
import re
import json
import argparse
from datetime import datetime

try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def safe_float(val):
    if val is None or val == "":
        return None
    try:
        m = re.search(r"[-+]?(?:\d*\.\d+|\d+)", str(val))
        return float(m.group(0)) if m else None
    except Exception:
        return None


def safe_int(val):
    if val is None or val == "":
        return None
    try:
        m = re.search(r"[-+]?\d+", str(val))
        return int(m.group(0)) if m else None
    except Exception:
        return None


def map_diagnostic_category(cat_str):
    if not cat_str: return 0
    if "Single-Suture" in cat_str: return 1
    if "Multi-Suture" in cat_str: return 2
    if "Syndromic" in cat_str: return 3
    if "Cleft" in cat_str: return 4
    if "Encephalocoele" in cat_str: return 5
    if "Hypertelorism" in cat_str: return 6
    if "Deformational" in cat_str: return 7
    return 8


def map_suture(sut_str):
    if not sut_str: return 0
    if "Sagittal" in sut_str: return 1
    if "Metopic" in sut_str: return 2
    if "Unilateral Coronal - Right" in sut_str: return 3
    if "Unilateral Coronal - Left" in sut_str: return 4
    if "Bicoronal" in sut_str: return 5
    if "Unilateral Lambdoid" in sut_str: return 6
    if "Bilateral Lambdoid" in sut_str: return 7
    if "Cloverleaf" in sut_str or "Pan-Synostosis" in sut_str: return 8
    return 9


def map_syndrome(syn_str):
    if not syn_str: return 0
    if "Non-Syndromic" in syn_str: return 0
    if "Crouzon" in syn_str: return 1
    if "Apert" in syn_str: return 2
    if "Pfeiffer" in syn_str: return 3
    if "Saethre" in syn_str: return 4
    if "Muenke" in syn_str: return 5
    if "CFND" in syn_str or "Craniofrontonasal" in syn_str: return 6
    if "Carpenter" in syn_str: return 7
    return 8


def map_gene(gene_str):
    if not gene_str or "Negative" in gene_str: return 0
    if "FGFR2" in gene_str: return 1
    if "FGFR3" in gene_str: return 2
    if "FGFR1" in gene_str: return 3
    if "TWIST1" in gene_str: return 4
    if "EFNB1" in gene_str: return 5
    if "TCF12" in gene_str: return 6
    if "ERF" in gene_str: return 7
    if "SMAD6" in gene_str: return 8
    return 9


def map_whitaker(w_str):
    if not w_str: return 0
    if "Category I" in w_str: return 1
    if "Category II" in w_str: return 2
    if "Category III" in w_str: return 3
    if "Category IV" in w_str: return 4
    return 0


def convert_patient_records(patients_data, surgeries_data):
    rows = []
    for p in patients_data:
        p_id = p.get("id")
        path = p.get("pathology", {}) or {}
        pre = p.get("preop", {}) or {}
        out = p.get("outcomes", {}) or {}

        p_surgs = [s for s in surgeries_data if s.get("patient_id") == p_id]
        last_s = p_surgs[-1] if p_surgs else {}
        has_redo = any("Redo" in s.get("procedure_sequence", "") or "Secondary" in s.get("procedure_sequence", "") for s in p_surgs)

        row = {
            "study_id": str(p.get("study_id", "")),
            "age_pres_mo": safe_float(p.get("age_at_presentation_months")),
            "gender": 1 if p.get("gender") == "Male" else 2 if p.get("gender") == "Female" else 3,
            "diag_cat": map_diagnostic_category(path.get("primary_diagnostic_category")),
            "suture": map_suture(path.get("primary_suture_involved")),
            "syndrome": map_syndrome(path.get("syndromic_diagnosis")),
            "gene": map_gene(path.get("specific_gene_identified")),
            "pre_ci": safe_float(pre.get("cephalic_index")),
            "post_ci": safe_float(out.get("postop_cephalic_index")),
            "ci_change": safe_float(out.get("cephalic_index_improvement")),
            "whitaker": map_whitaker(out.get("whitaker_classification")),
            "parent_sat": safe_int(out.get("parent_overall_satisfaction_score")),
            "raised_icp": 1 if pre.get("copper_beaten_skull_on_imaging") in ["Moderate", "Severe Pan-Calvarial"] or pre.get("papilloedema_present") == "Yes" else 0,
            "ahi": safe_float(pre.get("ahi_apnea_hypopnea_index")),
            "chiari": 1 if pre.get("chiari_malformation_present") == "Yes" else 0,
            "surg_count": len(p_surgs),
            "ebl_ml": safe_int(last_s.get("estimated_blood_loss_ml")),
            "ebl_pct_ebv": safe_float(last_s.get("estimated_blood_loss_pct_ebv")),
            "prbc_ml": safe_int(last_s.get("prbc_transfused_ml")),
            "dural_tear": 1 if last_s.get("dural_tear_occurred") and last_s.get("dural_tear_occurred") != "No" else 0,
            "csf_leak": 1 if out.get("complication_dural_tear_or_csf_leak") in ["Postoperative CSF Leak", "Pseudomeningocele / Subgaleal Collection"] else 0,
            "redo_surgery": 1 if has_redo else 0
        }
        rows.append(row)
    return rows


def export_to_stata(json_path, output_dta_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    patients = data.get("patients", [])
    surgeries = data.get("surgeries", [])

    rows = convert_patient_records(patients, surgeries)

    if not HAS_PANDAS:
        print("Error: pandas is required for Stata export.")
        sys.exit(1)

    df = pd.DataFrame(rows)

    variable_labels = {
        "study_id": "Patient Study Identifier",
        "age_pres_mo": "Age at initial presentation (months)",
        "gender": "Patient Gender (1=Male, 2=Female, 3=Other)",
        "diag_cat": "Primary Diagnostic Category (1=Single, 2=Multi, 3=Syndromic, 4=Cleft)",
        "suture": "Suture Involved (1=Sag, 2=Met, 3=R-Cor, 4=L-Cor, 5=Bicor, 6=Lamb, 8=Clover)",
        "syndrome": "Syndrome (0=NonSyn, 1=Crouzon, 2=Apert, 3=Pfeiffer, 4=Saethre, 5=Muenke)",
        "gene": "Identified Gene (0=Neg, 1=FGFR2, 2=FGFR3, 3=FGFR1, 4=TWIST1, 6=TCF12)",
        "pre_ci": "Preoperative Cephalic Index (%)",
        "post_ci": "Postoperative Cephalic Index (%)",
        "ci_change": "Cephalic Index Normalization Change (%)",
        "whitaker": "Whitaker Classification of Outcome (Category 1 to 4)",
        "parent_sat": "Parent Overall Satisfaction Score (1 to 5 Stars)",
        "raised_icp": "Evidence of Intracranial Hypertension (0=No, 1=Yes)",
        "ahi": "Sleep Study Apnea-Hypopnea Index (events/hr)",
        "chiari": "Chiari I Tonsillar Herniation Present (0=No, 1=Yes)",
        "surg_count": "Total Craniofacial Surgical Procedures",
        "ebl_ml": "Estimated Blood Loss Most Recent Surgery (mL)",
        "ebl_pct_ebv": "EBL as % of Estimated Blood Volume (%)",
        "prbc_ml": "Packed Red Blood Cells Transfused (mL)",
        "dural_tear": "Intraoperative Dural Tear Encountered (0=No, 1=Yes)",
        "csf_leak": "Postoperative CSF Leak / Pseudomeningocele (0=No, 1=Yes)",
        "redo_surgery": "Underwent Redo / Secondary Craniofacial Surgery (0=No, 1=Yes)"
    }

    val_labels = {
        "gender": {1: "Male", 2: "Female", 3: "Other"},
        "diag_cat": {1: "Single Suture", 2: "Multi Suture", 3: "Syndromic", 4: "Cleft", 5: "Encephalocoele", 7: "Deformational"},
        "suture": {1: "Sagittal", 2: "Metopic", 3: "R Unicoronal", 4: "L Unicoronal", 5: "Bicoronal", 6: "Lambdoid", 8: "Pan-Synostosis"},
        "syndrome": {0: "Non-Syndromic", 1: "Crouzon", 2: "Apert", 3: "Pfeiffer", 4: "Saethre-Chotzen", 5: "Muenke", 6: "CFND"},
        "whitaker": {1: "Category I (Optimal)", 2: "Category II (Minor)", 3: "Category III (Bone Graft)", 4: "Category IV (Redo Reop)"}
    }

    df.to_stata(
        output_dta_path,
        version=117,
        variable_labels=variable_labels,
        value_labels=val_labels,
        write_index=False
    )
    print(f"Successfully exported {len(df)} paediatric craniofacial patient records to Stata (.dta): {output_dta_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export Paediatric Craniofacial database to Stata (.dta)")
    parser.add_argument("input_json", help="Path to input JSON backup")
    parser.add_argument("output_dta", help="Path to output Stata (.dta) file")
    args = parser.parse_args()

    export_to_stata(args.input_json, args.output_dta)
