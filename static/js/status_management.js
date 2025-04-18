document.addEventListener("DOMContentLoaded", () => {
  // 1) Check if logged in as superuser
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "/";
    return;
  }

  // ----------------------------------------------------------------
  // Populate Company Dropdowns (for both "Manual Status Update" and "Company Status Overview")
  // ----------------------------------------------------------------
  const companyDropdown = document.getElementById("companyDropdown");
  const companyStatusDropdown = document.getElementById("companyStatusDropdown");

  async function loadCompanies() {
    try {
      const res = await fetch("/status/companies", {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (!res.ok) {
        throw new Error("Failed to load companies");
      }
      const companies = await res.json();
      // Populate both dropdowns
      companies.forEach((company) => {
        const { company_id, company_name } = company;

        // For manual status update
        const option1 = document.createElement("option");
        option1.value = company_id;
        option1.textContent = `${company_name} (ID: ${company_id})`;
        companyDropdown.appendChild(option1);

        // For company status overview
        const option2 = document.createElement("option");
        option2.value = company_id;
        option2.textContent = `${company_name} (ID: ${company_id})`;
        companyStatusDropdown.appendChild(option2);
      });
    } catch (error) {
      console.error(error);
      alert("Error loading companies: " + error.message);
    }
  }

  loadCompanies();

  // ----------------------------------------------------------------
  // When a company is selected in the "Manual Status Update" form,
  // load that company's Emails (ID, subject, current status).
  // ----------------------------------------------------------------
  const emailDropdown = document.getElementById("emailDropdown");

  companyDropdown.addEventListener("change", async (e) => {
    const companyId = e.target.value;
    emailDropdown.innerHTML =
      '<option value="" disabled selected>Select an Email...</option>';

    if (!companyId) return;

    try {
      const url = `/status/company/${companyId}/emails`;
      const res = await fetch(url, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (!res.ok) {
        throw new Error("Failed to fetch emails for this company");
      }
      const emails = await res.json();

      emails.forEach((emailItem) => {
        const { email_id, subject, status } = emailItem;
        const option = document.createElement("option");
        option.value = email_id;
        option.textContent = `#${email_id} | ${subject} [${status}]`;
        emailDropdown.appendChild(option);
      });
    } catch (error) {
      alert(error.message);
    }
  });

  // ------------------------------
  // Manual Status Update Handler
  // ------------------------------
  const statusUpdateForm = document.getElementById("statusUpdateForm");
  const updateMessage = document.getElementById("updateMessage");

  statusUpdateForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!statusUpdateForm.checkValidity()) {
      return;
    }

    const selectedEmailId = emailDropdown.value;
    if (!selectedEmailId) {
      updateMessage.innerHTML = `<div class="alert alert-danger">Please select an email.</div>`;
      return;
    }

    const newStatus = document.getElementById("newStatusInput").value.trim();

    try {
      // Construct the PUT URL
      let url = `/status/update/${selectedEmailId}`;
      if (newStatus) {
        url += `?new_status=${encodeURIComponent(newStatus)}`;
      }

      const res = await fetch(url, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to update status");
      }

      const data = await res.json();
      updateMessage.innerHTML = `
        <div class="alert alert-success">
          Status updated to: <strong>${data.status}</strong> for Email ID: <strong>${data.email_id}</strong>
        </div>`;

      // Clear the newStatusInput, but don't reset the entire form
      document.getElementById("newStatusInput").value = "";
      // Optionally, remove 'was-validated' if you want to allow multiple updates
      statusUpdateForm.classList.remove("was-validated");
    } catch (error) {
      updateMessage.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
  });

  // ------------------------------
  // Company Status Overview
  // ------------------------------
  const companyStatusForm = document.getElementById("companyStatusForm");
  const pendingCount = document.getElementById("pendingCount");
  const followUpCount = document.getElementById("followUpCount");

  companyStatusForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!companyStatusForm.checkValidity()) {
      return;
    }

    const selectedCompanyId = companyStatusDropdown.value;
    if (!selectedCompanyId) {
      alert("Please select a company.");
      return;
    }

    // Retrieve user dates (YYYY-MM-DD)
    const startDate = document.getElementById("startDateInput").value;
    const endDate = document.getElementById("endDateInput").value;

    // Build query so that it EXACTLY matches what your backend expects
    // e.g. "YYYY-MM-DDT00:00:00"
    let qs = "";
    if (startDate) qs += `&start_date=${startDate}T00:00:00`;
    if (endDate) qs += `&end_date=${endDate}T23:59:59`;

    try {
      const url = `/status/company/${selectedCompanyId}/status?${qs}`;
      const res = await fetch(url, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to fetch company status");
      }

      const data = await res.json();
      // e.g. { company_id: 4, pending_emails: 3, follow_up_emails: 1 }
      pendingCount.textContent = data.pending_emails ?? "--";
      followUpCount.textContent = data.follow_up_emails ?? "--";
    } catch (error) {
      alert(error.message);
    }
  });
});
