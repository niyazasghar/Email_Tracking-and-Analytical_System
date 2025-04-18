document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "/";
    return;
  }

  // Element references for email analytics
  const companySelect = document.getElementById("companySelect");
  const applyFiltersBtn = document.getElementById("applyFilters");
  const totalEmailsEl = document.getElementById("total-emails");
  const repliedEmailsEl = document.getElementById("replied-emails");
  const pendingEmailsEl = document.getElementById("pending-emails");
  const conversionRateEl = document.getElementById("conversion-rate");

  // Element references for placement analytics
  const placementYearInput = document.getElementById("placementYear");
  const placementCompanySelect = document.getElementById("placementCompanySelect");
  const placementQueryBtn = document.getElementById("placementQueryBtn");
  const placementResult = document.getElementById("placementResult");

  // Chart variables for email analytics
  let statusChart, companyConversionChart, hourlyChart;

  // --- Function to populate companies dropdown for email analytics ---
  async function populateCompaniesDropdown() {
    try {
      const res = await fetch("/analytics/companies", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to load companies");
      const companies = await res.json();
      // Clear and add default option
      companySelect.innerHTML = '<option value="0" selected>System Wide (All Companies)</option>';
      // Also populate placement dropdown with same companies
      placementCompanySelect.innerHTML = '<option value="0" selected>All Companies</option>';
      companies.forEach(c => {
        const optEmail = document.createElement("option");
        optEmail.value = c.id;
        optEmail.textContent = c.name;
        companySelect.appendChild(optEmail);

        const optPlacement = document.createElement("option");
        optPlacement.value = c.id;
        optPlacement.textContent = c.name;
        placementCompanySelect.appendChild(optPlacement);
      });
    } catch (error) {
      console.error("Error populating companies dropdown:", error);
    }
  }
  populateCompaniesDropdown();

  // --- Execute Email Analytics Query ---
  applyFiltersBtn.addEventListener("click", async () => {
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;
    const selectedCompany = companySelect.value;
    // Build query string; backend expects ISO formatted dates.
    let qs = `?company_id=${selectedCompany}`;
    if (startDate) qs += `&start_date=${startDate}T00:00:00`;
    if (endDate) qs += `&end_date=${endDate}T23:59:59`;

    try {
      const res = await fetch("/analytics/overview" + qs, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to fetch analytics data");
      const data = await res.json();

      // Update summary numbers
      totalEmailsEl.textContent = data.overall.total_emails;
      repliedEmailsEl.textContent = data.overall.replied_emails;
      pendingEmailsEl.textContent = data.overall.pending_emails;
      conversionRateEl.textContent = data.overall.conversion_rate + "%";

      // Update charts and table
      updateStatusChart(data.charts.status_distribution);
      updateCompanyConversionChart(data.companies);
      updateHourlyChart(data.charts.hourly_distribution);
      updateCompanyTable(data.companies);
    } catch (error) {
      console.error("Error fetching analytics data:", error);
      alert("Error: " + error.message);
    }
  });

  // --- Placement Analytics Query ---
  placementQueryBtn.addEventListener("click", async () => {
    const year = placementYearInput.value;
    const selectedPlacementCompany = placementCompanySelect.value;
    if (!year) {
      alert("Please specify a placement year.");
      return;
    }
    const qs = `?year=${year}&company_id=${selectedPlacementCompany}`;
    try {
      const res = await fetch("/analytics/placements" + qs, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to fetch placement analytics");
      const data = await res.json();
      let resultHtml = "";
      if (selectedPlacementCompany == 0) {
        resultHtml += `<p>Placement Year: ${data.year}</p>`;
        resultHtml += `<table class="table table-striped"><thead><tr><th>Company ID</th><th>Company Name</th><th>Placed Students</th></tr></thead><tbody>`;
        data.placements.forEach(item => {
          resultHtml += `<tr>
            <td>${item.company_id}</td>
            <td>${item.company_name}</td>
            <td>${item.placements_count}</td>
          </tr>`;
        });
        resultHtml += `</tbody></table>`;
      } else {
        resultHtml += `<p>Placement Year: ${data.year}</p>`;
        resultHtml += `<p>Company: ${data.company_name} (ID: ${data.company_id})</p>`;
        resultHtml += `<p>Placed Students: ${data.placements_count}</p>`;
      }
      placementResult.innerHTML = resultHtml;
    } catch (error) {
      console.error("Error loading placement analytics:", error);
      placementResult.innerHTML = `<p class="text-danger">Error: ${error.message}</p>`;
    }
  });

  // --- Chart Updating Functions ---

  function updateStatusChart(dist) {
    const colorMap = {
      "Replied": "#4caf50",
      "Pending": "#ffc107",
      "Follow-up Required": "#f44336",
      "Sent": "#2196f3",
      "Received": "#c196f5"
    };
    const backgroundColors = dist.labels.map(label => colorMap[label] || "#9e9e9e");
    const ctx = document.getElementById("statusChart").getContext("2d");
    if (statusChart) statusChart.destroy();
    statusChart = new Chart(ctx, {
      type: "pie",
      data: {
        labels: dist.labels,
        datasets: [{
          data: dist.data,
          backgroundColor: backgroundColors,
          borderColor: "#222222",
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top", labels: { color: "#e0e0e0", font: { size: 14 } } }
        }
      }
    });
  }

  function updateCompanyConversionChart(companies) {
    const ctx = document.getElementById("companyConversionChart").getContext("2d");
    if (companyConversionChart) companyConversionChart.destroy();
    const labels = companies.map(c => c.company_name);
    const data = companies.map(c => c.conversion_rate);
    companyConversionChart = new Chart(ctx, {
      type: "bar",
      data: { labels, datasets: [{ label: "Conversion Rate (%)", data, backgroundColor: "#8a2be2" }] },
      options: { scales: { y: { beginAtZero: true, max: 100 } }, responsive: true, maintainAspectRatio: false }
    });
  }

  function updateHourlyChart(hourDist) {
    const ctx = document.getElementById("hourlyChart").getContext("2d");
    if (hourlyChart) hourlyChart.destroy();
    hourlyChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: hourDist.labels,
        datasets: [{
          label: "Replies per Hour",
          data: hourDist.data,
          borderColor: "#00dffc",
          backgroundColor: "rgba(0, 223, 252, 0.25)",
          fill: true,
          tension: 0.3
        }]
      },
      options: {
        scales: { x: { title: { display: true, text: "Hour of Day" } }, y: { beginAtZero: true } },
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }

  function updateCompanyTable(companies) {
    const tableBody = document.querySelector("#companyTable tbody");
    tableBody.innerHTML = "";
    if (!companies || companies.length === 0) {
      const row = document.createElement("tr");
      row.innerHTML = `<td colspan="4" class="text-center text-secondary">No data found</td>`;
      tableBody.appendChild(row);
      return;
    }
    companies.forEach(comp => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${comp.company_id}</td>
        <td>${comp.sent}</td>
        <td>${comp.replied}</td>
        <td>${comp.conversion_rate}</td>
      `;
      tableBody.appendChild(row);
    });
  }
});
