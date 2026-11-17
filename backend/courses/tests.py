from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from courses.models import Course, Lesson, Enrollment, Progress


class LMSWorkflowAndIsolationTests(TestCase):
    def setUp(self):
        self.client_a = APIClient()
        self.client_b = APIClient()
        self.client_admin = APIClient()

        # Create Student A
        self.student_a = User.objects.create_user(
            email="student_a@example.com",
            password="Password123!",
            name="Student A",
            role="student"
        )
        res_a = self.client_a.post(reverse("auth-login"), {
            "email": "student_a@example.com",
            "password": "Password123!"
        })
        self.token_a = res_a.data["access"]
        self.client_a.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")

        # Create Student B
        self.student_b = User.objects.create_user(
            email="student_b@example.com",
            password="Password123!",
            name="Student B",
            role="student"
        )
        res_b = self.client_b.post(reverse("auth-login"), {
            "email": "student_b@example.com",
            "password": "Password123!"
        })
        self.token_b = res_b.data["access"]
        self.client_b.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_b}")

        # Create Admin
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="AdminPassword123!",
            name="Super Admin"
        )
        res_admin = self.client_admin.post(reverse("auth-login"), {
            "email": "admin@example.com",
            "password": "AdminPassword123!"
        })
        self.token_admin = res_admin.data["access"]
        self.client_admin.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_admin}")

        # Setup Courses
        self.course_python = Course.objects.create(
            title="Python Mastery",
            description="Complete Python course.",
            category="Programming",
            level="Beginner",
            is_published=True
        )
        self.l1 = Lesson.objects.create(course=self.course_python, title="L1", order=1)
        self.l2 = Lesson.objects.create(course=self.course_python, title="L2", order=2)
        self.l3 = Lesson.objects.create(course=self.course_python, title="L3", order=3)
        self.l4 = Lesson.objects.create(course=self.course_python, title="L4", order=4)

        self.course_web = Course.objects.create(
            title="Web Development",
            description="HTML, CSS, JS",
            category="Web Development",
            level="Intermediate",
            is_published=True
        )
        self.w1 = Lesson.objects.create(course=self.course_web, title="HTML Basics", order=1)
        self.w2 = Lesson.objects.create(course=self.course_web, title="CSS Flexbox", order=2)

    def test_enrollment_and_duplicate_prevention(self):
        url = reverse("enrollment-list-create")
        res1 = self.client_a.post(url, {"course_id": self.course_python.id})
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        # Duplicate enrollment should fail
        res2 = self.client_a.post(url, {"course_id": self.course_python.id})
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already enrolled", res2.data["detail"].lower())

    def test_multi_user_isolation(self):
        # Student A enrolls in Python and completes 2 of 4 lessons (50%)
        self.client_a.post(reverse("enrollment-list-create"), {"course_id": self.course_python.id})
        self.client_a.post(reverse("lesson-complete", kwargs={"lesson_id": self.l1.id}))
        res_comp2 = self.client_a.post(reverse("lesson-complete", kwargs={"lesson_id": self.l2.id}))
        self.assertEqual(res_comp2.data["course_progress_percentage"], 50)

        # Student B enrolls in Python and completes 1 lesson (25%)
        self.client_b.post(reverse("enrollment-list-create"), {"course_id": self.course_python.id})
        res_comp_b = self.client_b.post(reverse("lesson-complete", kwargs={"lesson_id": self.l1.id}))
        self.assertEqual(res_comp_b.data["course_progress_percentage"], 25)

        # Check Student A's dashboard overview
        res_prog_a = self.client_a.get(reverse("my-progress"))
        self.assertEqual(res_prog_a.status_code, status.HTTP_200_OK)
        self.assertEqual(res_prog_a.data["courses"][0]["progress_percentage"], 50)

        # Check Student B's dashboard overview
        res_prog_b = self.client_b.get(reverse("my-progress"))
        self.assertEqual(res_prog_b.status_code, status.HTTP_200_OK)
        self.assertEqual(res_prog_b.data["courses"][0]["progress_percentage"], 25)

        # Verify Student B cannot see Student A's enrollments list
        enrollments_b = self.client_b.get(reverse("my-enrollments")).data
        self.assertEqual(len(enrollments_b), 1)
        self.assertEqual(enrollments_b[0]["progress_percentage"], 25)

    def test_admin_permissions(self):
        # Student cannot create courses
        url_create = reverse("course-list-create")
        res_denied = self.client_a.post(url_create, {
            "title": "Hacked Course",
            "description": "Desc",
            "category": "Tech",
        })
        self.assertEqual(res_denied.status_code, status.HTTP_403_FORBIDDEN)

        # Admin CAN create courses
        res_allowed = self.client_admin.post(url_create, {
            "title": "Official Admin Course",
            "description": "Authorized course",
            "category": "Programming",
            "level": "Beginner",
            "duration": "4 Weeks",
            "is_published": True,
        })
        self.assertEqual(res_allowed.status_code, status.HTTP_201_CREATED)

        # Student cannot access admin stats
        res_stats_denied = self.client_a.get(reverse("admin-stats"))
        self.assertEqual(res_stats_denied.status_code, status.HTTP_403_FORBIDDEN)

        # Admin can access admin stats
        res_stats_allowed = self.client_admin.get(reverse("admin-stats"))
        self.assertEqual(res_stats_allowed.status_code, status.HTTP_200_OK)
        self.assertIn("total_students", res_stats_allowed.data)
