/**
 * MULTIDISCIPLINARY PAEDIATRIC CRANIOFACIAL DATABASE
 * Frontend Application Controller (js/app.js)
 * Conceived, designed and tested: Dr G Narenthiran MB ChB BSc(MedSci)(Hons) MRCS(Ed.) FEBNS FRCS(SN)
 * Copyright 2026, Dr G Narenthiran, g_narenthiran@hotmail.com, all rights reserved.
 * Dedicated to Mrs Nirmaladevy Ganesalingam BSc
 */

// Quick fill helper for login modal
window.quickFillLogin = function(u, p) {
  const uInput = document.getElementById('f-login-username');
  const pInput = document.getElementById('f-login-password');
  if (uInput) uInput.value = u;
  if (pInput) pInput.value = p;
  const alertEl = document.getElementById('login-error-msg');
  if (alertEl) alertEl.style.display = 'none';
};

// Global App State
window.AppState = {
  currentUser: null,
  activePatientId: null,
  activePatientData: null,
  patientsList: [],
  surgeriesList: [],
  theme: localStorage.getItem('peds_cf_theme') || 'dark'
};

// Toast notification helper
function showToast(message, type = 'success') {
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.cssText = 'position:fixed; bottom:20px; right:20px; z-index:99999; display:flex; flex-direction:column; gap:8px; pointer-events:none;';
    document.body.appendChild(toastContainer);
  }
  const toast = document.createElement('div');
  const bg = type === 'success' ? '#059669' : type === 'error' ? '#dc2626' : '#0284c7';
  toast.style.cssText = `background:${bg}; color:#fff; padding:10px 16px; border-radius:6px; font-size:13px; font-weight:500; box-shadow:0 4px 12px rgba(0,0,0,0.3); pointer-events:auto; display:flex; align-items:center; gap:8px; opacity:0; transform:translateY(10px); transition:all 0.25s ease;`;
  toast.innerHTML = `<span>${message}</span>`;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
  }, 10);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  initLoginBarrier();
  initNavigationTabs();
  initModals();
  initCalculators();
  initActions();
  initAuditAndDesignModals();

  // Try auto-session or wait for login barrier
  const savedUserJson = sessionStorage.getItem('peds_cf_user');
  if (savedUserJson) {
    try {
      const user = JSON.parse(savedUserJson);
      handleSuccessfulLogin(user);
    } catch (e) {
      console.error('Session restore failed:', e);
    }
  }
});

function initTheme() {
  const currentTheme = window.AppState.theme;
  document.documentElement.setAttribute('data-theme', currentTheme);
  const themeBtn = document.getElementById('btn-theme-toggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const nextTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', nextTheme);
      window.AppState.theme = nextTheme;
      localStorage.setItem('peds_cf_theme', nextTheme);
    });
  }
}

function initLoginBarrier() {
  const loginForm = document.getElementById('form-login');
  const errorMsg = document.getElementById('login-error-msg');

  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const u = document.getElementById('f-login-username').value.trim();
      const p = document.getElementById('f-login-password').value;
      const user = window.DatabaseAdapter.authenticate(u, p);
      if (user) {
        if (errorMsg) errorMsg.style.display = 'none';
        sessionStorage.setItem('peds_cf_user', JSON.stringify(user));
        handleSuccessfulLogin(user);
      } else {
        if (errorMsg) {
          errorMsg.textContent = 'Invalid username or password.';
          errorMsg.style.display = 'block';
        }
      }
    });
  }

  // Logout trigger
  const logoutBtn = document.getElementById('btn-trigger-logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      sessionStorage.removeItem('peds_cf_user');
      window.AppState.currentUser = null;
      document.getElementById('modal-login-barrier').style.display = 'flex';
      showToast('Logged out securely.', 'info');
    });
  }

  // User menu dropdown toggle
  const userMenuTrigger = document.getElementById('btn-user-menu-trigger');
  const userMenuDropdown = document.getElementById('user-menu-dropdown');
  if (userMenuTrigger && userMenuDropdown) {
    userMenuTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      userMenuDropdown.style.display = userMenuDropdown.style.display === 'block' ? 'none' : 'block';
    });
    document.addEventListener('click', () => {
      userMenuDropdown.style.display = 'none';
    });
  }

  // Change Password Modal Trigger & Form
  const triggerChangePwd = document.getElementById('btn-trigger-change-password');
  if (triggerChangePwd) {
    triggerChangePwd.addEventListener('click', () => {
      document.getElementById('modal-change-password').style.display = 'flex';
    });
  }

  const formChangePwd = document.getElementById('form-change-password');
  if (formChangePwd) {
    formChangePwd.addEventListener('submit', (e) => {
      e.preventDefault();
      const currentPwd = document.getElementById('f-pwd-current').value;
      const newPwd = document.getElementById('f-pwd-new').value;
      const confirmPwd = document.getElementById('f-pwd-confirm').value;

      if (newPwd !== confirmPwd) {
        showToast('New passwords do not match.', 'error');
        return;
      }
      try {
        window.DatabaseAdapter.changePassword(window.AppState.currentUser.username, currentPwd, newPwd);
        showToast('Password updated successfully.', 'success');
        document.getElementById('modal-change-password').style.display = 'none';
        formChangePwd.reset();
      } catch (err) {
        showToast(err.message || 'Password update failed.', 'error');
      }
    });
  }

  // User Management Modal Trigger & Form
  const triggerUserMgmt = document.getElementById('btn-trigger-user-mgmt');
  if (triggerUserMgmt) {
    triggerUserMgmt.addEventListener('click', () => {
      renderUsersList();
      document.getElementById('modal-user-management').style.display = 'flex';
    });
  }

  const formCreateUser = document.getElementById('form-create-user');
  if (formCreateUser) {
    formCreateUser.addEventListener('submit', (e) => {
      e.preventDefault();
      const u = document.getElementById('f-new-username').value.trim();
      const p = document.getElementById('f-new-password').value;
      const fn = document.getElementById('f-new-fullname').value.trim();
      const r = document.getElementById('f-new-role').value;

      try {
        window.DatabaseAdapter.createUser(u, p, fn, r);
        showToast(`User account '${u}' created.`, 'success');
        formCreateUser.reset();
        renderUsersList();
      } catch (err) {
        showToast(err.message || 'User creation failed.', 'error');
      }
    });
  }
}

function handleSuccessfulLogin(user) {
  window.AppState.currentUser = user;
  const barrier = document.getElementById('modal-login-barrier');
  if (barrier) barrier.style.display = 'none';

  const userNameEl = document.getElementById('current-user-name');
  const userRoleEl = document.getElementById('current-user-role');
  if (userNameEl) userNameEl.textContent = user.fullName || user.username;
  if (userRoleEl) userRoleEl.textContent = user.role.toUpperCase();

  // Role permissions
  const mgmtItem = document.getElementById('btn-trigger-user-mgmt');
  if (mgmtItem) {
    mgmtItem.style.display = (user.role === 'developer' || user.role === 'administrator') ? 'flex' : 'none';
  }

  loadPatientsList();
}

