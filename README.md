# Multidisciplinary Paediatric Craniofacial DB
### Dedicated Clinical Registry & Research Database for Simple & Complex Craniosynostosis and Craniofacial Anomalies

**Conceived, designed and tested: Dr G Narenthiran MB ChB BSc(MedSci)(Hons) MRCS(Ed.) FEBNS FRCS(SN). Copyright 2026, Dr G Narenthiran, g_narenthiran@hotmail.com, all rights reserved.**  
by **Dr G Narenthiran MB ChB BSc(MedSci)(Hons) MRCS(Ed.) FEBNS FRCS(SN)**  
*Dedicated with heartfelt love and gratitude to Mrs Nirmaladevy Ganesalingam BSc.*

---

## 🌟 Clinical & Academic Overview

The **Multidisciplinary Paediatric Craniofacial DB** is a dedicated clinical registry, surgical audit platform, and biostatistical database designed for tertiary paediatric craniofacial and neurosurgical units.

It provides disease-specific ontologies and scoring engines tailored for:
1. **Simple Craniosynostosis (Non-Syndromic Single-Suture)**: Sagittal, Metopic, Unicoronal, Bicoronal, Lambdoid.
2. **Complex & Multi-Suture Craniosynostosis**: Pan-synostosis, Cloverleaf skull (Kleeblattschädel).
3. **Syndromic Craniosynostosis**: Crouzon, Apert, Pfeiffer (1–3), Saethre-Chotzen, Muenke, Craniofrontonasal Dysplasia (CFND), Carpenter, Jackson-Weiss, Antley-Bixler.
4. **Craniofacial Anomalies**: Craniofacial clefts (Tessier), encephalocoeles, hypertelorism, and differential diagnosis of deformational plagiocephaly.

---

## 🔬 Key Clinical Features & Innovations

### 1. Underlying Pathology & Molecular Genetics
- Granular classification of sutures involved and syndromic etiology.
- Specific gene identification: *FGFR1*, *FGFR2*, *FGFR3*, *TWIST1*, *EFNB1*, *TCF12*, *ERF*, *SMAD6*, *RAB23*, *ALX1-4*, *POR*, *RUNX2*.
- Detailed DNA mutation recording (cDNA / protein) and inheritance counseling (de novo vs autosomal dominant).

### 2. Preoperative Assessment & Reactive Morphometry
- **Cephalic Index (CI) Engine**: Real-time evaluation of $(\text{Width}/\text{Length})\times 100$ categorizing Dolichocephaly / Scaphocephaly ($<75\%$), Mesocephaly ($75-80\%$), Brachycephaly ($80.1-85\%$), and Hyperbrachycephaly ($>85\%$).
- Cranial Vault Asymmetry Index (CVAI %), intercanthal and interpupillary distances.
- **Intracranial Hypertension**: Clinical signs, copper beaten skull, and Frisén papilloedema grades (0–5).
- **Airway & Sleep Study**: Apnea-Hypopnea Index (AHI, events/hr) categorization and respiratory support (CPAP, BiPAP, Tracheostomy).
- **Neuro-Anatomy**: Chiari I tonsillar herniation measurement and hydrocephalus / Evans index.

### 3. Comprehensive Surgical Module (Primary, Redo & Modern Techniques)
- **Surgeon’s Narrative Description**: Dedicated operative recording.
- **Surgical Technique Categorization**:
  - `Open Cranial Vault Remodeling` (FOAR, Total Vault, Pi, Bandeau advancement)
  - `Minimally Invasive / Minimal Access`
  - `Spring-Assisted Cranioplasty` (Dynamic expansion spring force and removal dates)
  - `Endoscopy-Assisted Strip Craniectomy`
  - `Helmet Therapy Alone` (Custom orthotic molding helmet duration and compliance)
  - `Distraction Osteogenesis` (PVDO, FOAR distraction)
  - `Monobloc / Le Fort III Advancement`
  - `Other` (with mandatory free-text explanation)
- **Redo Surgery Options**: Explicit tracking of secondary vault expansion, secondary frontoorbital advancement, secondary contouring, and hardware removal.
- **Hemodynamics & Transfusion**: Operative time, Estimated Blood Loss (EBL in mL and % of Estimated Blood Volume $\approx 80\,\text{mL/kg}$), PRBC, FFP, cell saver, tranexamic acid (TXA), and dural tear classification.

