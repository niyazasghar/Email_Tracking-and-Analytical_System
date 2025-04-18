// static/js/automatic_followup.js

document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "/";
    return;
  }

  const runFollowUpButton = document.getElementById("runFollowUp");
  const followUpMessage = document.getElementById("followUpMessage");

  runFollowUpButton.addEventListener("click", async () => {
    try {
      const res = await fetch("/followups/run", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to run follow-ups");
      }
      const data = await res.json();
      // data is an array of updated emails, e.g. [ {...}, {...} ]
      followUpMessage.innerHTML = `
        <div class="alert alert-success">
          Automatic follow-up process completed. Updated ${data.length} emails.
        </div>`;
    } catch (error) {
      followUpMessage.innerHTML = `
        <div class="alert alert-danger">
          ${error.message}
        </div>`;
    }
  });
});
