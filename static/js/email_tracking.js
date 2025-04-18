document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "/";
    return;
  }

  // 1) Fetch current user’s email for bubble positioning
  let myEmail = null;
  async function getMyEmail() {
    try {
      const res = await fetch("/auth/me", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error();
      return (await res.json()).email;
    } catch {
      return null;
    }
  }

  // 2) Logout
  document.getElementById("logoutBtn")
    .addEventListener("click", () => {
      localStorage.removeItem("access_token");
      window.location.href = "/";
    });

  // 3) Send Email Form (unchanged)
  const emailForm = document.getElementById("emailForm");
  const messageDiv = document.getElementById("message");
  emailForm.addEventListener("submit", async e => {
    e.preventDefault();
    if (!emailForm.checkValidity()) {
      emailForm.classList.add("was-validated");
      return;
    }
    const sender    = document.getElementById("sender").value;
    const recipient = document.getElementById("recipient").value;
    const subject   = document.getElementById("subject").value;
    const body      = document.getElementById("body").value;

    try {
      const res = await fetch("/email-tracking/send", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ sender, recipient, subject, body })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || JSON.stringify(err));
      }
      const data = await res.json();
      messageDiv.innerHTML = `
        <div class="alert alert-success">
          Email sent!<br>
          Message ID: ${data.message_id}<br>
          Subject: ${data.subject}
        </div>
      `;
      emailForm.reset();
      emailForm.classList.remove("was-validated");
    } catch (err) {
      messageDiv.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
    }
  });

  // 4) Chat Interface
  const companySelect = document.getElementById("companySelect");
  const startDate     = document.getElementById("startDate");
  const endDate       = document.getElementById("endDate");
  const loadChatBtn   = document.getElementById("loadChatBtn");
  const chatContainer = document.getElementById("chatContainer");

  // 4a) Populate companies dropdown
  async function loadCompanies() {
    try {
      const res = await fetch("/email-tracking/companies", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to load companies");
      const companies = await res.json();
      companySelect.innerHTML =
        '<option value="" disabled selected>Select a company</option>';
      companies.forEach(c => {
        const opt = document.createElement("option");
        opt.value = c.company_id;
        opt.textContent = c.company_name;
        companySelect.appendChild(opt);
      });
    } catch (err) {
      console.error(err);
      companySelect.innerHTML = `<option disabled>Error loading</option>`;
    }
  }

  // 4b) Fetch + render chat bubbles
  loadChatBtn.addEventListener("click", async () => {
    chatContainer.innerHTML = "";
    const companyId = companySelect.value;
    if (!companyId) {
      chatContainer.innerHTML =
        `<p class="text-center text-danger">Please select a company.</p>`;
      return;
    }

    let qs = `?company_id=${companyId}`;
    if (startDate.value) qs += `&start_date=${startDate.value}T00:00:00`;
    if (endDate.value)   qs += `&end_date=${endDate.value}T23:59:59`;

    try {
      const res = await fetch(`/email-tracking/chat${qs}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to load chat");
      }
      const emails = await res.json();
      if (!emails.length) {
        chatContainer.innerHTML =
          `<p class="text-center text-secondary">No messages found.</p>`;
        return;
      }

      emails.forEach(email => {
        const bubble = document.createElement("div");
        bubble.classList.add("message-bubble");
        const isSent = myEmail &&
          email.sender.toLowerCase() === myEmail.toLowerCase();
        bubble.classList.add(isSent ? "sent" : "received");

        const ts = new Date(email.sent_timestamp).toLocaleString();
        bubble.innerHTML = `
          <strong>${email.subject}</strong><br>
          <span>${email.body}</span>
          <div class="timestamp">${ts}</div>
        `;
        chatContainer.appendChild(bubble);
      });

      chatContainer.scrollTop = chatContainer.scrollHeight;
    } catch (err) {
      console.error(err);
      chatContainer.innerHTML =
        `<p class="text-center text-danger">${err.message}</p>`;
    }
  });

  // 5) Initialize
  (async () => {
    myEmail = await getMyEmail();
    await loadCompanies();
  })();
});
