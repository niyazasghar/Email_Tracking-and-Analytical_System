document.addEventListener("DOMContentLoaded", () => {
  // Elements for toggling forms
  const loginTabBtn = document.getElementById("loginTabBtn");
  const registerTabBtn = document.getElementById("registerTabBtn");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const loginMessage = document.getElementById("loginMessage");
  const registerMessage = document.getElementById("registerMessage");

  // Toggle: Show login form, hide registration form
  loginTabBtn.addEventListener("click", () => {
    loginForm.style.display = "block";
    registerForm.style.display = "none";
    loginMessage.innerHTML = "";
    registerMessage.innerHTML = "";
  });

  // Toggle: Show registration form, hide login form
  registerTabBtn.addEventListener("click", () => {
    loginForm.style.display = "none";
    registerForm.style.display = "block";
    loginMessage.innerHTML = "";
    registerMessage.innerHTML = "";
  });

  // LOGIN FORM SUBMISSION
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!loginForm.checkValidity()) return;

    const email = document.getElementById("emailInput").value;
    const password = document.getElementById("passwordInput").value;

    try {
      // Call /auth/login API
      const response = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Login failed");
      }

      const data = await response.json();
      // Store the token in localStorage
      localStorage.setItem("access_token", data.access_token);

      // Verify user data using /auth/me
      const meRes = await fetch("/auth/me", {
        headers: { "Authorization": `Bearer ${data.access_token}` }
      });
      if (!meRes.ok) throw new Error("Failed to validate user");
      const meData = await meRes.json();

      // Redirect based on whether the user is a superuser
      if (meData.is_superuser) {
        window.location.href = "/superuser-dashboard";
      } else {
        window.location.href = "/student-dashboard";
      }
    } catch (error) {
      console.error(error);
      loginMessage.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
  });

  // REGISTRATION FORM SUBMISSION
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!registerForm.checkValidity()) return;

    const regEmail = document.getElementById("regEmailInput").value;
    const regPassword = document.getElementById("regPasswordInput").value;
    const regConfirmPassword = document.getElementById("regConfirmPasswordInput").value;

    if (regPassword !== regConfirmPassword) {
      registerMessage.innerHTML = `<div class="alert alert-danger">Passwords do not match.</div>`;
      return;
    }

    try {
      // Call /auth/register API for user registration
      const response = await fetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: regEmail, password: regPassword })
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Registration failed");
      }
      const data = await response.json();
      registerMessage.innerHTML = `<div class="alert alert-success">Registration successful! Please login with your credentials.</div>`;

      // Auto-switch to login form after a short delay
      setTimeout(() => {
        loginTabBtn.click();
      }, 1500);
    } catch (error) {
      console.error(error);
      registerMessage.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
  });
});
