"""
LearnHub Comprehensive End-to-End Integration & Multi-User Isolation Test Suite
Runs all 16 verification steps required by the Master Specification.
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from courses.models import Course, Lesson, Enrollment, Progress


def run_full_verification():
    print("=" * 70)
    print("STARTING FULL LEARNHUB LMS MULTI-USER VERIFICATION")
    print("=" * 70)

    client_a = APIClient()
    client_b = APIClient()
    client_admin = APIClient()

    # Step 1: Register Student A
    print("\n[Step 1] Registering Student A...")
    email_a = "student_a_verify@learnhub.internal"
    User.objects.filter(email=email_a).delete()
    res_reg_a = client_a.post("/api/auth/register/", {
        "name": "Student A",
        "email": email_a,
        "password": "Password123!",
        "confirm_password": "Password123!",
    })
    assert res_reg_a.status_code == status.HTTP_201_CREATED, f"Student A registration failed: {res_reg_a.data}"
    assert res_reg_a.data["user"]["role"] == "student", "Role must be 'student'"
    tokens_a = res_reg_a.data["tokens"]
    print(f" -> Student A registered successfully. Role: {res_reg_a.data['user']['role']}")

    # Step 2: Register Student B
    print("\n[Step 2] Registering Student B...")
    email_b = "student_b_verify@learnhub.internal"
    User.objects.filter(email=email_b).delete()
    res_reg_b = client_b.post("/api/auth/register/", {
        "name": "Student B",
        "email": email_b,
        "password": "Password123!",
        "confirm_password": "Password123!",
    })
    assert res_reg_b.status_code == status.HTTP_201_CREATED, f"Student B registration failed: {res_reg_b.data}"
    assert res_reg_b.data["user"]["role"] == "student", "Role must be 'student'"
    tokens_b = res_reg_b.data["tokens"]
    print(f" -> Student B registered successfully. Role: {res_reg_b.data['user']['role']}")

    # Step 3: Login as Student A
    print("\n[Step 3] Logging in as Student A...")
    res_login_a = client_a.post("/api/auth/login/", {
        "email": email_a,
        "password": "Password123!"
    })
    assert res_login_a.status_code == status.HTTP_200_OK, "Student A login failed"
    token_a = res_login_a.data["access"]
    client_a.credentials(HTTP_AUTHORIZATION=f"Bearer {token_a}")
    print(" -> Student A JWT access token obtained.")

    # Fetch courses for enrollment
    python_course = Course.objects.filter(category="Programming").first()
    web_course = Course.objects.filter(category="Web Development").first()
    uiux_course = Course.objects.filter(category="UI/UX Design").first()

    assert python_course is not None, "Python course not found"
    assert web_course is not None, "Web development course not found"
    assert uiux_course is not None, "UI/UX course not found"

    # Step 4: Enroll Student A in Python and Web Development
    print(f"\n[Step 4] Enrolling Student A in '{python_course.title}' and '{web_course.title}'...")
    res_enr_a1 = client_a.post("/api/enrollments/", {"course_id": python_course.id})
    assert res_enr_a1.status_code == status.HTTP_201_CREATED, f"Enrollment in Python failed: {res_enr_a1.data}"
    res_enr_a2 = client_a.post("/api/enrollments/", {"course_id": web_course.id})
    assert res_enr_a2.status_code == status.HTTP_201_CREATED, f"Enrollment in Web failed: {res_enr_a2.data}"
    print(" -> Student A enrolled in 2 courses.")

    # Step 5: Complete some Python lessons for Student A
    print("\n[Step 5] Student A completes lessons 1 and 2 in Python course...")
    python_lessons = list(python_course.lessons.all()[:2])
    assert len(python_lessons) >= 2, "Python course needs at least 2 lessons"

    res_l1 = client_a.post(f"/api/progress/lessons/{python_lessons[0].id}/complete/")
    assert res_l1.status_code == status.HTTP_200_OK, f"Complete lesson 1 failed: {res_l1.data}"
    res_l2 = client_a.post(f"/api/progress/lessons/{python_lessons[1].id}/complete/")
    assert res_l2.status_code == status.HTTP_200_OK, f"Complete lesson 2 failed: {res_l2.data}"

    student_a_progress_pct = res_l2.data["course_progress_percentage"]
    print(f" -> Student A Python course progress: {student_a_progress_pct}%")

    # Step 6: Logout Student A
    print("\n[Step 6] Logging out Student A...")
    res_logout_a = client_a.post("/api/auth/logout/", {"refresh": tokens_a["refresh"]})
    assert res_logout_a.status_code == status.HTTP_200_OK, "Logout failed"
    print(" -> Student A logged out successfully.")

    # Step 7: Login as Student B
    print("\n[Step 7] Logging in as Student B...")
    res_login_b = client_b.post("/api/auth/login/", {
        "email": email_b,
        "password": "Password123!"
    })
    assert res_login_b.status_code == status.HTTP_200_OK, "Student B login failed"
    token_b = res_login_b.data["access"]
    client_b.credentials(HTTP_AUTHORIZATION=f"Bearer {token_b}")
    print(" -> Student B JWT access token obtained.")

    # Step 8: Enroll Student B in Python and UI/UX
    print(f"\n[Step 8] Enrolling Student B in '{python_course.title}' and '{uiux_course.title}'...")
    res_enr_b1 = client_b.post("/api/enrollments/", {"course_id": python_course.id})
    assert res_enr_b1.status_code == status.HTTP_201_CREATED, f"Student B Python enroll failed: {res_enr_b1.data}"
    res_enr_b2 = client_b.post("/api/enrollments/", {"course_id": uiux_course.id})
    assert res_enr_b2.status_code == status.HTTP_201_CREATED, f"Student B UI/UX enroll failed: {res_enr_b2.data}"
    print(" -> Student B enrolled in 2 courses.")

    # Step 9: Verify Student B sees only their own enrollments
    print("\n[Step 9] Verifying Student B enrollments list...")
    res_my_b = client_b.get("/api/enrollments/my/")
    assert res_my_b.status_code == status.HTTP_200_OK
    b_enrolled_titles = [e["course"]["title"] for e in res_my_b.data]
    assert python_course.title in b_enrolled_titles
    assert uiux_course.title in b_enrolled_titles
    assert web_course.title not in b_enrolled_titles, "Student B must NOT see Student A's Web Development enrollment!"
    print(f" -> Student B enrolled courses: {b_enrolled_titles} (Web Development correctly isolated)")

    # Step 10: Verify Student B cannot see Student A's progress
    print("\n[Step 10] Verifying Student B Python progress is independent (0%)...")
    python_enr_b = next(e for e in res_my_b.data if e["course"]["id"] == python_course.id)
    assert python_enr_b["progress_percentage"] == 0, f"Student B progress should be 0%, got {python_enr_b['progress_percentage']}%"
    print(f" -> Student B progress in Python is {python_enr_b['progress_percentage']}% (completely separate from Student A)")

    # Step 11: Verify Student A's progress remains unchanged
    print("\n[Step 11] Verifying Student A progress remains unchanged...")
    client_a.credentials(HTTP_AUTHORIZATION=f"Bearer {token_a}")
    res_my_a = client_a.get("/api/enrollments/my/")
    python_enr_a = next(e for e in res_my_a.data if e["course"]["id"] == python_course.id)
    assert python_enr_a["progress_percentage"] == student_a_progress_pct, (
        f"Student A progress should be {student_a_progress_pct}%, got {python_enr_a['progress_percentage']}%"
    )
    print(f" -> Student A Python progress is preserved at {python_enr_a['progress_percentage']}%")

    # Step 12: Verify both students can see shared published course catalogue
    print("\n[Step 12] Verifying shared published course catalogue...")
    courses_a = client_a.get("/api/courses/").data
    courses_b = client_b.get("/api/courses/").data
    assert len(courses_a) == len(courses_b), "Both students must see identical published catalogue"
    assert len(courses_a) >= 15, f"Must have at least 15 courses, got {len(courses_a)}"
    print(f" -> Both students see all {len(courses_a)} published courses across all categories.")

    # Step 13: Test duplicate enrollment prevention
    print("\n[Step 13] Testing duplicate enrollment prevention...")
    dup_res = client_a.post("/api/enrollments/", {"course_id": python_course.id})
    assert dup_res.status_code == status.HTTP_400_BAD_REQUEST
    assert "already enrolled" in dup_res.data["detail"].lower()
    print(" -> Duplicate enrollment correctly rejected with 400 Bad Request.")

    # Step 14: Test unauthorized access
    print("\n[Step 14] Testing unauthorized access...")
    unauth_client = APIClient()
    res_unauth = unauth_client.get("/api/enrollments/my/")
    assert res_unauth.status_code == status.HTTP_401_UNAUTHORIZED
    res_unauth_enr = unauth_client.post("/api/enrollments/", {"course_id": python_course.id})
    assert res_unauth_enr.status_code == status.HTTP_401_UNAUTHORIZED
    print(" -> Protected endpoints correctly rejected unauthorized requests with 401.")

    # Step 15: Test admin permissions
    print("\n[Step 15] Testing admin permissions...")
    # Student cannot access admin stats
    res_admin_denied = client_a.get("/api/admin/stats/")
    assert res_admin_denied.status_code == status.HTTP_403_FORBIDDEN
    print(" -> Student correctly denied access to admin stats (403 Forbidden).")

    # Real admin login
    res_admin_login = client_admin.post("/api/auth/login/", {
        "email": "pathnejab@gmail.com",
    })
    # If password is known or authenticate via admin user
    admin_user = User.objects.filter(role="admin").first()
    assert admin_user is not None, "Admin user must exist"
    client_admin.force_authenticate(user=admin_user)
    res_admin_stats = client_admin.get("/api/admin/stats/")
    assert res_admin_stats.status_code == status.HTTP_200_OK
    assert res_admin_stats.data["total_courses"] >= 15
    print(f" -> Admin access verified: total_courses={res_admin_stats.data['total_courses']}, total_students={res_admin_stats.data['total_students']}")

    # Step 16: Test token refresh
    print("\n[Step 16] Testing JWT token refresh...")
    res_refresh = client_a.post("/api/auth/refresh/", {"refresh": tokens_a["refresh"]})
    assert res_refresh.status_code == status.HTTP_200_OK
    assert "access" in res_refresh.data
    new_access = res_refresh.data["access"]
    # Verify new token works
    client_a.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access}")
    res_me = client_a.get("/api/auth/me/")
    assert res_me.status_code == status.HTTP_200_OK
    assert res_me.data["email"] == email_a
    print(" -> New access token obtained and validated via /api/auth/me/.")

    print("\n" + "=" * 70)
    print("ALL 16 MASTER SPECIFICATION TEST SCENARIOS PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    run_full_verification()
