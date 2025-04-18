/*  MANAGEMENT‑DASHBOARD  (company‑name dropdown for “Add Placed Student”)
    ====================================================================== */
document.addEventListener('DOMContentLoaded', () => {
  /* ------------------------------------------------------------ 0. AUTH */
  const token = localStorage.getItem('access_token');
  if (!token) { location.href = '/'; return; }

  /* ------------------------------------------------------------ 1. NAV */
  document.getElementById('backToMainBtn')
          .addEventListener('click', () => location.href = '/superuser-dashboard');
  document.getElementById('logoutBtn')
          .addEventListener('click', () => { localStorage.removeItem('access_token'); location.href = '/'; });

  /* ------------------------------------------------------------ 2. DATA */
  /**  Map company_name ➜ company_id (for later lookup)  */
  const nameToId = new Map();

  async function loadCompanies () {
    try {
      const res = await fetch('/analytics/companies', {
        headers: { Authorization:`Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to load companies');
      /** @type {{id:number, name:string}[]} */
      const companies = await res.json();

      const eventSel   = document.getElementById('companyDropdownEvent');
      const placedSel  = document.getElementById('placedCompanyDropdown');

      eventSel.length  = 1;   // keep <option disabled selected …>
      placedSel.length = 1;

      nameToId.clear();

      companies.forEach(c => {
        // ➊ Add to Select‑Event dropdown: id as value (unchanged)
        eventSel.add(new Option(c.name, c.id));

        // ➋ Add to Placed‑Student dropdown: name as value
        placedSel.add(new Option(c.name, c.name));

        // ➌ Remember mapping
        nameToId.set(c.name, c.id);
      });
    } catch (err) {
      console.error(err);
      alert('Error loading company list: '+ err.message);
    }
  }
  loadCompanies();

  /* ------------------------------------------------------- 3. ADD COMPANY */
  document.getElementById('addCompanyForm')
          .addEventListener('submit', async e => {
    e.preventDefault();
    const f = e.target;
    if (!f.checkValidity()) { f.classList.add('was-validated'); return; }

    const payload = {
      company_name        : f.companyName.value,
      domain              : f.domain.value,
      recruitment_year    : +f.recruitmentYear.value,
      eligibility_criteria: f.eligibility.value,
      selection_process   : f.selectionProcess.value,
      package_offered     : f.packageOffered.value,
      role_offered        : f.roleOffered.value,
      joining_date        : f.joiningDate.value || null,
      job_type            : f.jobType.value,
      location            : f.location.value,
      work_environment    : f.workEnvironment.value,
      recruitment_mode    : f.recruitmentMode.value
    };

    try {
      const r = await fetch('/recruitment/company', {
        method : 'POST',
        headers: { 'Content-Type':'application/json', Authorization:`Bearer ${token}` },
        body   : JSON.stringify(payload)
      });
      if (!r.ok) throw new Error((await r.json()).detail);
      const data = await r.json();
      showMsg('companyMessage', `✅ Company added (ID ${data.company_id})`, 'success');
      f.reset(); f.classList.remove('was-validated');
      loadCompanies();                      // refresh dropdowns & map
    } catch (err) { showMsg('companyMessage', err.message, 'danger'); }
  });

  /* --------------------------------------------------------- 4. ADD EVENT */
  document.getElementById('addEventForm')
          .addEventListener('submit', async e => {
    e.preventDefault();
    const f = e.target;
    if (!f.checkValidity()) { f.classList.add('was-validated'); return; }

    const payload = {
      company_id: +f.companyDropdownEvent.value,
      event_date: f.eventDate.value
    };

    try {
      const r = await fetch('/recruitment/event', {
        method :'POST',
        headers: { 'Content-Type':'application/json', Authorization:`Bearer ${token}` },
        body   : JSON.stringify(payload)
      });
      if (!r.ok) throw new Error((await r.json()).detail);
      const data = await r.json();
      showMsg('eventMessage', `✅ Event added (ID ${data.event_id})`, 'success');
      f.reset(); f.classList.remove('was-validated');
    } catch (err) { showMsg('eventMessage', err.message, 'danger'); }
  });

  /* ---------------------------------------------- 5. ADD PLACED STUDENT  */
  document.getElementById('addPlacedForm')
          .addEventListener('submit', async e => {
    e.preventDefault();
    const f = e.target;
    if (!f.checkValidity()) { f.classList.add('was-validated'); return; }

    const chosenName = f.placedCompanyDropdown.value;
    const company_id = nameToId.get(chosenName);

    if (company_id === undefined) {
      showMsg('placedStudentMessage', 'Unknown company – refresh the page.', 'danger');
      return;
    }

    const payload = {
      student_name   : f.studentName.value,
      student_roll   : f.studentRoll.value,
      company_id,                       // backend ID
      company_name   : chosenName,      // optional – in case server wants it
      role_offered   : f.placedRoleOffered.value,
      joining_date   : f.joiningDatePlaced.value || null,
      package_offered: f.packagePlaced.value,
      placement_year : +f.placementYearPlaced.value
    };

    try {
      const r = await fetch('/recruitment/add-student', {
        method :'POST',
        headers: { 'Content-Type':'application/json', Authorization:`Bearer ${token}` },
        body   : JSON.stringify(payload)
      });
      if (!r.ok) throw new Error((await r.json()).detail);
      const data = await r.json();
      showMsg('placedStudentMessage', `✅ Student placed (ID ${data.placement_id})`, 'success');
      f.reset(); f.classList.remove('was-validated');
    } catch (err) { showMsg('placedStudentMessage', err.message, 'danger'); }
  });

  /* ------------------------------------------------------------- UTIL */
  function showMsg (holderId, text, type='info') {
    document.getElementById(holderId).innerHTML =
      `<div class="alert alert-${type}" role="alert">${text}</div>`;
  }
});
