// LearnHub Individual Student Dashboard & My Courses

async function loadStudentDashboard() {
  const nameEl = document.getElementById("studentName");
  const enrolledCountEl = document.getElementById("enrolledCount");
  const completedCountEl = document.getElementById("completedCount");
  const progressPercentEl = document.getElementById("overallProgressPercent");
  const learningStatusEl = document.getElementById("learningStatus");
  const coursesGrid = document.getElementById("dashboardCourses");

  if (!nameEl && !coursesGrid) return; // Not on dashboard page

  if (!Auth.requireLogin()) return;

  const cachedUser = Auth.getUser();
  if (nameEl && cachedUser) {
    nameEl.textContent = cachedUser.name || cachedUser.email.split("@")[0];
  }

  try {
    const data = await apiRequest("/api/progress/my/");

    if (nameEl) nameEl.textContent = data.student_name || cachedUser.name;
    if (enrolledCountEl) enrolledCountEl.textContent = data.total_enrolled;
    if (completedCountEl) completedCountEl.textContent = data.completed_courses;
    if (progressPercentEl) progressPercentEl.textContent = `${data.overall_progress}%`;

    if (learningStatusEl) {
      if (data.total_enrolled === 0) {
        learningStatusEl.textContent = "Get Started";
        learningStatusEl.style.color = "#9baaa4";
      } else if (data.completed_courses === data.total_enrolled) {
        learningStatusEl.textContent = "All Done! 🎉";
        learningStatusEl.style.color = "#34d399";
      } else {
        learningStatusEl.textContent = "Active";
        learningStatusEl.style.color = "#10b981";
      }
    }

    if (coursesGrid) {
      if (!data.courses || data.courses.length === 0) {
        coursesGrid.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 50px 20px; background: #111c19; border: 1px dashed rgba(255,255,255,0.1); border-radius: 16px;">
            <p style="font-size: 32px; margin-bottom: 8px;">🎓</p>
            <h3 style="color: #f3f7f5; margin-bottom: 6px;">You haven't enrolled in any courses yet</h3>
            <p style="color: #9baaa4; font-size: 14px; margin-bottom: 18px;">Explore our 15 career-focused categories and start learning today.</p>
            <a href="courses.html" class="primary-btn" style="display: inline-block;">Explore Courses →</a>
          </div>
        `;
      } else {
        coursesGrid.innerHTML = data.courses.map(item => `
          <article class="dynamic-course" style="display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              ${item.thumbnail_url ? `
                <div style="height: 140px; border-radius: 10px; overflow: hidden; margin-bottom: 12px; background: #15221f;">
                  <img src="${item.thumbnail_url}" alt="${item.course_title}" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
              ` : `
                <div class="course-symbol" style="font-size: 28px; margin-bottom: 10px;">💻</div>
              `}
              <span class="course-category" style="color: #10b981; font-size: 11px; font-weight: 700; text-transform: uppercase;">${item.category}</span>
              <h3 style="font-size: 18px; margin: 6px 0 10px; color: #f3f7f5;">${item.course_title}</h3>

              <!-- Progress Bar -->
              <div style="margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; color: #9baaa4;">
                  <span>Progress</span>
                  <strong style="color: #34d399;">${item.progress_percentage}%</strong>
                </div>
                <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.08); border-radius: 999px; overflow: hidden;">
                  <div style="width: ${item.progress_percentage}%; height: 100%; background: linear-gradient(90deg, #10b981, #34d399); border-radius: 999px; transition: width 0.4s ease;"></div>
                </div>
                <div style="font-size: 11px; color: #9baaa4; margin-top: 5px;">
                  ${item.completed_lessons} of ${item.total_lessons} lessons completed
                </div>
              </div>
            </div>

            <a class="card-action" href="lesson.html?course_id=${item.course_id}" style="display: block; text-align: center; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25); color: #34d399; padding: 10px; border-radius: 8px; font-weight: 600; font-size: 13.5px; transition: all 0.2s;">
              ${item.progress_percentage === 100 ? "Review Course ✓" : "Continue Learning →"}
            </a>
          </article>
        `).join("");
      }
    }
  } catch (err) {
    if (coursesGrid) {
      coursesGrid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #ef4444;">
          Failed to load dashboard data. Please try refreshing the page.
        </div>
      `;
    }
  }
}

async function loadMyCoursesPage() {
  const grid = document.getElementById("myCoursesGrid");
  const msg = document.getElementById("myCoursesMessage");
  if (!grid) return; // Not on my-courses page

  if (!Auth.requireLogin()) return;

  grid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #9baaa4;">Loading your enrollments...</div>`;
  if (msg) msg.textContent = "";

  try {
    const enrollments = await apiRequest("/api/enrollments/my/");

    if (enrollments.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; background: #111c19; border: 1px dashed rgba(255,255,255,0.1); border-radius: 16px;">
          <p style="font-size: 36px; margin-bottom: 10px;">📚</p>
          <h3 style="color: #f3f7f5; margin-bottom: 6px;">No Enrolled Courses Yet</h3>
          <p style="color: #9baaa4; font-size: 14px; margin-bottom: 20px;">Browse our catalog and enroll in your first course for free.</p>
          <a href="courses.html" class="primary-btn" style="display: inline-block;">Browse All Courses →</a>
        </div>
      `;
      return;
    }

    grid.innerHTML = enrollments.map(e => {
      const course = e.course;
      const pct = e.progress_percentage || 0;
      const lastLesson = e.last_accessed_lesson;

      return `
        <article class="dynamic-course" style="display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            ${course.thumbnail_url ? `
              <div style="height: 150px; border-radius: 10px; overflow: hidden; margin-bottom: 12px; background: #15221f;">
                <img src="${course.thumbnail_url}" alt="${course.title}" style="width: 100%; height: 100%; object-fit: cover;">
              </div>
            ` : `
              <div class="course-symbol" style="font-size: 28px; margin-bottom: 10px;">💻</div>
            `}
            <span class="course-category" style="color: #10b981; font-size: 11px; font-weight: 700; text-transform: uppercase;">${course.category}</span>
            <h3 style="font-size: 18px; margin: 6px 0 10px; color: #f3f7f5;">${course.title}</h3>

            <!-- Progress Info -->
            <div style="margin: 15px 0;">
              <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; color: #9baaa4;">
                <span>${pct === 100 ? "Completed" : "In Progress"}</span>
                <strong style="color: #34d399;">${pct}%</strong>
              </div>
              <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.08); border-radius: 999px; overflow: hidden;">
                <div style="width: ${pct}%; height: 100%; background: linear-gradient(90deg, #10b981, #34d399); border-radius: 999px;"></div>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 11.5px; color: #9baaa4; margin-top: 6px;">
                <span>${e.completed_lessons_count} of ${e.total_lessons_count} lessons</span>
                <span>Enrolled: ${new Date(e.enrolled_at).toLocaleDateString()}</span>
              </div>
            </div>

            ${lastLesson ? `
              <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); padding: 8px 12px; border-radius: 8px; font-size: 12px; color: #9baaa4; margin-bottom: 14px;">
                <span style="color: #34d399; font-weight: 600;">Current:</span> Lesson ${lastLesson.order}. ${lastLesson.title}
              </div>
            ` : ""}
          </div>

          <div style="display: flex; gap: 10px; margin-top: 10px;">
            <a class="card-action" href="lesson.html?course_id=${course.id}" style="flex: 1; text-align: center; background: #10b981; color: #04130e; padding: 10px; border-radius: 8px; font-weight: 700; font-size: 13px;">
              ${pct === 100 ? "Study Again ↺" : "Go to Lessons →"}
            </a>
            <a href="course-details.html?id=${course.id}" style="padding: 10px; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; color: #9baaa4; font-size: 13px; display: grid; place-items: center;" title="Course Syllabus">
              ℹ️
            </a>
          </div>
        </article>
      `;
    }).join("");
  } catch (err) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #ef4444;">
        Failed to load your enrolled courses.
      </div>
    `;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadStudentDashboard();
  loadMyCoursesPage();
});
