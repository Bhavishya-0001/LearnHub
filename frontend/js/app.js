// LearnHub App Main Utilities

const API_BASE_URL = "http://127.0.0.1:8000";

function getCurrentUser() {
  return Auth.getUser();
}

function requireLogin(role = null) {
  return Auth.requireLogin(role);
}

function logoutUser() {
  Auth.logout();
}

// Auto-run mobile menu toggles or common dynamic effects
document.addEventListener("DOMContentLoaded", () => {
  // Smooth scroll
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function(e) {
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth" });
      }
    });
  });
});