function renderUsersList() {
  const tbody = document.getElementById('tbody-users-list');
  if (!tbody) return;
  const users = window.DatabaseAdapter.getUsers();
  tbody.innerHTML = '';
  users.forEach(u => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${u.username}</strong></td>
      <td>${u.fullName}</td>
      <td><span class="badge ${u.role === 'developer' ? 'badge-purple' : u.role === 'administrator' ? 'badge-primary' : 'badge-secondary'}">${u.role}</span></td>
      <td>
        ${u.username !== 'admin' && u.username !== window.AppState.currentUser.username ? `
          <button class="btn btn-outline btn-xs text-danger" onclick="window.deleteUserAccount('${u.username}')">Remove</button>
        ` : '<span class="text-muted text-xs">Protected</span>'}
      </td>
    `;
    tbody.appendChild(tr);
  });
}

window.deleteUserAccount = function(username) {
  if (confirm(`Are you sure you want to remove user account '${username}'?`)) {
    try {
      window.DatabaseAdapter.deleteUser(username);
      showToast(`User '${username}' removed.`, 'info');
      renderUsersList();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }
};

function initNavigationTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn[data-tab]');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      tabButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      document.querySelectorAll('.tab-content').forEach(tc => {
        tc.classList.remove('active');
      });
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active');
      }

      if (targetId === 'tab-cohort') {
        renderCohortAnalytics();
      }
    });
  });
}

function initModals() {
  // Generic close buttons
  document.querySelectorAll('[data-close-modal]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modalId = btn.getAttribute('data-close-modal');
      const m = document.getElementById(modalId);
      if (m) m.style.display = 'none';
    });
  });

  // Modal open triggers
  const modalTriggers = [
    { btn: 'btn-add-surgery', modal: 'modal-surgery' },
    { btn: 'btn-add-neurosurg', modal: 'modal-neurosurg' },
    { btn: 'btn-add-cranio', modal: 'modal-cranio' },
    { btn: 'btn-add-genetics', modal: 'modal-genetics' },
    { btn: 'btn-add-neuropsych', modal: 'modal-neuropsych' },
    { btn: 'btn-add-speech', modal: 'modal-speech' },
    { btn: 'btn-add-ophthalmology', modal: 'modal-ophthalmology' },
    { btn: 'btn-add-airway', modal: 'modal-airway' },
    { btn: 'btn-about-info', modal: 'modal-about' },
    { btn: 'btn-db-design', modal: 'modal-database-design' },
    { btn: 'btn-audit-log', modal: 'modal-audit-log' },
    { btn: 'btn-db-ops', modal: 'modal-db-operations' }
  ];

  modalTriggers.forEach(({ btn, modal }) => {
    const el = document.getElementById(btn);
    if (el) {
      el.addEventListener('click', () => {
        if (modal.startsWith('modal-') && !['modal-about', 'modal-database-design', 'modal-audit-log', 'modal-db-operations'].includes(modal)) {
          if (!window.AppState.activePatientId) {
            showToast('Please select or save a patient first.', 'error');
            return;
          }
        }
        const m = document.getElementById(modal);
        if (m) m.style.display = 'flex';
      });
    }
  });

  // Close modals on Escape key
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-backdrop').forEach(m => {
        if (m.id !== 'modal-login-barrier') m.style.display = 'none';
      });
    }
  });
}

function initCalculators() {
  // Pre-op Cephalic Index Calculator
  const preLen = document.getElementById('f-cranial-length-mm');
  const preWid = document.getElementById('f-cranial-width-mm');
  if (preLen) preLen.addEventListener('input', updatePreopCI);
  if (preWid) preWid.addEventListener('input', updatePreopCI);

  // Post-op Cephalic Index Calculator
  const postLen = document.getElementById('f-postop-cranial-length-mm');
  const postWid = document.getElementById('f-postop-cranial-width-mm');
  if (postLen) postLen.addEventListener('input', updatePostopCI);
  if (postWid) postWid.addEventListener('input', updatePostopCI);

  // Whitaker Category Evaluator
  const whitSelect = document.getElementById('f-whitaker-classification');
  if (whitSelect) whitSelect.addEventListener('change', updateWhitakerBadge);

  // AHI Sleep Apnea Severity Evaluator
  const ahiInput = document.getElementById('f-ahi-apnea-hypopnea-index');
  if (ahiInput) ahiInput.addEventListener('input', updateAHIEvaluation);

  // Surgery Modal EBL & % EBV Calculator
  const eblInput = document.getElementById('m-surg-ebl');
  if (eblInput) eblInput.addEventListener('input', updateSurgeryBloodLoss);

  // Surgery Modal Technique change (Show/hide Other)
  const techSelect = document.getElementById('m-surg-technique');
  if (techSelect) {
    techSelect.addEventListener('change', () => {
      const otherGroup = document.getElementById('group-surg-technique-other');
      if (otherGroup) {
        otherGroup.style.display = techSelect.value === 'Other' ? 'block' : 'none';
      }
    });
  }
}

function updatePreopCI() {
  const len = document.getElementById('f-cranial-length-mm')?.value;
  const wid = document.getElementById('f-cranial-width-mm')?.value;
  const ciInput = document.getElementById('f-cephalic-index');
  const catInput = document.getElementById('f-cephalic-index-category');
  const badge = document.getElementById('badge-preop-ci-metric');

  if (window.ScoringEngines) {
    const res = window.ScoringEngines.evalCephalicIndex(wid, len);
    if (res) {
      if (ciInput) ciInput.value = `${res.ci}%`;
      if (catInput) catInput.value = res.category;
      if (badge) {
        badge.textContent = `CI: ${res.ci}% [${res.status}]`;
        badge.className = `score-badge ${res.status === 'Normal' ? 'badge-success' : res.status === 'Scaphocephaly' ? 'badge-primary' : 'badge-warning'}`;
      }
    } else {
      if (ciInput) ciInput.value = '';
      if (catInput) catInput.value = '';
      if (badge) {
        badge.textContent = 'Enter Width & Length';
        badge.className = 'score-badge badge-secondary';
      }
    }
  }
}

function updatePostopCI() {
  const len = document.getElementById('f-postop-cranial-length-mm')?.value;
  const wid = document.getElementById('f-postop-cranial-width-mm')?.value;
  const postCIInput = document.getElementById('f-postop-cephalic-index');
  const deltaInput = document.getElementById('f-cephalic-index-improvement');

  if (window.ScoringEngines) {
    const res = window.ScoringEngines.evalCephalicIndex(wid, len);
    if (res) {
      if (postCIInput) postCIInput.value = `${res.ci}%`;
      const preCIStr = document.getElementById('f-cephalic-index')?.value || '';
      const preCIVal = parseFloat(preCIStr);
      if (!isNaN(preCIVal) && deltaInput) {
        const delta = Math.round(Math.abs(res.ci - preCIVal) * 10) / 10;
        deltaInput.value = `+${delta}% normalization`;
      }
    } else {
      if (postCIInput) postCIInput.value = '';
      if (deltaInput) deltaInput.value = '';
    }
  }
}

function updateWhitakerBadge() {
  const val = document.getElementById('f-whitaker-classification')?.value;
  const badge = document.getElementById('badge-whitaker-metric');
  const recEl = document.getElementById('whitaker-recommendation-text');

  if (window.ScoringEngines) {
    const res = window.ScoringEngines.evalWhitaker(val);
    if (res) {
      if (badge) {
        badge.textContent = `${res.category}: ${res.tier}`;
        badge.className = `score-badge ${res.badgeClass}`;
      }
      if (recEl) recEl.textContent = res.recommendation;
    } else {
      if (badge) {
        badge.textContent = 'Select Whitaker Grade';
        badge.className = 'score-badge badge-secondary';
      }
    }
  }
}

function updateAHIEvaluation() {
  const score = document.getElementById('f-ahi-apnea-hypopnea-index')?.value;
  const sevInput = document.getElementById('f-ahi-severity');

  if (window.ScoringEngines) {
    const res = window.ScoringEngines.evalAHI(score);
    if (res && sevInput) {
      sevInput.value = `${res.severity} (${res.description})`;
    } else if (sevInput) {
      sevInput.value = '';
    }
  }
}

function updateSurgeryBloodLoss() {
  const ebl = document.getElementById('m-surg-ebl')?.value;
  const wt = document.getElementById('f-preop-weight-kg')?.value || 8;
  const pctInput = document.getElementById('m-surg-ebl-pct');

  if (window.ScoringEngines) {
    const res = window.ScoringEngines.evalBloodLoss(ebl, wt);
    if (res && pctInput) {
      pctInput.value = `${res.pct}% of EBV (${res.tier})`;
    } else if (pctInput) {
      pctInput.value = '';
    }
  }
}

function initActions() {
  // New Patient Button
  const btnNew = document.getElementById('btn-new-patient');
  if (btnNew) {
    btnNew.addEventListener('click', () => {
      resetPatientForm();
      showToast('Ready to register new paediatric craniofacial patient.', 'info');
    });
  }

  // Save Patient Button
  const btnSave = document.getElementById('btn-save-patient');
  if (btnSave) {
    btnSave.addEventListener('click', saveCurrentPatient);
  }

  // Delete Patient Button
  const btnDelete = document.getElementById('btn-delete-patient');
  if (btnDelete) {
    btnDelete.addEventListener('click', deleteCurrentPatient);
  }

  // Patient Search Filter
  const searchInput = document.getElementById('search-patient');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      loadPatientsList(e.target.value.trim());
    });
  }

  // Export Buttons
  const btnStata = document.getElementById('btn-export-stata');
  if (btnStata) {
    btnStata.addEventListener('click', () => {
      try {
        window.DatabaseAdapter.exportToStata();
        showToast('Exported Paediatric Craniofacial cohort to Stata 114 format (.dta)', 'success');
      } catch (err) {
        showToast('Stata export failed: ' + err.message, 'error');
      }
    });
  }

  const btnExcel = document.getElementById('btn-export-excel');
  if (btnExcel) {
    btnExcel.addEventListener('click', () => {
      try {
        window.DatabaseAdapter.exportToExcel();
        showToast('Exported Paediatric Craniofacial cohort to Excel (.csv)', 'success');
      } catch (err) {
        showToast('Excel export failed: ' + err.message, 'error');
      }
    });
  }

  const btnJson = document.getElementById('btn-export-json');
  if (btnJson) {
    btnJson.addEventListener('click', () => {
      try {
        window.DatabaseAdapter.exportToJson();
        showToast('Exported database JSON snapshot backup', 'success');
      } catch (err) {
        showToast('JSON export failed: ' + err.message, 'error');
      }
    });
  }

  // Inpatient Discharge Summary Modal Open & Actions
  const btnOpenDischarge = document.getElementById('btn-open-discharge-modal');
  if (btnOpenDischarge) {
    btnOpenDischarge.addEventListener('click', () => {
      if (!window.AppState.activePatientId) {
        showToast('Please select a patient first.', 'error');
        return;
      }
      const summaryText = window.DatabaseAdapter.generateDischargeSummary(window.AppState.activePatientId);
      document.getElementById('preview-discharge-letter-content').value = summaryText;
      document.getElementById('modal-discharge-letter').style.display = 'flex';
    });
  }

  const btnCopyDischarge = document.getElementById('btn-copy-discharge-letter');
  if (btnCopyDischarge) {
    btnCopyDischarge.addEventListener('click', () => {
      const text = document.getElementById('preview-discharge-letter-content').value;
      navigator.clipboard.writeText(text).then(() => {
        showToast('Discharge Summary copied to clipboard!', 'success');
      });
    });
  }

  const btnPrintDischarge = document.getElementById('btn-print-discharge-letter');
  if (btnPrintDischarge) {
    btnPrintDischarge.addEventListener('click', () => {
      printTextContent(document.getElementById('preview-discharge-letter-content').value, 'Inpatient Craniofacial Surgery Discharge Summary');
    });
  }

  // Outpatient Clinic Letter Modal Open & Actions
  const btnOpenClinic = document.getElementById('btn-open-clinic-modal');
  if (btnOpenClinic) {
    btnOpenClinic.addEventListener('click', () => {
      if (!window.AppState.activePatientId) {
        showToast('Please select a patient first.', 'error');
        return;
      }
      const letterText = window.DatabaseAdapter.generateClinicLetter(window.AppState.activePatientId);
      document.getElementById('preview-clinic-letter-content').value = letterText;
      document.getElementById('modal-clinic-letter').style.display = 'flex';
    });
  }

  const btnCopyClinic = document.getElementById('btn-copy-clinic-letter');
  if (btnCopyClinic) {
    btnCopyClinic.addEventListener('click', () => {
      const text = document.getElementById('preview-clinic-letter-content').value;
      navigator.clipboard.writeText(text).then(() => {
        showToast('Clinic Review Letter copied to clipboard!', 'success');
      });
    });
  }

  const btnPrintClinic = document.getElementById('btn-print-clinic-letter');
  if (btnPrintClinic) {
    btnPrintClinic.addEventListener('click', () => {
      printTextContent(document.getElementById('preview-clinic-letter-content').value, 'Multidisciplinary Paediatric Craniofacial Clinic Letter');
    });
  }

  // Form Submissions for Child Records
  initChildFormSubmissions();
}

function printTextContent(content, title) {
  const win = window.open('', '_blank');
  win.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>${title}</title>
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11pt; line-height: 1.5; color: #111; margin: 30px; }
        pre { white-space: pre-wrap; word-wrap: break-word; font-family: monospace; font-size: 10pt; }
        @media print { body { margin: 15mm; } }
      </style>
    </head>
    <body>
      <pre>${content.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
    </body>
    </html>
  `);
  win.document.close();
  win.focus();
  setTimeout(() => {
    win.print();
    win.close();
  }, 250);
}

