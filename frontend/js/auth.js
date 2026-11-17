// LearnHub Production Authentication Client

document.addEventListener("DOMContentLoaded", () => {
  const registerForm = document.getElementById("registerForm");
  const loginForm = document.getElementById("loginForm");

  // Redirect away if already logged in
  if (Auth.isAuthenticated()) {
    const params = new URLSearchParams(window.location.search);
    const next = params.get("next");
    if (next) {
      window.location.href = decodeURIComponent(next);
      return;
    }
    // If already logged in, redirect to dashboard
    if (window.location.pathname.endsWith("login.html") || window.location.pathname.endsWith("register.html")) {
      window.location.href = Auth.isAdmin() ? "admin-dashboard.html" : "dashboard.html";
      return;
    }
  }

  // Real Registration
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const message = document.getElementById("registerMessage");
      const submitBtn = registerForm.querySelector("button[type='submit']");

      const name = document.getElementById("name").value.trim();
      const email = document.getElementById("email").value.trim().toLowerCase();
      const password = document.getElementById("password").value;
      const confirmPassword = document.getElementById("confirmPassword").value;

      message.style.color = "#ef4444";
      message.textContent = "";

      if (password.length < 8) {
        message.textContent = "Password must be at least 8 characters.";
        return;
      }

      if (password !== confirmPassword) {
        message.textContent = "Passwords do not match.";
        return;
      }

      try {
        submitBtn.disabled = true;
        submitBtn.textContent = "Creating Account...";

        const response = await apiRequest("/api/auth/register/", {
          method: "POST",
          body: JSON.stringify({
            name,
            email,
            password,
            confirm_password: confirmPassword,
          }),
        });

        message.style.color = "#10b981";
        message.textContent = "Account created successfully! Loading your dashboard...";

        // Save real tokens and user data
        Auth.setAuth(response.tokens, response.user);

        setTimeout(() => {
          window.location.href = "dashboard.html";
        }, 800);
      } catch (err) {
        message.style.color = "#ef4444";
        message.textContent = err.message || "Registration failed. Please check your inputs.";
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Create account →";
      }
    });
  }

  // Real Login
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const message = document.getElementById("loginMessage");
      const submitBtn = loginForm.querySelector("button[type='submit']");

      const email = document.getElementById("loginEmail").value.trim().toLowerCase();
      const password = document.getElementById("loginPassword").value;

      message.style.color = "#ef4444";
      message.textContent = "";

      if (!email || !password) {
        message.textContent = "Please enter both email and password.";
        return;
      }

      try {
        submitBtn.disabled = true;
        submitBtn.textContent = "Authenticating...";

        const response = await apiRequest("/api/auth/login/", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        });

        // Store real JWT tokens and user profile
        Auth.setAuth(
          { access: response.access, refresh: response.refresh },
          response.user
        );

        message.style.color = "#10b981";
        message.textContent = "Login successful! Opening your learning space...";

        const params = new URLSearchParams(window.location.search);
        const next = params.get("next");

        setTimeout(() => {
          if (next) {
            window.location.href = decodeURIComponent(next);
          } else if (response.user.role === "admin" || response.user.is_staff) {
            window.location.href = "admin-dashboard.html";
          } else {
            window.location.href = "dashboard.html";
          }
        }, 700);
      } catch (err) {
        message.style.color = "#ef4444";
        message.textContent = err.message || "Invalid email or password. Please try again.";
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Sign In →";
      }
    });
  }
});
