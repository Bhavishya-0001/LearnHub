// LearnHub Student Profile Manager

document.addEventListener("DOMContentLoaded", async () => {
  if (!Auth.requireLogin()) return;

  const nameInput = document.getElementById("profileName");
  const emailInput = document.getElementById("profileEmail");
  const joinedInput = document.getElementById("profileJoined");
  const avatarEl = document.getElementById("profileAvatar");
  const nameHeading = document.getElementById("profileNameHeading");
  const roleBadge = document.getElementById("profileRoleBadge");
  const form = document.getElementById("profileForm");

  try {
    const profile = await apiRequest("/api/profile/");

    nameInput.value = profile.name || "";
    emailInput.value = profile.email || "";
    nameHeading.textContent = profile.name || "Student";
    roleBadge.textContent = profile.role || "Student";

    const initials = (profile.name || profile.email).charAt(0).toUpperCase();
    avatarEl.textContent = initials;

    if (profile.date_joined) {
      joinedInput.value = new Date(profile.date_joined).toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    }

    // Handle updates
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const updatedName = nameInput.value.trim();
      if (!updatedName) return;

      try {
        const res = await apiRequest("/api/profile/", {
          method: "PUT",
          body: JSON.stringify({ name: updatedName }),
        });

        Auth.updateUser({ name: res.name });
        nameHeading.textContent = res.name;
        showNotification("Profile updated successfully!", "success");
      } catch (err) {
        showNotification(err.message || "Failed to update profile.", "error");
      }
    });

    document.getElementById("profileLogoutBtn")?.addEventListener("click", () => {
      Auth.logout();
    });
  } catch (err) {
    showNotification("Failed to load profile.", "error");
  }
});
