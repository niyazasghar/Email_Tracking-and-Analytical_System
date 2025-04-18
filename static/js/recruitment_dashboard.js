// static/js/recruitment_dashboard.js

document.addEventListener("DOMContentLoaded", () => {
  // Retrieve the JWT token. If missing, redirect to login.
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "/";
    return;
  }

  // -------------------------------
  // Logout Button Logic
  // -------------------------------
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      // Remove the token and redirect to login
      localStorage.removeItem("access_token");
      window.location.href = "/";
    });
  }

  // -------------------------------
  // Section 1: Get Upcoming Recruitments by Year
  // -------------------------------
  const upcomingForm = document.getElementById("upcomingForm");
  const upcomingMessage = document.getElementById("upcomingMessage");
  const upcomingTableBody = document.querySelector("#upcomingTable tbody");

  upcomingForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!upcomingForm.checkValidity()) return;

    const year = document.getElementById("upcomingYear").value;
    try {
      const res = await fetch(`/recruitment/upcoming?year=${year}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to fetch upcoming companies");
      }

      const data = await res.json();
      upcomingMessage.innerHTML = `<div class="alert alert-success">Found ${data.length} companies for year ${year}.</div>`;

      // Clear previous table rows
      upcomingTableBody.innerHTML = "";
      if (data.length === 0) {
        upcomingTableBody.innerHTML = `<tr><td colspan="11" class="text-center text-secondary">No data</td></tr>`;
      } else {
        // For each company record, display the required fields.
        data.forEach((company) => {
          const companyName = company.company_name || "--";
          const eligibility = company.eligibility_criteria || "--";
          const selectionProcess = company.selection_process || "--";
          const packageOffered = company.package_offered || "--";
          const roleOffered = company.role_offered || "--";
          const recruitmentMode = company.recruitment_mode || "--";
          const jobType = company.job_type || "--";
          const location = company.location || "--";
          const workEnvironment = company.work_environment || "--";
          // joining_date and event_date—if provided—are converted to local strings.
          const joiningDate = company.joining_date ? new Date(company.joining_date).toLocaleDateString() : "--";
          // Note: Since RecruitmentEvent is not directly part of Company, you must have joined or included event_date in your schema.
          // If it's included, then for example:
          const eventDate = company.event_date ? new Date(company.event_date).toLocaleString() : "--";

          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${companyName}</td>
            <td>${eligibility}</td>
            <td>${selectionProcess}</td>
            <td>${packageOffered}</td>
            <td>${roleOffered}</td>
            <td>${recruitmentMode}</td>
            <td>${jobType}</td>
            <td>${location}</td>
            <td>${workEnvironment}</td>
            <td>${joiningDate}</td>
            <td>${eventDate}</td>
          `;
          upcomingTableBody.appendChild(row);
        });
      }
    } catch (error) {
      upcomingMessage.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
  });

  // -------------------------------
  // Section 2: Add Company (Superuser Only)
  // -------------------------------
  const addCompanyForm = document.getElementById("addCompanyForm");
  const companyMessage = document.getElementById("companyMessage");

  addCompanyForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!addCompanyForm.checkValidity()) return;

    const formData = {
      company_name: document.getElementById("companyName").value,
      domain: document.getElementById("domain").value,
      recruitment_year: parseInt(document.getElementById("recruitmentYear").value, 10),
      eligibility_criteria: document.getElementById("eligibility").value,
      selection_process: document.getElementById("selectionProcess").value,
      package_offered: document.getElementById("packageOffered").value,
      role_offered: document.getElementById("roleOffered").value,
      joining_date: document.getElementById("joiningDate").value || null,
      job_type: document.getElementById("jobType").value,
      location: document.getElementById("location").value,
      work_environment: document.getElementById("workEnvironment").value,
      recruitment_mode: document.getElementById("recruitmentMode").value
    };

    try {
      const res = await fetch("/recruitment/company", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to add company");
      }
      const data = await res.json();
      companyMessage.innerHTML = `<div class="alert alert-success">Company added successfully! ID: ${data.company_id}</div>`;

      addCompanyForm.reset();
      addCompanyForm.classList.remove("was-validated");
    } catch (error) {
      companyMessage.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
  });

  // -------------------------------
  // Section 3: Add Event (Accessible to any logged-in user)
  // -------------------------------
  const addEventForm = document.getElementById("addEventForm");
  const eventMessage = document.getElementById("eventMessage");

  addEventForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!addEventForm.checkValidity()) return;

    const eventData = {
      company_id: parseInt(document.getElementById("eventCompanyId").value, 10),
      event_date: document.getElementById("eventDate").value // Format e.g., "2025-06-15T10:00"
    };

    try {
      const res = await fetch("/recruitment/event", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(eventData)
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to add event");
      }
      const data = await res.json();
      eventMessage.innerHTML = `<div class="alert alert-success">Event added! ID: ${data.event_id}, Date: ${data.event_date}</div>`;

      addEventForm.reset();
      addEventForm.classList.remove("was-validated");
    } catch (error) {
      eventMessage.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
  });
});
