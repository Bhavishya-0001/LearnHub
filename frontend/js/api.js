// LearnHub Centralized API Client & Auth Manager

const API_BASE = "http://127.0.0.1:8000";

const Auth = {
  getAccessToken() {
    return localStorage.getItem("learnhub_access");
  },
  getRefreshToken() {
    return localStorage.getItem("learnhub_refresh");
  },
  getUser() {
    try {
      const u = localStorage.getItem("learnhub_user");
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },
  setAuth(tokens, user) {
    if (tokens?.access) localStorage.setItem("learnhub_access", tokens.access);
    if (tokens?.refresh) localStorage.setItem("learnhub_refresh", tokens.refresh);
    if (user) localStorage.setItem("learnhub_user", JSON.stringify(user));
  },
  updateUser(userData) {
    const current = this.getUser() || {};
    const updated = { ...current, ...userData };
    localStorage.setItem("learnhub_user", JSON.stringify(updated));
    return updated;
  },
  clearAuth() {
    localStorage.removeItem("learnhub_access");
    localStorage.removeItem("learnhub_refresh");
    localStorage.removeItem("learnhub_user");
  },
  isAuthenticated() {
    return !!this.getAccessToken() && !!this.getUser();
  },
  isAdmin() {
    const user = this.getUser();
    return user && (user.role === "admin" || user.is_staff);
  },
  logout() {
    const refresh = this.getRefreshToken();
    if (refresh) {
      fetch(`${API_BASE}/api/auth/logout/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.getAccessToken()}`,
        },
        body: JSON.stringify({ refresh }),
      }).catch(() => {});
    }
    this.clearAuth();
    window.location.href = "login.html";
  },
  requireLogin(role = null) {
    if (!this.isAuthenticated()) {
      const currentUrl = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `login.html?next=${currentUrl}`;
      return false;
    }
    if (role === "admin" && !this.isAdmin()) {
      window.location.href = "dashboard.html";
      return false;
    }
    return true;
  },
};

async function apiRequest(endpoint, options = {}) {
  let token = Auth.getAccessToken();

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle Token Expiry & Refresh
  if (response.status === 401 && Auth.getRefreshToken()) {
    try {
      const refreshRes = await fetch(`${API_BASE}/api/auth/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh: Auth.getRefreshToken() }),
      });
      if (refreshRes.ok) {
        const refreshData = await refreshRes.json();
        if (refreshData.access) {
          localStorage.setItem("learnhub_access", refreshData.access);
          headers["Authorization"] = `Bearer ${refreshData.access}`;
          // Retry original request
          response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers,
          });
        }
      } else {
        Auth.clearAuth();
        window.location.href = "login.html";
        throw new Error("Session expired. Please log in again.");
      }
    } catch (err) {
      Auth.clearAuth();
      window.location.href = "login.html";
      throw err;
    }
  }

  let data = {};
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    data = await response.json().catch(() => ({}));
  }

  if (!response.ok) {
    const errorMsg =
      data.detail ||
      data.message ||
      (typeof data === "object" ? Object.entries(data).map(([k, v]) => `${k}: ${v}`).join(" | ") : "Request failed");
    const error = new Error(errorMsg);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

// Global UI helper for toasts / alerts
function showNotification(msg, type = "info") {
  let toast = document.getElementById("learnhub-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "learnhub-toast";
    toast.style.position = "fixed";
    toast.style.bottom = "24px";
    toast.style.right = "24px";
    toast.style.zIndex = "9999";
    toast.style.padding = "14px 22px";
    toast.style.borderRadius = "10px";
    toast.style.fontSize = "14px";
    toast.style.fontWeight = "600";
    toast.style.boxShadow = "0 10px 30px rgba(0,0,0,0.5)";
    toast.style.transition = "all 0.3s ease";
    document.body.appendChild(toast);
  }

  if (type === "success") {
    toast.style.background = "#10b981";
    toast.style.color = "#04130e";
  } else if (type === "error") {
    toast.style.background = "#ef4444";
    toast.style.color = "#ffffff";
  } else {
    toast.style.background = "#15221f";
    toast.style.color = "#34d399";
    toast.style.border = "1px solid rgba(16,185,129,0.3)";
  }

  toast.textContent = msg;
  toast.style.opacity = "1";
  toast.style.transform = "translateY(0)";

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
  }, 4000);
}

// Global Navbar updater
function syncNavbarAuth() {
  const navActions = document.querySelector(".nav-actions");
  const navLinks = document.querySelector(".nav-links");
  const user = Auth.getUser();

  if (user && navActions) {
    let adminLink = "";
    if (user.role === "admin" || user.is_staff) {
      adminLink = `<a href="admin-dashboard.html" class="nav-admin-link" style="color: #34d399; font-weight: 600;">Admin Hub</a>`;
    }

    navActions.innerHTML = `
      <div class="user-nav-dropdown" style="display: flex; align-items: center; gap: 15px;">
        ${adminLink}
        <a href="profile.html" class="user-pill" style="display: flex; align-items: center; gap: 8px; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25); padding: 7px 14px; border-radius: 999px; color: #f3f7f5; font-size: 13px; font-weight: 500;">
          <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981;"></span>
          ${user.name || user.email.split("@")[0]}
        </a>
        <button id="logoutBtn" class="login-btn" style="cursor: pointer; background: transparent; border: 1px solid rgba(255,255,255,0.12); padding: 7px 14px; border-radius: 8px; color: #9baaa4; font-size: 13px;">Logout</button>
      </div>
    `;

    document.getElementById("logoutBtn")?.addEventListener("click", () => Auth.logout());
  }

  if (user && navLinks) {
    if (!navLinks.querySelector('a[href="dashboard.html"]')) {
      const dashA = document.createElement("a");
      dashA.href = "dashboard.html";
      dashA.textContent = "Dashboard";
      navLinks.appendChild(dashA);
    }
    if (!navLinks.querySelector('a[href="my-courses.html"]')) {
      const myA = document.createElement("a");
      myA.href = "my-courses.html";
      myA.textContent = "My Courses";
      navLinks.appendChild(myA);
    }
  }
}

document.addEventListener("DOMContentLoaded", syncNavbarAuth);
