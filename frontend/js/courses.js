// LearnHub Real Backend-Connected Course Catalogue & Details

const CATEGORIES_LIST = [
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

function getCategoryIcon(cat) {
  const map = {
    "Technology & IT": "💻",
    "Programming": "🐍",
    "Web Development": "🌐",
    "Data Science & AI": "🤖",
    "Business & Sales": "📊",
    "Sales Management": "📈",
    "Design & Creative": "🎨",
    "UI/UX Design": "✨",
    "Digital Marketing": "📢",
    "Finance & Accounting": "💰",
    "Human Resources": "👥",
    "Communication Skills": "🗣️",
    "Entrepreneurship": "🚀",
    "Cloud Computing": "☁️",
    "Cybersecurity": "🛡️",
  };
  return map[cat] || "📚";
}

function createCourseCard(course) {
  const icon = getCategoryIcon(course.category);
  const enrolledBadge = course.is_enrolled
    ? `<span style="background: rgba(16,185,129,0.18); color: #34d399; font-size: 11px; padding: 4px 8px; border-radius: 6px; font-weight: 700;">ENROLLED (${course.progress_percentage || 0}%)</span>`
    : "";

  const thumbnailHtml = course.thumbnail_url
    ? `<div class="course-card-thumb" style="width: 100%; height: 160px; border-radius: 12px; overflow: hidden; margin-bottom: 15px; position: relative; background: #15221f;">
         <img src="${course.thumbnail_url}" alt="${course.title}" style="width: 100%; height: 100%; object-fit: cover;">
         <span style="position: absolute; top: 10px; right: 10px; background: rgba(8,14,13,0.85); padding: 4px 10px; border-radius: 6px; font-size: 11px; color: #34d399; font-weight: 700;">${icon} ${course.level}</span>
       </div>`
    : `<div class="course-symbol" style="font-size: 32px; margin-bottom: 12px;">${icon}</div>`;

  return `
    <article class="dynamic-course" style="display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
      <div>
        ${thumbnailHtml}
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span class="course-category" style="color: #10b981; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">${course.category}</span>
          ${enrolledBadge}
        </div>
        <h3 style="font-size: 19px; line-height: 1.4; margin-bottom: 8px; color: #f3f7f5;">${course.title}</h3>
        <p style="color: #9baaa4; font-size: 13.5px; line-height: 1.5; margin-bottom: 15px;">${course.description}</p>
      </div>

      <div>
        <div style="display: flex; justify-content: space-between; font-size: 12px; color: #9baaa4; border-top: 1px solid rgba(255,255,255,0.07); padding-top: 12px; margin-bottom: 12px;">
          <span>⏳ ${course.duration || "Self-paced"}</span>
          <span>📖 ${course.lessons_count || 0} Lessons</span>
        </div>
        <a class="card-action" href="course-details.html?id=${course.id}" style="display: block; text-align: center; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25); color: #34d399; padding: 10px; border-radius: 8px; font-weight: 600; font-size: 13.5px; transition: all 0.2s;">
          ${course.is_enrolled ? "Continue Learning →" : "View Course Details →"}
        </a>
      </div>
    </article>
  `;
}

async function renderCourses() {
  const grid = document.getElementById("coursesGrid");
  if (!grid) return;

  const search = document.getElementById("courseSearch");
  const categoryFilter = document.getElementById("categoryFilter");
  const levelFilter = document.getElementById("levelFilter");
  const coursesMessage = document.getElementById("coursesMessage");

  // Populate Categories in Dropdown
  if (categoryFilter && categoryFilter.options.length <= 1) {
    categoryFilter.innerHTML = '<option value="all">All Categories</option>';
    CATEGORIES_LIST.forEach(cat => {
      const opt = document.createElement("option");
      opt.value = cat;
      opt.textContent = cat;
      categoryFilter.appendChild(opt);
    });

    // Check URL param for pre-selected category
    const urlParams = new URLSearchParams(window.location.search);
    const catParam = urlParams.get("category");
    if (catParam) {
      categoryFilter.value = catParam;
    }
  }

  async function fetchAndDisplay() {
    grid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #9baaa4;">Loading courses...</div>`;
    if (coursesMessage) coursesMessage.textContent = "";

    const queryParams = new URLSearchParams();
    if (search && search.value.trim()) {
      queryParams.set("search", search.value.trim());
    }
    if (categoryFilter && categoryFilter.value !== "all") {
      queryParams.set("category", categoryFilter.value);
    }
    if (levelFilter && levelFilter.value !== "all") {
      queryParams.set("level", levelFilter.value);
    }

    try {
      const courses = await apiRequest(`/api/courses/?${queryParams.toString()}`);
      if (courses.length === 0) {
        grid.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; background: #111c19; border: 1px dashed rgba(255,255,255,0.1); border-radius: 16px;">
            <p style="font-size: 28px; margin-bottom: 10px;">🔍</p>
            <h3 style="color: #f3f7f5; margin-bottom: 6px;">No courses found</h3>
            <p style="color: #9baaa4; font-size: 14px;">Try adjusting your search keywords or category filters.</p>
          </div>
        `;
        return;
      }

      grid.innerHTML = courses.map(createCourseCard).join("");
    } catch (err) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #ef4444;">
          Failed to load courses. Please check your backend connection.
        </div>
      `;
    }
  }

  let debounceTimer;
  if (search) {
    search.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(fetchAndDisplay, 300);
    });
  }
  if (categoryFilter) categoryFilter.addEventListener("change", fetchAndDisplay);
  if (levelFilter) levelFilter.addEventListener("change", fetchAndDisplay);

  fetchAndDisplay();
}

