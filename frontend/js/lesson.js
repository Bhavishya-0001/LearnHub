// LearnHub Interactive Lesson & Progress Engine

let currentCourse = null;
let currentLessonIndex = 0;

async function initClassroom() {
  if (!Auth.requireLogin()) return;

  const params = new URLSearchParams(window.location.search);
  const courseId = params.get("course_id");
  const lessonIdParam = params.get("lesson_id");

  if (!courseId) {
    window.location.href = "my-courses.html";
    return;
  }

  try {
    currentCourse = await apiRequest(`/api/courses/${courseId}/`);

    // Enrollment check
    if (!currentCourse.is_enrolled) {
      showNotification("You must be enrolled in this course to access lessons.", "error");
      setTimeout(() => {
        window.location.href = `course-details.html?id=${courseId}`;
      }, 1200);
      return;
    }

    if (!currentCourse.lessons || currentCourse.lessons.length === 0) {
      document.getElementById("lessonTitle").textContent = "No lessons found for this course yet.";
      return;
    }

    // Set course title & back link
    document.getElementById("courseHeaderTitle").textContent = currentCourse.title;
    document.getElementById("backToCourse").href = `course-details.html?id=${currentCourse.id}`;

    // Determine initial lesson index
    if (lessonIdParam) {
      const idx = currentCourse.lessons.findIndex(l => l.id === Number(lessonIdParam));
      currentLessonIndex = idx >= 0 ? idx : 0;
    } else {
      // Default to first incomplete lesson or 0
      const firstIncompleteIdx = currentCourse.lessons.findIndex(l => !l.is_completed);
      currentLessonIndex = firstIncompleteIdx >= 0 ? firstIncompleteIdx : 0;
    }

    updateClassroomView();
    setupEventListeners();
  } catch (err) {
    showNotification("Failed to load course lessons.", "error");
    document.getElementById("lessonTitle").textContent = "Error loading classroom.";
  }
}

function updateClassroomView() {
  const lesson = currentCourse.lessons[currentLessonIndex];
  if (!lesson) return;

  // Header & Content
  document.getElementById("lessonOrderBadge").textContent = `LESSON ${lesson.order} OF ${currentCourse.lessons.length}`;
  document.getElementById("lessonTitle").textContent = lesson.title;
  document.getElementById("lessonDuration").textContent = `Duration: ${lesson.duration || "15 mins"}`;
  document.getElementById("lessonDescription").textContent =
    lesson.description || "In this lesson, you will learn key industry concepts and apply them practically.";

  // Video embed
  const videoIframe = document.getElementById("lessonVideo");
  if (lesson.content_url) {
    videoIframe.src = lesson.content_url;
  } else {
    // Fallback safe embed
    videoIframe.src = "https://www.youtube.com/embed/_uQrJ0TkZlc";
  }

  // Complete button
  const completeBtn = document.getElementById("completeBtn");
  if (lesson.is_completed) {
    completeBtn.textContent = "✓ Completed (Click to Toggle)";
    completeBtn.style.background = "#15221f";
    completeBtn.style.color = "#34d399";
    completeBtn.style.border = "1px solid #10b981";
  } else {
    completeBtn.textContent = "✓ Mark as Completed";
    completeBtn.style.background = "#10b981";
    completeBtn.style.color = "#04130e";
    completeBtn.style.border = "none";
  }

  // Prev / Next buttons
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");
  prevBtn.disabled = currentLessonIndex === 0;
  prevBtn.style.opacity = currentLessonIndex === 0 ? "0.4" : "1";

  if (currentLessonIndex === currentCourse.lessons.length - 1) {
    nextBtn.textContent = "Finish Course 🎓";
  } else {
    nextBtn.textContent = "Next Lesson →";
  }

  // Progress Bar and Counter
  const completedCount = currentCourse.lessons.filter(l => l.is_completed).length;
  const total = currentCourse.lessons.length;
  const pct = Math.round((completedCount / total) * 100);

  document.getElementById("progressBadge").textContent = `${pct}%`;
  document.getElementById("progressFill").style.width = `${pct}%`;
  document.getElementById("lessonsCounter").textContent = `${completedCount} of ${total} completed`;

  // Render Sidebar
  renderSidebar();
}

function renderSidebar() {
  const container = document.getElementById("lessonsSidebarList");
  if (!container) return;

  container.innerHTML = currentCourse.lessons.map((lesson, idx) => {
    const isActive = idx === currentLessonIndex;
    const isCompleted = lesson.is_completed;

    return `
      <div class="lesson-sidebar-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}" data-index="${idx}">
        <span class="check-bubble">
          ${isCompleted ? '✓' : lesson.order}
        </span>
        <div style="flex: 1; min-width: 0;">
          <div style="font-size: 13.5px; font-weight: ${isActive ? '700' : '500'}; color: ${isActive ? '#34d399' : '#f3f7f5'}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
            ${lesson.title}
          </div>
          <span style="font-size: 11px; color: #9baaa4;">${lesson.duration || "15 mins"}</span>
        </div>
      </div>
    `;
  }).join("");

  // Attach click listener to sidebar items
  container.querySelectorAll(".lesson-sidebar-item").forEach(item => {
    item.addEventListener("click", () => {
      const idx = Number(item.getAttribute("data-index"));
      currentLessonIndex = idx;
      updateClassroomView();
    });
  });
}

function setupEventListeners() {
  const completeBtn = document.getElementById("completeBtn");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");

  completeBtn.addEventListener("click", async () => {
    const lesson = currentCourse.lessons[currentLessonIndex];
    try {
      completeBtn.disabled = true;
      const res = await apiRequest(`/api/progress/lessons/${lesson.id}/complete/`, {
        method: "POST",
        body: JSON.stringify({ action: "toggle" }),
      });

      lesson.is_completed = res.lesson_status === "completed";
      showNotification(res.message, "success");
      updateClassroomView();
    } catch (err) {
      showNotification(err.message || "Failed to update progress.", "error");
    } finally {
      completeBtn.disabled = false;
    }
  });

  prevBtn.addEventListener("click", () => {
    if (currentLessonIndex > 0) {
      currentLessonIndex--;
      updateClassroomView();
    }
  });

  nextBtn.addEventListener("click", () => {
    if (currentLessonIndex < currentCourse.lessons.length - 1) {
      currentLessonIndex++;
      updateClassroomView();
    } else {
      showNotification("Congratulations on finishing all lessons! 🎉", "success");
      setTimeout(() => {
        window.location.href = "my-courses.html";
      }, 1200);
    }
  });
}

document.addEventListener("DOMContentLoaded", initClassroom);
