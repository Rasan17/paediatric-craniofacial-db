import os

code = r'''/**
 * PAEDIATRIC CRANIOFACIAL SCORING & PROGNOSTIC ENGINES
 * Conceived, designed and tested: Dr G Narenthiran MB ChB BSc(MedSci)(Hons) MRCS(Ed.) FEBNS FRCS(SN)
 * Dedicated to Mrs Nirmaladevy Ganesalingam BSc
 * Includes:
 * 1. Cephalic Index (CI) Morphometric Calculator & Classification
 * 2. Whitaker Classification of Craniofacial Outcomes (Category I - IV)
 * 3. Paediatric Apnea-Hypopnea Index (AHI) Obstructive Sleep Apnea Severity
 * 4. Paediatric Estimated Blood Loss (% of EBV) Hemodynamic Risk Engine
 * 5. Frisen Papilloedema & Raised ICP Assessment Engine
 */

export const ScoringEngines = {
  /**
   * Cephalic Index (CI) Calculator
   * CI = (Cranial Width / Cranial Length) * 100
   */
  evalCephalicIndex(widthMm, lengthMm) {
    const w = parseFloat(widthMm);
    const l = parseFloat(lengthMm);
    if (isNaN(w) || isNaN(l) || l <= 0 || w <= 0) return null;

    const ci = (w / l) * 100;
    const roundedCI = Math.round(ci * 10) / 10;
    let category = "Mesocephalic (Normal)";
    let description = "Normal cranial proportion (75.0 - 80.0%)";
    let status = "Normal";

    if (ci < 75.0) {
      category = "Dolichocephalic / Scaphocephalic";
      description = "Narrow, elongated cranial vault characteristic of Sagittal Synostosis (<75.0%)";
      status = "Scaphocephaly";
    } else if (ci > 85.0) {
      category = "Hyperbrachycephalic";
      description = "Severely foreshortened, widened cranial vault (Bicoronal / Syndromic / Cloverleaf >85.0%)";
      status = "Severe Brachycephaly";
    } else if (ci > 80.0) {
      category = "Brachycephalic";
      description = "Foreshortened cranial vault (Bicoronal synostosis or deformational brachycephaly 80.1 - 85.0%)";
      status = "Brachycephaly";
    }

    return {
      ci: roundedCI,
      category,
      description,
      status
    };
  },

  /**
   * Whitaker Classification of Craniofacial Outcomes
   */
  evalWhitaker(categoryString) {
    if (!categoryString) return null;

    if (categoryString.includes("Category I")) {
      return {
        category: "Category I",
        tier: "Optimal",
        badgeClass: "badge-success",
        recommendation: "Excellent structural outcome. No further surgical revision considered advisable or desired."
      };
    } else if (categoryString.includes("Category II")) {
      return {
        category: "Category II",
        tier: "Minor Revision",
        badgeClass: "badge-warning",
        recommendation: "Minor surgical revisions of contour, burring, or soft tissue touch-up considered."
      };
    } else if (categoryString.includes("Category III")) {
      return {
        category: "Category III",
        tier: "Major Bone Graft / Repeat Osteotomy",
        badgeClass: "badge-purple",
        recommendation: "Major bone grafting or repeat osteotomy needed, but less extensive than original procedure."
      };
    } else if (categoryString.includes("Category IV")) {
      return {
        category: "Category IV",
        tier: "Major Reoperation",
        badgeClass: "badge-danger",
        recommendation: "Major craniofacial reoperation duplicating or exceeding initial extent of surgery (Redo Surgery)."
      };
    }
    return null;
  },

  /**
   * Paediatric Apnea-Hypopnea Index (AHI)
   */
  evalAHI(score) {
    const ahi = parseFloat(score);
    if (isNaN(ahi) || ahi < 0) return null;

    if (ahi < 1.0) {
      return {
        ahi,
        severity: "Normal",
        tier: "Normal",
        badgeClass: "badge-success",
        description: "Normal paediatric respiratory polysomnography (<1.0 event/hr)."
      };
    } else if (ahi < 5.0) {
      return {
        ahi,
        severity: "Mild OSA",
        tier: "Mild",
        badgeClass: "badge-warning",
        description: "Mild Obstructive Sleep Apnea (1.0 - 4.9 events/hr). Routine surveillance indicated."
      };
    } else if (ahi < 10.0) {
      return {
        ahi,
        severity: "Moderate OSA",
        tier: "Moderate",
        badgeClass: "badge-purple",
        description: "Moderate Obstructive Sleep Apnea (5.0 - 9.9 events/hr). Consider nocturnal CPAP or ENT intervention."
      };
    } else {
      return {
        ahi,
        severity: "Severe OSA",
        tier: "Severe",
        badgeClass: "badge-danger",
        description: "Severe Obstructive Sleep Apnea (>=10.0 events/hr). Critical airway compromise risk; urgent midface/vault expansion or CPAP/tracheostomy."
      };
    }
  },

  /**
   * Estimated Blood Loss (% of EBV)
   * Infant/Child EBV ~ 80 mL/kg
   */
  evalBloodLoss(eblMl, weightKg) {
    const ebl = parseFloat(eblMl);
    const wt = parseFloat(weightKg);
    if (isNaN(ebl) || isNaN(wt) || wt <= 0) return null;

    const ebv = wt * 80;
    const pct = Math.round((ebl / ebv) * 1000) / 10;

    let tier = "Minimal";
    let badgeClass = "badge-success";
    if (pct > 30.0) {
      tier = "Critical / Massive Blood Loss (>30% EBV)";
      badgeClass = "badge-danger";
    } else if (pct > 15.0) {
      tier = "Moderate Hemorrhage (15 - 30% EBV)";
      badgeClass = "badge-warning";
    } else {
      tier = "Low Hemorrhage (<15% EBV)";
      badgeClass = "badge-success";
    }

    return {
      ebl,
      ebv: Math.round(ebv),
      pct,
      tier,
      badgeClass
    };
  },

  /**
   * Frisen Papilloedema Grade
   */
  evalFrisen(gradeString) {
    if (!gradeString || gradeString === "None") return { grade: "None", status: "No Papilloedema", badgeClass: "badge-success" };
    if (gradeString.includes("Grade 0")) return { grade: "Grade 0", status: "Normal Optic Disc", badgeClass: "badge-success" };
    if (gradeString.includes("Grade 1") || gradeString.includes("Grade 2")) return { grade: gradeString, status: "Early / Mild Papilloedema", badgeClass: "badge-warning" };
    if (gradeString.includes("Grade 3")) return { grade: "Grade 3", status: "Moderate Papilloedema", badgeClass: "badge-purple" };
    return { grade: gradeString, status: "Marked / Severe Papilloedema (Raised ICP Alert)", badgeClass: "badge-danger" };
  }
};

if (typeof window !== "undefined") {
  window.ScoringEngines = ScoringEngines;
}
'''

with open('js/scoring-engines.js', 'w') as f:
    f.write(code)

print("Generated js/scoring-engines.js successfully!")