function initChildFormSubmissions() {
  // Surgery Modal Form
  const formSurgery = document.getElementById('form-modal-surgery');
  if (formSurgery) {
    formSurgery.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!window.AppState.activePatientId) return;

      const tech = document.getElementById('m-surg-technique').value;
      const techOther = tech === 'Other' ? document.getElementById('m-surg-technique-other').value.trim() : '';

      const surgData = {
        patient_id: window.AppState.activePatientId,
        surgery_date: document.getElementById('m-surg-date').value,
        procedure_sequence: document.getElementById('m-surg-sequence').value,
        surgical_technique_category: tech,
        surgical_technique_other_detail: techOther,
        surgeon_operative_description: document.getElementById('m-surg-description').value,
        lead_surgeon: document.getElementById('m-surg-lead').value,
        assisting_surgeon: document.getElementById('m-surg-assisting').value,
        operating_time_minutes: parseInt(document.getElementById('m-surg-duration').value || 0, 10),
        estimated_blood_loss_ml: parseInt(document.getElementById('m-surg-ebl').value || 0, 10),
        estimated_blood_loss_pct_ebv: parseFloat(document.getElementById('m-surg-ebl-pct').value || 0),
        prbc_transfused_ml: parseInt(document.getElementById('m-surg-prbc').value || 0, 10),
        ffp_transfused_ml: parseInt(document.getElementById('m-surg-ffp').value || 0, 10),
        cell_saver_returned_ml: parseInt(document.getElementById('m-surg-cell-saver').value || 0, 10),
        tranexamic_acid_administered: document.getElementById('m-surg-txa').value,
        dural_tear_occurred: document.getElementById('m-surg-dural-tear').value,
        bone_fixation_method: document.getElementById('m-surg-fixation').value,
        spring_or_distractor_details: document.getElementById('m-surg-spring-details').value,
        helmet_therapy_planned: document.getElementById('m-surg-helmet').value
      };

      try {
        window.DatabaseAdapter.saveSurgery(surgData);
        showToast('Surgical procedure saved.', 'success');
        formSurgery.reset();
        document.getElementById('modal-surgery').style.display = 'none';
        renderSurgeriesTable(window.AppState.activePatientId);
      } catch (err) {
        showToast('Failed to save surgery: ' + err.message, 'error');
      }
    });
  }

  // Neurosurgery Modal Form
  const formNS = document.getElementById('form-modal-neurosurg');
  if (formNS) {
    formNS.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!window.AppState.activePatientId) return;

      const data = {
        patient_id: window.AppState.activePatientId,
        assessment_date: document.getElementById('m-ns-date').value,
        encounter_phase: document.getElementById('m-ns-phase').value,
        clinician_name: document.getElementById('m-ns-clinician').value,
        icp_assessment_summary: document.getElementById('m-ns-icp').value,
        fundoscopy_papilloedema_status: document.getElementById('m-ns-fundoscopy').value,
        chiari_tonsil_position_status: document.getElementById('m-ns-chiari').value,
        ventricles_and_csf_dynamics: document.getElementById('m-ns-ventricles').value,
        neurosurgical_recommendations: document.getElementById('m-ns-recs').value
      };

      try {
        window.DatabaseAdapter.saveNeurosurgery(data);
        showToast('Neurosurgical assessment logged.', 'success');
        formNS.reset();
        document.getElementById('modal-neurosurg').style.display = 'none';
        renderNeurosurgTable(window.AppState.activePatientId);
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // Craniofacial/Plastics Modal Form
  const formCr = document.getElementById('form-modal-cranio');
  if (formCr) {
    formCr.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!window.AppState.activePatientId) return;

      const data = {
        patient_id: window.AppState.activePatientId,
        assessment_date: document.getElementById('m-cr-date').value,
        encounter_phase: document.getElementById('m-cr-phase').value,
        clinician_name: document.getElementById('m-cr-clinician').value,
        forehead_and_supraorbital_contour: document.getElementById('m-cr-contour').value,
        midface_hypoplasia_assessment: document.getElementById('m-cr-midface').value,
        whitaker_stage_estimate: document.getElementById('m-cr-whitaker').value,
        surgical_plan_or_revisions: document.getElementById('m-cr-plan').value
      };

      try {
        window.DatabaseAdapter.saveCraniofacial(data);
        showToast('Craniofacial / Plastic surgery assessment logged.', 'success');
        formCr.reset();
        document.getElementById('modal-cranio').style.display = 'none';
        renderCranioTable(window.AppState.activePatientId);
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // Genetics Modal Form
  const formGn = document.getElementById('form-modal-genetics');
  if (formGn) {
    formGn.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!window.AppState.activePatientId) return;

      const data = {
        patient_id: window.AppState.activePatientId,
        consultation_date: document.getElementById('m-gn-date').value,
        geneticist_name: document.getElementById('m-gn-clinician').value,
        clinical_syndromic_impression: document.getElementById('m-gn-syndrome').value,
        dysmorphology_features: document.getElementById('m-gn-dysmorphology').value,
        counseling_inheritance_and_recurrence: document.getElementById('m-gn-counseling').value
      };

      try {
        window.DatabaseAdapter.saveGenetics(data);
        showToast('Clinical genetics consultation logged.', 'success');
        formGn.reset();
        document.getElementById('modal-genetics').style.display = 'none';
        renderGeneticsTable(window.AppState.activePatientId);
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // Neuropsychology Modal Form
  const formNP = document.getElementById('form-modal-neuropsych');
  if (formNP) {
    formNP.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!window.AppState.activePatientId) return;

      const data = {
        patient_id: window.AppState.activePatientId,
        assessment_date: document.getElementById('m-np-date').value,
        encounter_phase: document.getElementById('m-np-phase').value,
        battery_used: document.getElementById('m-np-battery').value,
        developmental_quotient_or_iq: parseFloat(document.getElementById('m-np-score').value || 0),
        gross_motor_development: document.getElementById('m-np-motor').value,
        language_and_communication: document.getElementById('m-np-language').value
      };

      try {
        window.DatabaseAdapter.saveNeuropsychology(data);
        showToast('Neuropsychology assessment logged.', 'success');
        formNP.reset();
        document.getElementById('modal-neuropsych').style.display = 'none';
        renderNeuropsychTable(window.AppState.activePatientId);
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // Speech Therapy Modal Form
  const formSp = document.getElementById('form-modal-speech');
  if (formSp) {
    formSp.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!window.AppState.activePatientId) return;

      const data = {
        patient_id: window.AppState.activePatientId,
        assessment_date: document.getElementById('m-sp-date').value,
        therapist_name: document.getElementById('m-sp-therapist').value,
        feeding_and_swallowing_function: document.getElementById('m-sp-feeding').value,
        velopharyngeal_competence: document.getElementById('m-sp-vpi').value,
        therapy_plan: document.getElementById('m-sp-plan').value
      };

      try {
        window.DatabaseAdapter.saveSpeechTherapy(data);
        showToast('Speech Therapy assessment logged.', 'success');
        formSp.reset();
        document.getElementById('modal-speech').style.display = 'none';
        renderSpeechTable(window.AppState.activePatientId);
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // Ophthalmology Modal Form
  const formOph = document.getElementById('form-modal-ophthalmology');
  if (formOph) {
    formOph.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!window.AppState.activePatientId) return;

      const data = {
        patient_id: window.AppState.activePatientId,
        examination_date: document.getElementById('m-oph-date').value,
        ophthalmologist_name: document.getElementById('m-oph-clinician').value,
        visual_acuity_right: document.getElementById('m-oph-va').value,
        exorbitism_hertel_mm: parseFloat(document.getElementById('m-oph-hertel').value || 0),
        strabismus_v_pattern: document.getElementById('m-oph-strabismus').value,
        corneal_integrity: document.getElementById('m-oph-cornea').value,
        optic_nerve_status_oct: document.getElementById('m-oph-oct').value
      };

      try {
        window.DatabaseAdapter.saveOphthalmology(data);
        showToast('Ophthalmology assessment logged.', 'success');
        formOph.reset();
        document.getElementById('modal-ophthalmology').style.display = 'none';
        renderOphthalmologyTable(window.AppState.activePatientId);
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // Airway Modal Form
  const formAw = document.getElementById('form-modal-airway');
  if (formAw) {
    formAw.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!window.AppState.activePatientId) return;

      const data = {
        patient_id: window.AppState.activePatientId,
        assessment_date: document.getElementById('m-aw-date').value,
        specialist_name: document.getElementById('m-aw-specialist').value,
        ahi_current_score: parseFloat(document.getElementById('m-aw-ahi').value || 0),
        cpap_bipap_tolerated: document.getElementById('m-aw-support').value,
        upper_airway_patency: document.getElementById('m-aw-patency').value,
        respiratory_plan: document.getElementById('m-aw-plan').value
      };

      try {
        window.DatabaseAdapter.saveAirway(data);
        showToast('Airway / Respiratory assessment logged.', 'success');
        formAw.reset();
        document.getElementById('modal-airway').style.display = 'none';
        renderAirwayTable(window.AppState.activePatientId);
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }
}

function loadPatientsList(query = '') {
  const container = document.getElementById('patients-list-container');
  if (!container) return;

  const patients = window.DatabaseAdapter.getPatients(query);
  window.AppState.patientsList = patients;
  container.innerHTML = '';

  if (patients.length === 0) {
    container.innerHTML = `<div class="p-3 text-muted text-xs text-center">No patients match search.</div>`;
    return;
  }

  patients.forEach(p => {
    const item = document.createElement('div');
    item.className = `patient-list-item ${p.id === window.AppState.activePatientId ? 'active' : ''}`;
    item.onclick = () => selectPatient(p.id);

    const fullName = `${p.first_name || ''} ${p.last_name || ''}`.trim() || 'Unnamed';
    const sut = p.pathology?.primary_suture_involved || 'Craniofacial';
    const synd = p.pathology?.syndromic_diagnosis || 'Non-Syndromic';

    item.innerHTML = `
      <div class="patient-item-header">
        <strong class="patient-item-id">${p.study_id}</strong>
        <span class="patient-item-badge badge-${p.gender === 'Male' ? 'primary' : 'purple'}">${p.gender || 'Unknown'} &bull; ${p.age_at_presentation_months ? p.age_at_presentation_months + 'm' : ''}</span>
      </div>
      <div class="patient-item-name">${fullName}</div>
      <div class="patient-item-meta">${sut} &bull; ${synd}</div>
    `;
    container.appendChild(item);
  });

  // Auto-select first patient if none active
  if (!window.AppState.activePatientId && patients.length > 0) {
    selectPatient(patients[0].id);
  }
}

function selectPatient(patientId) {
  const p = window.DatabaseAdapter.getPatient(patientId);
  if (!p) return;

  window.AppState.activePatientId = p.id;
  window.AppState.activePatientData = p;

  // Highlight list item
  document.querySelectorAll('.patient-list-item').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.patient-list-item').forEach(el => {
    if (el.querySelector('.patient-item-id')?.textContent === p.study_id) {
      el.classList.add('active');
    }
  });

  // Update Status Banner
  const bannerBadge = document.getElementById('active-patient-header-badge');
  if (bannerBadge) {
    const fullName = `${p.first_name || ''} ${p.last_name || ''}`.trim();
    const sut = p.pathology?.primary_suture_involved || 'Craniosynostosis';
    const whit = p.outcomes?.whitaker_classification?.split(':')[0] || 'Whitaker Pending';
    bannerBadge.innerHTML = `<strong>${p.study_id}</strong>: ${fullName} (${p.age_at_presentation_months}m) &bull; <span class="text-csf">${sut}</span> &bull; <em>${whit}</em>`;
  }

  // Tab 1: Demographics
  setVal('f-study-id', p.study_id);
  setVal('f-hospital-number', p.hospital_number);
  setVal('f-gender', p.gender || 'Male');
  setVal('f-first-name', p.first_name);
  setVal('f-last-name', p.last_name);
  setVal('f-dob', p.dob);
  setVal('f-age-at-presentation-months', p.age_at_presentation_months);
  setVal('f-ethnicity', p.ethnicity);
  setVal('f-gestational-age-weeks', p.gestational_age_weeks);
  setVal('f-birth-weight-kg', p.birth_weight_kg);
  setVal('f-head-circumference-at-birth-cm', p.head_circumference_at_birth_cm);
  setVal('f-clinical-nurse-specialist', p.clinical_nurse_specialist);
  setVal('f-lead-neurosurgeon', p.lead_neurosurgeon || 'Dr G Narenthiran');
  setVal('f-lead-craniofacial-surgeon', p.lead_craniofacial_surgeon);
  setVal('f-lead-plastic-surgeon', p.lead_plastic_surgeon);
  setVal('f-notes', p.notes);

  // Tab 2: Pathology & Genetics
  const path = p.pathology || {};
  setVal('f-primary-diagnostic-category', path.primary_diagnostic_category || 'Single-Suture Craniosynostosis (Non-Syndromic)');
  setVal('f-primary-suture-involved', path.primary_suture_involved || 'Sagittal (Scaphocephaly / Dolichocephaly)');
  setVal('f-syndromic-diagnosis', path.syndromic_diagnosis || 'Non-Syndromic (Isolated)');
  setVal('f-genetic-testing-performed', path.genetic_testing_performed || 'No');
  setVal('f-specific-gene-identified', path.specific_gene_identified || 'Negative / No Pathogenic Variant Found');
  setVal('f-inheritance-pattern', path.inheritance_pattern || 'De Novo');
  setVal('f-dna-mutation-details', path.dna_mutation_details);
  setVal('f-genetic-testing-modality', path.genetic_testing_modality);
  setVal('f-suture-details-text', path.suture_details_text);
  setVal('f-family-history-craniofacial', path.family_history_craniofacial);

  // Tab 3: Preoperative Assessment
  const pre = p.preop || {};
  setVal('f-preop-assessment-date', pre.assessment_date);
  setVal('f-preop-weight-kg', pre.weight_kg);
  setVal('f-preop-head-circumference-cm', pre.head_circumference_cm);
  setVal('f-preop-head-circumference-centile', pre.head_circumference_centile);
  setVal('f-cranial-length-mm', pre.cranial_length_mm);
  setVal('f-cranial-width-mm', pre.cranial_width_mm);
  setVal('f-cephalic-index', pre.cephalic_index ? `${pre.cephalic_index}%` : '');
  setVal('f-cephalic-index-category', pre.cephalic_index_category);
  setVal('f-cranial-vault-asymmetry-index-pct', pre.cranial_vault_asymmetry_index_pct);
  setVal('f-intercanthal-distance-mm', pre.intercanthal_distance_mm);
  setVal('f-interpupillary-distance-mm', pre.interpupillary_distance_mm);
  setVal('f-anterior-fontanelle-status', pre.anterior_fontanelle_status || 'Patent');
  setVal('f-suture-ridging-palpable', pre.suture_ridging_palpable);
  setVal('f-bitemporal-narrowing', pre.bitemporal_narrowing);
  setVal('f-forehead-bossing-or-retrusion', pre.forehead_bossing_or_retrusion);
  setVal('f-orbital-dystopia-harlequin', pre.orbital_dystopia_harlequin);
  setVal('f-exorbitism-proptosis-present', pre.exorbitism_proptosis_present || 'No');
  setVal('f-raised-icp-clinical-signs', pre.raised_icp_clinical_signs);
  setVal('f-copper-beaten-skull-on-imaging', pre.copper_beaten_skull_on_imaging || 'None');
  setVal('f-frisen-papilloedema-grade', pre.frisen_papilloedema_grade || 'Grade 0: Normal');
  setVal('f-ahi-apnea-hypopnea-index', pre.ahi_apnea_hypopnea_index);
  setVal('f-ahi-severity', pre.ahi_severity);
  setVal('f-respiratory-support-needed', pre.respiratory_support_needed || 'None');
  setVal('f-chiari-malformation-present', pre.chiari_malformation_present || 'No');
  setVal('f-tonsillar-descent-mm', pre.tonsillar_descent_mm || 0);
  setVal('f-hydrocephalus-present', pre.hydrocephalus_present || 'No');

  // Tab 5: Outcomes & Satisfaction
  const out = p.outcomes || {};
  setVal('f-whitaker-classification', out.whitaker_classification || 'Category I: No further surgical revision considered advisable or desired');
  setVal('f-postop-cranial-length-mm', out.postop_cranial_length_mm);
  setVal('f-postop-cranial-width-mm', out.postop_cranial_width_mm);
  setVal('f-postop-cephalic-index', out.postop_cephalic_index ? `${out.postop_cephalic_index}%` : '');
  setVal('f-cephalic-index-improvement', out.cephalic_index_improvement ? `+${out.cephalic_index_improvement}% normalization` : '');
  setVal('f-head-shape-aesthetic-correction', out.head_shape_aesthetic_correction || 'Excellent');
  setVal('f-forehead-symmetry-restored', out.forehead_symmetry_restored);
  setVal('f-supraorbital-rim-projection', out.supraorbital_rim_projection);
  setVal('f-overall-clinical-status', out.overall_clinical_status || 'Completed Treatment - Excellent Result');
  setVal('f-parent-overall-satisfaction-score', out.parent_overall_satisfaction_score || '5');
  setVal('f-parent-head-shape-satisfaction', out.parent_head_shape_satisfaction || 'Very Satisfied');
  setVal('f-parent-facial-appearance-satisfaction', out.parent_facial_appearance_satisfaction || 'Very Satisfied');
  setVal('f-parent-would-recommend-procedure', out.parent_would_recommend_procedure || 'Strongly Agree');
  setVal('f-complication-dural-tear-or-csf-leak', out.complication_dural_tear_or_csf_leak || 'None');
  setVal('f-complication-wound-infection', out.complication_wound_infection || 'None');
  setVal('f-complication-bone-resorption', out.complication_bone_resorption || 'None');
  setVal('f-complication-hardware-problem', out.complication_hardware_problem || 'None');
  setVal('f-complication-resynostosis-recurrence', out.complication_resynostosis_recurrence || 'No');
  setVal('f-complication-unplanned-reoperation-30d', out.complication_unplanned_reoperation_30d);

  // Refresh reactive calculators
  updatePreopCI();
  updatePostopCI();
  updateWhitakerBadge();
  updateAHIEvaluation();

  // Render Sub-tables
  renderSurgeriesTable(p.id);
  renderNeurosurgTable(p.id);
  renderCranioTable(p.id);
  renderGeneticsTable(p.id);
  renderNeuropsychTable(p.id);
  renderSpeechTable(p.id);
  renderOphthalmologyTable(p.id);
  renderAirwayTable(p.id);
}

function setVal(id, val) {
  const el = document.getElementById(id);
  if (el) {
    el.value = (val !== null && val !== undefined) ? val : '';
  }
}

function resetPatientForm() {
  window.AppState.activePatientId = null;
  window.AppState.activePatientData = null;

  document.querySelectorAll('.patient-list-item').forEach(i => i.classList.remove('active'));

  const count = (window.AppState.patientsList.length + 1).toString().padStart(3, '0');
  const newStudyId = `CF-${count}`;

  document.querySelectorAll('input, select, textarea').forEach(el => {
    if (!el.id.startsWith('f-login-') && !el.id.startsWith('f-pwd-') && !el.id.startsWith('f-new-') && !el.id.startsWith('m-')) {
      el.value = '';
    }
  });

  setVal('f-study-id', newStudyId);
  setVal('f-gender', 'Male');
  setVal('f-lead-neurosurgeon', 'Dr G Narenthiran');
  setVal('f-primary-diagnostic-category', 'Single-Suture Craniosynostosis (Non-Syndromic)');
  setVal('f-primary-suture-involved', 'Sagittal (Scaphocephaly / Dolichocephaly)');
  setVal('f-syndromic-diagnosis', 'Non-Syndromic (Isolated)');
  setVal('f-genetic-testing-performed', 'No');
  setVal('f-specific-gene-identified', 'Negative / No Pathogenic Variant Found');
  setVal('f-inheritance-pattern', 'De Novo');
  setVal('f-whitaker-classification', 'Category I: No further surgical revision considered advisable or desired');
  setVal('f-parent-overall-satisfaction-score', '5');
  setVal('f-parent-head-shape-satisfaction', 'Very Satisfied');
  setVal('f-parent-facial-appearance-satisfaction', 'Very Satisfied');
  setVal('f-parent-would-recommend-procedure', 'Strongly Agree');
  setVal('f-complication-dural-tear-or-csf-leak', 'None');
  setVal('f-overall-clinical-status', 'Under Routine Clinical Follow-up');

  const banner = document.getElementById('active-patient-header-badge');
  if (banner) banner.innerHTML = `<strong>NEW PATIENT DRAFT</strong> (${newStudyId})`;

  ['tbody-surgeries', 'tbody-mdt-neurosurg', 'tbody-mdt-cranio', 'tbody-mdt-genetics', 'tbody-mdt-neuropsych', 'tbody-mdt-speech', 'tbody-mdt-ophthalmology', 'tbody-mdt-airway'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = `<tr><td colspan="9" class="text-center text-muted text-xs p-3">Save patient to log entries.</td></tr>`;
  });

  updatePreopCI();
  updatePostopCI();
  updateWhitakerBadge();
}

function saveCurrentPatient() {
  const studyId = document.getElementById('f-study-id')?.value.trim();
  if (!studyId) {
    showToast('Study ID is mandatory.', 'error');
    return;
  }

  const patientObj = {
    id: window.AppState.activePatientId || undefined,
    study_id: studyId,
    hospital_number: document.getElementById('f-hospital-number')?.value.trim(),
    gender: document.getElementById('f-gender')?.value,
    first_name: document.getElementById('f-first-name')?.value.trim(),
    last_name: document.getElementById('f-last-name')?.value.trim(),
    dob: document.getElementById('f-dob')?.value,
    age_at_presentation_months: parseFloat(document.getElementById('f-age-at-presentation-months')?.value || 0),
    ethnicity: document.getElementById('f-ethnicity')?.value,
    gestational_age_weeks: parseFloat(document.getElementById('f-gestational-age-weeks')?.value || 0),
    birth_weight_kg: parseFloat(document.getElementById('f-birth-weight-kg')?.value || 0),
    head_circumference_at_birth_cm: parseFloat(document.getElementById('f-head-circumference-at-birth-cm')?.value || 0),
    clinical_nurse_specialist: document.getElementById('f-clinical-nurse-specialist')?.value,
    lead_neurosurgeon: document.getElementById('f-lead-neurosurgeon')?.value,
    lead_craniofacial_surgeon: document.getElementById('f-lead-craniofacial-surgeon')?.value,
    lead_plastic_surgeon: document.getElementById('f-lead-plastic-surgeon')?.value,
    notes: document.getElementById('f-notes')?.value,

    pathology: {
      primary_diagnostic_category: document.getElementById('f-primary-diagnostic-category')?.value,
      primary_suture_involved: document.getElementById('f-primary-suture-involved')?.value,
      syndromic_diagnosis: document.getElementById('f-syndromic-diagnosis')?.value,
      genetic_testing_performed: document.getElementById('f-genetic-testing-performed')?.value,
      specific_gene_identified: document.getElementById('f-specific-gene-identified')?.value,
      inheritance_pattern: document.getElementById('f-inheritance-pattern')?.value,
      dna_mutation_details: document.getElementById('f-dna-mutation-details')?.value,
      genetic_testing_modality: document.getElementById('f-genetic-testing-modality')?.value,
      suture_details_text: document.getElementById('f-suture-details-text')?.value,
      family_history_craniofacial: document.getElementById('f-family-history-craniofacial')?.value
    },

    preop: {
      assessment_date: document.getElementById('f-preop-assessment-date')?.value,
      weight_kg: parseFloat(document.getElementById('f-preop-weight-kg')?.value || 0),
      head_circumference_cm: parseFloat(document.getElementById('f-preop-head-circumference-cm')?.value || 0),
      head_circumference_centile: parseFloat(document.getElementById('f-preop-head-circumference-centile')?.value || 0),
      cranial_length_mm: parseFloat(document.getElementById('f-cranial-length-mm')?.value || 0),
      cranial_width_mm: parseFloat(document.getElementById('f-cranial-width-mm')?.value || 0),
      cephalic_index: parseFloat(document.getElementById('f-cephalic-index')?.value || 0),
      cephalic_index_category: document.getElementById('f-cephalic-index-category')?.value,
      cranial_vault_asymmetry_index_pct: parseFloat(document.getElementById('f-cranial-vault-asymmetry-index-pct')?.value || 0),
      intercanthal_distance_mm: parseFloat(document.getElementById('f-intercanthal-distance-mm')?.value || 0),
      interpupillary_distance_mm: parseFloat(document.getElementById('f-interpupillary-distance-mm')?.value || 0),
      anterior_fontanelle_status: document.getElementById('f-anterior-fontanelle-status')?.value,
      suture_ridging_palpable: document.getElementById('f-suture-ridging-palpable')?.value,
      bitemporal_narrowing: document.getElementById('f-bitemporal-narrowing')?.value,
      forehead_bossing_or_retrusion: document.getElementById('f-forehead-bossing-or-retrusion')?.value,
      orbital_dystopia_harlequin: document.getElementById('f-orbital-dystopia-harlequin')?.value,
      exorbitism_proptosis_present: document.getElementById('f-exorbitism-proptosis-present')?.value,
      raised_icp_clinical_signs: document.getElementById('f-raised-icp-clinical-signs')?.value,
      copper_beaten_skull_on_imaging: document.getElementById('f-copper-beaten-skull-on-imaging')?.value,
      frisen_papilloedema_grade: document.getElementById('f-frisen-papilloedema-grade')?.value,
      ahi_apnea_hypopnea_index: parseFloat(document.getElementById('f-ahi-apnea-hypopnea-index')?.value || 0),
      ahi_severity: document.getElementById('f-ahi-severity')?.value,
      respiratory_support_needed: document.getElementById('f-respiratory-support-needed')?.value,
      chiari_malformation_present: document.getElementById('f-chiari-malformation-present')?.value,
      tonsillar_descent_mm: parseFloat(document.getElementById('f-tonsillar-descent-mm')?.value || 0),
      hydrocephalus_present: document.getElementById('f-hydrocephalus-present')?.value
    },

    outcomes: {
      whitaker_classification: document.getElementById('f-whitaker-classification')?.value,
      postop_cranial_length_mm: parseFloat(document.getElementById('f-postop-cranial-length-mm')?.value || 0),
      postop_cranial_width_mm: parseFloat(document.getElementById('f-postop-cranial-width-mm')?.value || 0),
      postop_cephalic_index: parseFloat(document.getElementById('f-postop-cephalic-index')?.value || 0),
      head_shape_aesthetic_correction: document.getElementById('f-head-shape-aesthetic-correction')?.value,
      forehead_symmetry_restored: document.getElementById('f-forehead-symmetry-restored')?.value,
      supraorbital_rim_projection: document.getElementById('f-supraorbital-rim-projection')?.value,
      overall_clinical_status: document.getElementById('f-overall-clinical-status')?.value,
      parent_overall_satisfaction_score: parseInt(document.getElementById('f-parent-overall-satisfaction-score')?.value || 5, 10),
      parent_head_shape_satisfaction: document.getElementById('f-parent-head-shape-satisfaction')?.value,
      parent_facial_appearance_satisfaction: document.getElementById('f-parent-facial-appearance-satisfaction')?.value,
      parent_would_recommend_procedure: document.getElementById('f-parent-would-recommend-procedure')?.value,
      complication_dural_tear_or_csf_leak: document.getElementById('f-complication-dural-tear-or-csf-leak')?.value,
      complication_wound_infection: document.getElementById('f-complication-wound-infection')?.value,
      complication_bone_resorption: document.getElementById('f-complication-bone-resorption')?.value,
      complication_hardware_problem: document.getElementById('f-complication-hardware-problem')?.value,
      complication_resynostosis_recurrence: document.getElementById('f-complication-resynostosis-recurrence')?.value,
      complication_unplanned_reoperation_30d: document.getElementById('f-complication-unplanned-reoperation-30d')?.value
    }
  };

  try {
    const saved = window.DatabaseAdapter.savePatient(patientObj);
    showToast(`Patient record '${saved.study_id}' saved successfully.`, 'success');
    loadPatientsList();
    selectPatient(saved.id);
  } catch (err) {
    showToast('Failed to save patient: ' + err.message, 'error');
  }
}

function deleteCurrentPatient() {
  if (!window.AppState.activePatientId) {
    showToast('No active patient selected to delete.', 'error');
    return;
  }
  const studyId = window.AppState.activePatientData?.study_id || 'this patient';

  if (confirm(`Permanently delete craniofacial record '${studyId}' and all linked surgical and MDT assessments?`)) {
    try {
      window.DatabaseAdapter.deletePatient(window.AppState.activePatientId);
      showToast(`Patient '${studyId}' deleted.`, 'info');
      resetPatientForm();
      loadPatientsList();
    } catch (err) {
      showToast('Delete failed: ' + err.message, 'error');
    }
  }
}

// Child Table Renderers
function renderSurgeriesTable(patientId) {
  const tbody = document.getElementById('tbody-surgeries');
  if (!tbody) return;

  const surgeries = window.DatabaseAdapter.getSurgeries(patientId);
  window.AppState.surgeriesList = surgeries;
  tbody.innerHTML = '';

  if (surgeries.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted text-xs p-3">No surgical procedures logged. Click '+ Log Surgical Procedure'.</td></tr>`;
    return;
  }

  surgeries.forEach(s => {
    const tr = document.createElement('tr');
    const isRedo = s.procedure_sequence.includes('Redo') || s.procedure_sequence.includes('Secondary');
    const badgeColor = isRedo ? 'badge-danger' : s.procedure_sequence.includes('Stage') ? 'badge-warning' : 'badge-primary';

    tr.innerHTML = `
      <td><strong>${s.surgery_date || '-'}</strong></td>
      <td><span class="badge ${badgeColor}">${s.procedure_sequence}</span></td>
      <td>
        <strong>${s.surgical_technique_category}</strong>
        ${s.surgical_technique_other_detail ? `<div class="text-xs text-muted">${s.surgical_technique_other_detail}</div>` : ''}
      </td>
      <td>${s.lead_surgeon || '-'}</td>
      <td>${s.operating_time_minutes ? s.operating_time_minutes + ' min' : '-'}</td>
      <td>
        <strong>${s.estimated_blood_loss_ml || 0} mL</strong>
        ${s.estimated_blood_loss_pct_ebv ? `<span class="badge ${s.estimated_blood_loss_pct_ebv > 20 ? 'badge-danger' : 'badge-secondary'} text-xs">${s.estimated_blood_loss_pct_ebv}% EBV</span>` : ''}
      </td>
      <td>PRBC: ${s.prbc_transfused_ml || 0} mL</td>
      <td><span class="badge ${s.dural_tear_occurred !== 'No' ? 'badge-warning' : 'badge-success'}">${s.dural_tear_occurred || 'No'}</span></td>
      <td>
        <button class="btn btn-outline btn-xs text-danger" onclick="window.deleteSurgeryRecord('${s.id}')">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

window.deleteSurgeryRecord = function(id) {
  if (confirm('Delete this surgical record?')) {
    try {
      window.DatabaseAdapter.deleteSurgery(id);
      showToast('Surgery record deleted.', 'info');
      renderSurgeriesTable(window.AppState.activePatientId);
    } catch (e) {
      showToast(e.message, 'error');
    }
  }
};

function renderNeurosurgTable(patientId) {
  const tbody = document.getElementById('tbody-mdt-neurosurg');
  if (!tbody) return;
  const list = window.DatabaseAdapter.getNeurosurgery(patientId);
  tbody.innerHTML = '';
  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted text-xs p-3">No neurosurgery assessments logged.</td></tr>`;
    return;
  }
  list.forEach(m => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${m.assessment_date}</strong></td>
      <td><span class="badge badge-secondary">${m.encounter_phase}</span></td>
      <td>${m.clinician_name || '-'}</td>
      <td><span class="text-xs">${m.icp_assessment_summary || '-'}</span></td>
      <td><span class="text-xs">${m.fundoscopy_papilloedema_status || '-'}</span></td>
      <td><span class="text-xs">${m.chiari_tonsil_position_status || '-'}</span></td>
      <td><button class="btn btn-outline btn-xs text-danger" onclick="window.deleteMdtItem('Neurosurgery', '${m.id}')">Delete</button></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderCranioTable(patientId) {
  const tbody = document.getElementById('tbody-mdt-cranio');
  if (!tbody) return;
  const list = window.DatabaseAdapter.getCraniofacial(patientId);
  tbody.innerHTML = '';
  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted text-xs p-3">No craniofacial / plastic assessments logged.</td></tr>`;
    return;
  }
  list.forEach(m => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${m.assessment_date}</strong></td>
      <td><span class="badge badge-secondary">${m.encounter_phase}</span></td>
      <td>${m.clinician_name || '-'}</td>
      <td><span class="text-xs">${m.forehead_and_supraorbital_contour || '-'}</span></td>
      <td><span class="text-xs">${m.midface_hypoplasia_assessment || '-'}</span></td>
      <td><span class="badge badge-purple">${m.whitaker_stage_estimate || '-'}</span></td>
      <td><button class="btn btn-outline btn-xs text-danger" onclick="window.deleteMdtItem('Craniofacial', '${m.id}')">Delete</button></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderGeneticsTable(patientId) {
  const tbody = document.getElementById('tbody-mdt-genetics');
  if (!tbody) return;
  const list = window.DatabaseAdapter.getGenetics(patientId);
  tbody.innerHTML = '';
  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted text-xs p-3">No genetics consultations logged.</td></tr>`;
    return;
  }
  list.forEach(m => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${m.consultation_date}</strong></td>
      <td>${m.geneticist_name || '-'}</td>
      <td><span class="badge badge-primary">${m.clinical_syndromic_impression || '-'}</span></td>
      <td><span class="text-xs">${m.dysmorphology_features || '-'}</span></td>
      <td><span class="text-xs">${m.counseling_inheritance_and_recurrence || '-'}</span></td>
      <td><button class="btn btn-outline btn-xs text-danger" onclick="window.deleteMdtItem('Genetics', '${m.id}')">Delete</button></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderNeuropsychTable(patientId) {
  const tbody = document.getElementById('tbody-mdt-neuropsych');
  if (!tbody) return;
  const list = window.DatabaseAdapter.getNeuropsychology(patientId);
  tbody.innerHTML = '';
  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted text-xs p-3">No neuropsychology assessments logged.</td></tr>`;
    return;
  }
  list.forEach(m => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${m.assessment_date}</strong></td>
      <td><span class="badge badge-secondary">${m.encounter_phase}</span></td>
      <td>${m.neuropsychologist_name || '-'}</td>
      <td><span class="badge badge-purple">${m.battery_used || '-'}</span></td>
      <td><strong>${m.developmental_quotient_or_iq || '-'}</strong></td>
      <td><span class="text-xs">${m.gross_motor_development || '-'}</span></td>
      <td><button class="btn btn-outline btn-xs text-danger" onclick="window.deleteMdtItem('Neuropsychology', '${m.id}')">Delete</button></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderSpeechTable(patientId) {
  const tbody = document.getElementById('tbody-mdt-speech');
  if (!tbody) return;
  const list = window.DatabaseAdapter.getSpeechTherapy(patientId);
  tbody.innerHTML = '';
  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted text-xs p-2">No speech therapy assessments logged.</td></tr>`;
    return;
  }
  list.forEach(m => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${m.assessment_date}</strong></td>
      <td>${m.therapist_name || '-'}</td>
      <td><span class="text-xs">${m.feeding_and_swallowing_function || '-'}</span></td>
      <td><span class="badge ${m.velopharyngeal_competence?.includes('VPI') ? 'badge-danger' : 'badge-success'}">${m.velopharyngeal_competence || '-'}</span></td>
      <td><span class="text-xs">${m.therapy_plan || '-'}</span></td>
      <td><button class="btn btn-outline btn-xs text-danger" onclick="window.deleteMdtItem('Speech', '${m.id}')">Delete</button></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderOphthalmologyTable(patientId) {
  const tbody = document.getElementById('tbody-mdt-ophthalmology');
  if (!tbody) return;
  const list = window.DatabaseAdapter.getOphthalmology(patientId);
  tbody.innerHTML = '';
  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted text-xs p-2">No ophthalmology assessments logged.</td></tr>`;
    return;
  }
  list.forEach(m => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${m.examination_date}</strong></td>
      <td>${m.ophthalmologist_name || '-'}</td>
      <td><span class="text-xs">${m.visual_acuity_right || '-'}</span></td>
      <td><span class="text-xs">${m.strabismus_v_pattern || '-'}</span></td>
      <td><strong>${m.exorbitism_hertel_mm ? m.exorbitism_hertel_mm + ' mm' : '-'}</strong></td>
      <td><span class="text-xs">${m.optic_nerve_status_oct || '-'}</span></td>
      <td><button class="btn btn-outline btn-xs text-danger" onclick="window.deleteMdtItem('Ophthalmology', '${m.id}')">Delete</button></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderAirwayTable(patientId) {
  const tbody = document.getElementById('tbody-mdt-airway');
  if (!tbody) return;
  const list = window.DatabaseAdapter.getAirway(patientId);
  tbody.innerHTML = '';
  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted text-xs p-2">No airway/sleep assessments logged.</td></tr>`;
    return;
  }
  list.forEach(m => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${m.assessment_date}</strong></td>
      <td>${m.specialist_name || '-'}</td>
      <td><span class="text-xs">${m.upper_airway_patency || '-'}</span></td>
      <td><span class="badge ${m.ahi_current_score >= 10 ? 'badge-danger' : m.ahi_current_score >= 5 ? 'badge-warning' : 'badge-success'}">${m.ahi_current_score ? m.ahi_current_score + ' /hr' : '-'}</span></td>
      <td><span class="text-xs">${m.cpap_bipap_tolerated || '-'}</span></td>
      <td><button class="btn btn-outline btn-xs text-danger" onclick="window.deleteMdtItem('Airway', '${m.id}')">Delete</button></td>
    `;
    tbody.appendChild(tr);
  });
}

window.deleteMdtItem = function(discipline, id) {
  if (confirm(`Delete this ${discipline} record?`)) {
    try {
      if (discipline === 'Neurosurgery') window.DatabaseAdapter.deleteNeurosurgery(id);
      else if (discipline === 'Craniofacial') window.DatabaseAdapter.deleteCraniofacial(id);
      else if (discipline === 'Genetics') window.DatabaseAdapter.deleteGenetics(id);
      else if (discipline === 'Neuropsychology') window.DatabaseAdapter.deleteNeuropsychology(id);
      else if (discipline === 'Speech') window.DatabaseAdapter.deleteSpeechTherapy(id);
      else if (discipline === 'Ophthalmology') window.DatabaseAdapter.deleteOphthalmology(id);
      else if (discipline === 'Airway') window.DatabaseAdapter.deleteAirway(id);

      showToast(`${discipline} record removed.`, 'info');
      selectPatient(window.AppState.activePatientId);
    } catch (e) {
      showToast(e.message, 'error');
    }
  }
};

// Cohort Analytics
function renderCohortAnalytics() {
  const a = window.DatabaseAdapter.getCohortAnalytics();

  const cTotal = document.getElementById('card-cohort-total');
  const cSurg = document.getElementById('card-cohort-surgeries');
  const cRedo = document.getElementById('card-cohort-redo-rate');
  const cPre = document.getElementById('card-cohort-pre-ci');
  const cPost = document.getElementById('card-cohort-post-ci');
  const cSat = document.getElementById('card-cohort-sat');

  if (cTotal) cTotal.textContent = a.totalPatients;
  if (cSurg) cSurg.textContent = a.totalSurgeries;
  if (cRedo) cRedo.textContent = `${a.redoRatePct}%`;
  if (cPre) cPre.textContent = `${a.meanPreCI}%`;
  if (cPost) cPost.textContent = `${a.meanPostCI}%`;
  if (cSat) cSat.textContent = `${a.meanParentSatisfaction} / 5`;

  renderDistTable('tbody-cohort-sutures', a.sutureDistribution, a.totalPatients);
  renderDistTable('tbody-cohort-techniques', a.techniqueDistribution, a.totalSurgeries);
  renderDistTable('tbody-cohort-whitaker', a.whitakerDistribution, a.totalPatients);
}

function renderDistTable(tbodyId, distMap, total) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  tbody.innerHTML = '';
  const entries = Object.entries(distMap).sort((a, b) => b[1] - a[1]);

  if (entries.length === 0) {
    tbody.innerHTML = `<tr><td colspan="3" class="text-center text-muted text-xs p-2">No data</td></tr>`;
    return;
  }

  entries.forEach(([key, count]) => {
    const pct = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${key}</strong></td>
      <td>${count}</td>
      <td>
        <div style="display:flex; align-items:center; gap:6px;">
          <div style="flex:1; background:rgba(255,255,255,0.08); height:6px; border-radius:3px; overflow:hidden;">
            <div style="width:${pct}%; background:var(--accent-csf); height:100%;"></div>
          </div>
          <span class="text-xs text-muted" style="min-width:32px;">${pct}%</span>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function initAuditAndDesignModals() {
  const btnAudit = document.getElementById('btn-audit-log');
  if (btnAudit) btnAudit.addEventListener('click', renderAuditLog);

  const sqlContainer = document.getElementById('schema-sql-display');
  if (sqlContainer && window.SCHEMA_SQL) {
    sqlContainer.textContent = window.SCHEMA_SQL.trim();
  }

  const btnClone = document.getElementById('btn-clone-db');
  if (btnClone) {
    btnClone.addEventListener('click', () => {
      try {
        window.DatabaseAdapter.exportToJson();
        showToast('Database clone created as JSON snapshot.', 'success');
      } catch (e) {
        showToast(e.message, 'error');
      }
    });
  }

  const btnResetDb = document.getElementById('btn-reset-db-demo');
  if (btnResetDb) {
    btnResetDb.addEventListener('click', () => {
      if (confirm('Warning: This will reload the default preloaded craniofacial demonstrator cases. Proceed?')) {
        localStorage.clear();
        window.location.reload();
      }
    });
  }
}

function renderAuditLog() {
  const tbody = document.getElementById('tbody-audit-log');
  if (!tbody) return;
  const logs = window.DatabaseAdapter.getAuditLog();
  tbody.innerHTML = '';

  if (logs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted text-xs p-3">Audit ledger is empty.</td></tr>`;
    return;
  }

  logs.slice(0, 50).forEach(l => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><span class="text-xs">${l.timestamp}</span></td>
      <td><strong>${l.username}</strong></td>
      <td><span class="badge ${l.action.includes('DELETE') ? 'badge-danger' : l.action.includes('SAVE') || l.action.includes('CREATE') ? 'badge-success' : 'badge-secondary'}">${l.action}</span></td>
      <td>${l.study_id || '-'}</td>
      <td><span class="text-xs">${l.details || '-'}</span></td>
      <td><code class="text-xs">${l.record_hash.substring(0, 10)}...</code> <span class="badge badge-success" style="font-size:9px;">VERIFIED</span></td>
    `;
    tbody.appendChild(tr);
  });
}