### 4. Outcomes Measures, Parent Satisfaction & Complications
- **Whitaker Classification of Craniofacial Outcomes**:
  - *Category I*: Optimal structural result; no further surgery advised.
  - *Category II*: Minor contouring or soft tissue revisions.
  - *Category III*: Major bone graft or repeat osteotomy (less than original).
  - *Category IV*: Major craniofacial reoperation duplicating initial surgery (Redo).
- Postoperative Cephalic Index and $\Delta\text{CI}$ normalization index.
- **Parent-Reported Outcome Measures (PROM)**: 5-star overall satisfaction, head shape satisfaction, facial appearance satisfaction, family recommendation index.
- **Complications**: Dural tear, postoperative CSF leak, pseudomeningocele, surgical site infection (superficial vs deep osteomyelitis), bone flap resorption, hardware extrusion, re-synostosis recurrence.

### 5. Multidisciplinary Team (MDT) Inputs (Pre-op & Follow-ups)
Integrated input forms and longitudinal tables for 7 specialized disciplines:
1. **Paediatric Neurosurgeons**: ICP status, fontanelle tension, papilloedema, Chiari I tonsillar descent, CSF dynamics.
2. **Craniofacial / Plastic Surgeons**: Supraorbital bar projection, bandeau advancement, midface retrusion, scar assessment, Whitaker staging.
3. **Clinical Geneticists**: Syndromic assessment, dysmorphology examination, gene variant interpretation, recurrence risk counseling.
4. **Neuropsychologists**: Developmental quotients (DQ/IQ), Bayley-4, WPPSI, WISC, motor and adaptive milestones, parental stress.
5. **Speech & Language Therapists (SLT)**: Feeding and swallowing function, cleft palate evaluation, velopharyngeal competence (VPI status), hypernasality.
6. **Ophthalmologists**: Visual acuity, cycloplegic refraction, strabismus (V-pattern), exorbitism (Hertel mm), corneal exposure keratitis, optic nerve OCT.
7. **ENT & Respiratory / Sleep Specialists**: Upper airway patency, choanal stenosis, adenotonsillar hypertrophy, polysomnography AHI, CPAP compliance.

---

## 💻 Technical Architecture

- **Desktop Framework**: Tauri v2 + Rust + SQLite (Zero external runtime dependencies).
- **Web Frontend**: Modern modular web frontend (Vanilla HTML5 / CSS3 / ES Modules) with responsive clinical dark/light theme.
- **RBAC Security**: Role-Based Access Control (Developer, Administrator, Clinician) with SHA-256 hashed credentials and cryptographic audit ledger.
- **Export Engines**:
  - **Stata 114 / 118** binary dataset generator (`.dta`) for biostatistical modeling.
  - **Microsoft Excel** (`.csv`) export.
  - **JSON** full-schema database snapshot.
- **Clinical Letter Generators**:
  - Inpatient Craniofacial Surgery Discharge Summary.
  - Multidisciplinary Craniofacial Outpatient Clinic Review Letter.

---

## 🚀 Quick Launch (macOS & Windows)

### macOS One-Click Launch
Double-click:
```bash
./Launch_Paediatric_Craniofacial_DB.command
```
Or open in any modern browser:
```bash
open index.html
```

### Building Native Desktop Installers (Tauri)
To compile native `.dmg` (macOS) or `.msi` (Windows) packages:
```bash
npm run build
# Or build standalone frontend:
node build.js
```

---

## 👤 Attribution & Licensing

- **Conceived, designed and tested**: **Dr G Narenthiran MB ChB BSc(MedSci)(Hons) MRCS(Ed.) FEBNS FRCS(SN)**  
  *Consultant Paediatric Neurosurgeon*  
  *Email*: [g_narenthiran@hotmail.com](mailto:g_narenthiran@hotmail.com)  
  *Copyright © 2026, Dr G Narenthiran. All rights reserved.*

- **Dedication**:  
  *"Dedicated with utmost love and gratitude to Mrs Nirmaladevy Ganesalingam BSc."*