async function renderCourseDetails() {
  const container = document.getElementById("courseDetails");
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const courseId = params.get("id");

  if (!courseId) {
    window.location.href = "courses.html";
    return;
  }

  try {
    const course = await apiRequest(`/api/courses/${courseId}/`);

    document.getElementById("detailTitle").textContent = course.title;
    document.getElementById("detailDescription").textContent = course.description;
    document.getElementById("detailCategory").textContent = `${getCategoryIcon(course.category)} ${course.category}`;
    document.getElementById("detailLevel").textContent = `Level: ${course.level}`;
    document.getElementById("detailInstructor").textContent = `Instructor: ${course.instructor_name || "LearnHub Faculty"}`;

    const durationEl = document.getElementById("detailDuration");
    if (durationEl) durationEl.textContent = `Duration: ${course.duration || "Self-Paced"}`;

    const lessonsCountEl = document.getElementById("detailLessonsCount");
    if (lessonsCountEl) lessonsCountEl.textContent = `${course.lessons_count || 0} Lessons`;

    // Render lessons list
    const lessonsListEl = document.getElementById("detailLessons");
    if (lessonsListEl) {
      if (course.lessons && course.lessons.length > 0) {
        lessonsListEl.innerHTML = course.lessons.map(lesson => `
          <li style="display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 12px;">
              <span style="display: grid; place-items: center; width: 28px; height: 28px; border-radius: 50%; background: ${lesson.is_completed ? '#10b981' : 'rgba(255,255,255,0.08)'}; color: ${lesson.is_completed ? '#04130e' : '#9baaa4'}; font-size: 12px; font-weight: 700;">
                ${lesson.is_completed ? '✓' : lesson.order}
              </span>
              <div>
                <strong style="color: #f3f7f5; font-size: 14.5px;">${lesson.title}</strong>
                <p style="color: #9baaa4; font-size: 12px; margin-top: 3px;">${lesson.description || ""}</p>
              </div>
            </div>
            <span style="color: #9baaa4; font-size: 12px;">${lesson.duration || "15 mins"}</span>
          </li>
        `).join("");
      } else {
        lessonsListEl.innerHTML = `<li style="color: #9baaa4; padding: 10px;">No lessons published for this course yet.</li>`;
      }
    }

    // Configure Enrollment Button
    const enrollBtn = document.getElementById("enrollButton");
    const enrollMsg = document.getElementById("enrollMessage");

    if (enrollBtn) {
      if (course.is_enrolled) {
        enrollBtn.textContent = `Continue Learning (${course.progress_percentage || 0}%) →`;
        enrollBtn.style.background = "#34d399";
        enrollBtn.onclick = () => {
          window.location.href = `lesson.html?course_id=${course.id}`;
        };
      } else {
        enrollBtn.textContent = "Enroll Now (Free) →";
        enrollBtn.onclick = async () => {
          if (!Auth.isAuthenticated()) {
            const nextUrl = encodeURIComponent(`course-details.html?id=${course.id}`);
            window.location.href = `login.html?next=${nextUrl}`;
            return;
          }

          try {
            enrollBtn.disabled = true;
            enrollBtn.textContent = "Enrolling...";

            const res = await apiRequest("/api/enrollments/", {
              method: "POST",
              body: JSON.stringify({ course_id: course.id }),
            });

            enrollMsg.style.color = "#10b981";
            enrollMsg.textContent = res.message || "Enrolled successfully! Redirecting...";

            setTimeout(() => {
              window.location.href = `lesson.html?course_id=${course.id}`;
            }, 800);
          } catch (err) {
            enrollMsg.style.color = "#ef4444";
            enrollMsg.textContent = err.message || "Enrollment failed.";
            enrollBtn.disabled = false;
            enrollBtn.textContent = "Enroll Now (Free) →";
          }
        };
      }
    }

    // Render Related Courses
    const relatedContainer = document.getElementById("relatedCoursesGrid");
    if (relatedContainer && course.related_courses && course.related_courses.length > 0) {
      relatedContainer.innerHTML = course.related_courses.map(r => `
        <div style="background: #111c19; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px;">
          <span style="font-size: 11px; color: #10b981; font-weight: 700;">${r.category}</span>
          <h4 style="margin: 6px 0; font-size: 15px;"><a href="course-details.html?id=${r.id}" style="color: #f3f7f5;">${r.title}</a></h4>
          <span style="font-size: 12px; color: #9baaa4;">Level: ${r.level}</span>
          <a href="course-details.html?id=${r.id}" style="display: block; margin-top: 10px; color: #34d399; font-size: 12.5px; font-weight: 600;">View →</a>
        </div>
      `).join("");
    }
  } catch (err) {
    container.innerHTML = `
      <div style="text-align: center; padding: 60px 20px;">
        <h2 style="color: #ef4444; margin-bottom: 12px;">Course not found</h2>
        <p style="color: #9baaa4; margin-bottom: 20px;">The course you are looking for does not exist or has been unpublished.</p>
        <a href="courses.html" class="primary-btn" style="display: inline-block;">Return to Course Catalogue</a>
      </div>
    `;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderCourses();
  renderCourseDetails();
});
