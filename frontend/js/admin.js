// LearnHub Admin Dashboard Control Engine

const ADMIN_CATEGORIES = [
  "Technology & IT",
  "Programming",
  "Web Development",
  "Data Science & AI",
  "Business & Sales",
  "Sales Management",
  "Design & Creative",
  "UI/UX Design",
  "Digital Marketing",
  "Finance & Accounting",
  "Human Resources",
  "Communication Skills",
  "Entrepreneurship",
  "Cloud Computing",
  "Cybersecurity"
];

let allAdminCourses = [];

async function initAdminDashboard() {
  if (!Auth.requireLogin("admin")) return;

  setupTabs();
  setupModals();
  populateCategorySelect();

  await loadAdminStats();
  await loadAdminCourses();
  await loadAdminStudents();
  await loadAdminEnrollments();
}

function setupTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(tc => tc.style.display = "none");

      btn.classList.add("active");
      const target = document.getElementById(btn.getAttribute("data-tab"));
      if (target) target.style.display = "block";
    });
  });
}

function populateCategorySelect() {
  const sel = document.getElementById("newCourseCategory");
  if (!sel) return;
  sel.innerHTML = ADMIN_CATEGORIES.map(c => `<option value="${c}">${c}</option>`).join("");
}

async function loadAdminStats() {
  try {
    const stats = await apiRequest("/api/admin/stats/");
    document.getElementById("statStudents").textContent = stats.total_students;
    document.getElementById("statCourses").textContent = stats.total_courses;
    document.getElementById("statPublished").textContent = stats.published_courses;
    document.getElementById("statEnrollments").textContent = stats.total_enrollments;
    document.getElementById("statCompleted").textContent = stats.completed_enrollments;
  } catch (err) {
    showNotification("Failed to load platform stats.", "error");
  }
}

async function loadAdminCourses() {
  const tbody = document.getElementById("adminCoursesTable");
  if (!tbody) return;

  try {
    allAdminCourses = await apiRequest("/api/courses/");
    if (allAdminCourses.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #9baaa4; padding: 30px;">No courses created yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = allAdminCourses.map(c => `
      <tr>
        <td style="color: #9baaa4;">#${c.id}</td>
        <td>
          <strong style="color: #f3f7f5;">${c.title}</strong>
          <div style="font-size: 11px; color: #9baaa4;">${c.lessons_count || 0} Lessons • ${c.instructor_name || 'Faculty'}</div>
        </td>
        <td><span style="color: #34d399; font-size: 12px;">${c.category}</span></td>
        <td><span style="background: rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 4px; font-size: 11px;">${c.level}</span></td>
        <td>${c.duration}</td>
        <td>
          <button class="toggle-pub-btn" data-id="${c.id}" data-pub="${c.is_published}" style="cursor: pointer; padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; border: none; background: ${c.is_published ? 'rgba(16,185,129,0.18)' : 'rgba(239,68,68,0.18)'}; color: ${c.is_published ? '#34d399' : '#ef4444'};">
            ${c.is_published ? '● Published' : '○ Unpublished'}
          </button>
        </td>
        <td>
          <div style="display: flex; gap: 8px;">
            <button class="add-lesson-btn" data-id="${c.id}" data-title="${c.title}" style="cursor: pointer; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25); color: #34d399; padding: 4px 10px; border-radius: 6px; font-size: 12px;">
              + Lesson
            </button>
            <button class="del-course-btn" data-id="${c.id}" style="cursor: pointer; background: transparent; border: 1px solid rgba(239,68,68,0.3); color: #ef4444; padding: 4px 8px; border-radius: 6px; font-size: 12px;">
              Delete
            </button>
          </div>
        </td>
      </tr>
    `).join("");

    attachCourseActionListeners();
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #ef4444; padding: 30px;">Error loading courses.</td></tr>`;
  }
}

function attachCourseActionListeners() {
  document.querySelectorAll(".toggle-pub-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const courseId = btn.getAttribute("data-id");
      const currentPub = btn.getAttribute("data-pub") === "true";
      try {
        await apiRequest(`/api/courses/${courseId}/`, {
          method: "PUT",
          body: JSON.stringify({ is_published: !currentPub }),
        });
        showNotification(`Course ${!currentPub ? 'published' : 'unpublished'}!`, "success");
        await loadAdminStats();
        await loadAdminCourses();
      } catch (err) {
        showNotification("Failed to update course status.", "error");
      }
    });
  });

  document.querySelectorAll(".del-course-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const courseId = btn.getAttribute("data-id");
      if (!confirm("Are you sure you want to delete this course? This will remove its lessons and enrollments.")) return;
      try {
        await apiRequest(`/api/courses/${courseId}/`, { method: "DELETE" });
        showNotification("Course deleted.", "success");
        await loadAdminStats();
        await loadAdminCourses();
      } catch (err) {
        showNotification("Failed to delete course.", "error");
      }
    });
  });

  document.querySelectorAll(".add-lesson-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const courseId = btn.getAttribute("data-id");
      const courseTitle = btn.getAttribute("data-title");
      openAddLessonModal(courseId, courseTitle);
    });
  });
}

