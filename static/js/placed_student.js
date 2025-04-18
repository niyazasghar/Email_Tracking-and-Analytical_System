document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "/";
    return;
  }

  // Elements
  const companySelect   = document.getElementById("companySelect");
  const placementYear   = document.getElementById("placementYear");
  const roleOffered     = document.getElementById("roleOffered");
  const placedForm      = document.getElementById("placedFilterForm");
  const placedTableBody = document.querySelector("#placedTable tbody");
  const placedMessage   = document.getElementById("placedMessage");

  // 1) Load companies into dropdown
  async function loadCompanies() {
    try {
      const res = await fetch("/recruitment/companies", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Could not fetch companies");
      const list = await res.json();  // [{company_id, company_name}, …]
      companySelect.innerHTML = `<option value="">All Companies</option>`;
      list.forEach(c => {
        const opt = new Option(c.company_name, c.company_id);
        companySelect.appendChild(opt);
      });
    } catch (err) {
      console.error(err);
      companySelect.innerHTML = `<option disabled>Error loading</option>`;
    }
  }

  // 2) Query placed students on form submit
  placedForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!placedForm.checkValidity()) {
      placedForm.classList.add("was-validated");
      return;
    }

    let qs = "?";
    if (companySelect.value) qs += `company_id=${companySelect.value}&`;
    if (placementYear.value) qs += `year=${placementYear.value}&`;
    if (roleOffered.value)   qs += `role=${encodeURIComponent(roleOffered.value)}&`;

    try {
      const res = await fetch(`/placement/students${qs}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || JSON.stringify(err));
      }
      const data = await res.json();
      placedTableBody.innerHTML = "";

      if (!data.length) {
        placedTableBody.innerHTML = `
          <tr><td colspan="8" class="text-center text-secondary">
            No results found
          </td></tr>`;
        return;
      }

      data.forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${item.placement_id}</td>
          <td>${item.student_name||"--"}</td>
          <td>${item.student_roll||"--"}</td>
          <td>${item.company_name||"--"}</td>
          <td>${item.role_offered||"--"}</td>
          <td>${item.joining_date||"--"}</td>
          <td>${item.package_offered||"--"}</td>
          <td>${item.placement_year||"--"}</td>
        `;
        placedTableBody.appendChild(tr);
      });
    } catch (error) {
      placedMessage.innerHTML = `
        <div class="alert alert-danger">${error.message}</div>`;
    }
  });

  // Initialize
  loadCompanies();
});
