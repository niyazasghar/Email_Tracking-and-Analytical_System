// static/js/superuser_dashboard.js

document.addEventListener("DOMContentLoaded", async () => {
  // Retrieve the token from localStorage.
  const token = localStorage.getItem("access_token");
  if (!token) {
    // No token means user is not logged in – redirect to login.
    window.location.href = "/";
    return;
  }

  // Verify the user is a superuser using the /auth/me endpoint.
  try {
    const meRes = await fetch("/auth/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!meRes.ok) throw new Error("Not authorized");
    const meData = await meRes.json();
    if (!meData.is_superuser) {
      // If the user is not a superuser, redirect to the student dashboard.
      window.location.href = "/student-dashboard";
      return;
    }
  } catch (error) {
    console.error("Error verifying user:", error);
    window.location.href = "/";
    return;
  }

  // Attach logout functionality to the logout button.
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      // Remove the token from localStorage.
      localStorage.removeItem("access_token");
      // Optionally, you can also call a backend logout endpoint here if needed.
      // Redirect to the login page.
      window.location.href = "/";
    });
  }
});