async function loadAdminStudents() {
  const tbody = document.getElementById("adminStudentsTable");
  if (!tbody) return;

  try {
    const students = await apiRequest("/api/admin/students/");
    if (students.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #9baaa4; padding: 30px;">No registered students yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = students.map(s => `
      <tr>
        <td style="color: #9baaa4;">#${s.id}</td>
        <td><strong style="color: #f3f7f5;">${s.name}</strong></td>
        <td>${s.email}</td>
        <td><span style="color: #34d399; font-weight: 700;">${s.total_enrollments}</span> courses</td>
        <td><span style="color: #10b981; font-weight: 700;">${s.completed_courses}</span> completed</td>
        <td style="color: #9baaa4;">${new Date(s.date_joined).toLocaleDateString()}</td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #ef4444; padding: 30px;">Error loading students.</td></tr>`;
  }
}

async function loadAdminEnrollments() {
  const tbody = document.getElementById("adminEnrollmentsTable");
  if (!tbody) return;

  try {
    const enrollments = await apiRequest("/api/admin/enrollments/");
    if (enrollments.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #9baaa4; padding: 30px;">No enrollments recorded yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = enrollments.map(e => `
      <tr>
        <td style="color: #9baaa4;">#${e.id}</td>
        <td>
          <div style="font-weight: 600; color: #f3f7f5;">${e.student_name}</div>
          <div style="font-size: 11px; color: #9baaa4;">${e.student_email}</div>
        </td>
        <td><span style="color: #34d399;">${e.course_title}</span></td>
        <td>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 80px; height: 6px; background: rgba(255,255,255,0.08); border-radius: 999px;">
              <div style="width: ${e.progress_percentage}%; height: 100%; background: #10b981; border-radius: 999px;"></div>
            </div>
            <span style="font-size: 12px; font-weight: 700; color: #f3f7f5;">${e.progress_percentage}%</span>
          </div>
        </td>
        <td style="color: #9baaa4;">${new Date(e.enrolled_at).toLocaleDateString()}</td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #ef4444; padding: 30px;">Error loading enrollments.</td></tr>`;
  }
}

function setupModals() {
  const createModal = document.getElementById("createCourseModal");
  const openCreateBtn = document.getElementById("openCreateCourseModal");
  const closeCreateBtn = document.getElementById("closeCreateCourseModal");
  const createForm = document.getElementById("createCourseForm");

  if (openCreateBtn) openCreateBtn.onclick = () => createModal.classList.add("open");
  if (closeCreateBtn) closeCreateBtn.onclick = () => createModal.classList.remove("open");

  if (createForm) {
    createForm.onsubmit = async (e) => {
      e.preventDefault();
      const payload = {
        title: document.getElementById("newCourseTitle").value.trim(),
        category: document.getElementById("newCourseCategory").value,
        level: document.getElementById("newCourseLevel").value,
        duration: document.getElementById("newCourseDuration").value.trim() || "8 Weeks",
        instructor_name: document.getElementById("newCourseInstructor").value.trim() || "LearnHub Faculty",
        thumbnail_url: document.getElementById("newCourseThumb").value.trim() || "",
        description: document.getElementById("newCourseDesc").value.trim(),
        is_published: true,
      };

      try {
        await apiRequest("/api/courses/", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        showNotification("Course created successfully!", "success");
        createModal.classList.remove("open");
        createForm.reset();
        await loadAdminStats();
        await loadAdminCourses();
      } catch (err) {
        showNotification(err.message || "Failed to create course.", "error");
      }
    };
  }

  // Add Lesson Modal
  const lessonModal = document.getElementById("addLessonModal");
  const closeLessonBtn = document.getElementById("closeAddLessonModal");
  const addLessonForm = document.getElementById("addLessonForm");

  if (closeLessonBtn) closeLessonBtn.onclick = () => lessonModal.classList.remove("open");

  if (addLessonForm) {
    addLessonForm.onsubmit = async (e) => {
      e.preventDefault();
      const courseId = document.getElementById("lessonTargetCourseId").value;
      const payload = {
        title: document.getElementById("newLessonTitle").value.trim(),
        order: Number(document.getElementById("newLessonOrder").value),
        duration: document.getElementById("newLessonDuration").value.trim() || "15 mins",
        content_url: document.getElementById("newLessonVideoUrl").value.trim() || "",
        description: document.getElementById("newLessonDesc").value.trim(),
      };

      try {
        await apiRequest(`/api/admin/courses/${courseId}/lessons/`, {
          method: "POST",
          body: JSON.stringify(payload),
        });
        showNotification("Lesson added successfully!", "success");
        lessonModal.classList.remove("open");
        addLessonForm.reset();
        await loadAdminCourses();
      } catch (err) {
        showNotification(err.message || "Failed to add lesson.", "error");
      }
    };
  }
}

function openAddLessonModal(courseId, courseTitle) {
  const modal = document.getElementById("addLessonModal");
  document.getElementById("addLessonModalTitle").textContent = `Add Lesson to: ${courseTitle}`;
  document.getElementById("lessonTargetCourseId").value = courseId;

  // Predict next order
  const course = allAdminCourses.find(c => c.id == courseId);
  if (course) {
    document.getElementById("newLessonOrder").value = (course.lessons_count || 0) + 1;
  }

  modal.classList.add("open");
}

document.addEventListener("DOMContentLoaded", initAdminDashboard);
