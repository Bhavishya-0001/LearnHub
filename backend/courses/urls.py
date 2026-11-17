from django.urls import path
from .views import (
    CourseListCreateView,
    CourseDetailView,
    EnrollmentListCreateView,
    EnrollmentDetailView,
    LessonCompleteView,
    UserProgressOverviewView,
    AdminStatsView,
    AdminStudentsListView,
    AdminEnrollmentsListView,
    AdminCourseLessonsView,
    AdminLessonDetailView,
)

urlpatterns = [
    # Courses
    path("courses/", CourseListCreateView.as_view(), name="course-list-create"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),

    # Enrollments
    path("enrollments/", EnrollmentListCreateView.as_view(), name="enrollment-list-create"),
    path("enrollments/my/", EnrollmentListCreateView.as_view(), name="my-enrollments"),
    path("enrollments/<int:pk>/", EnrollmentDetailView.as_view(), name="enrollment-detail"),

    # Progress
    path("progress/my/", UserProgressOverviewView.as_view(), name="my-progress"),
    path("progress/lessons/<int:lesson_id>/complete/", LessonCompleteView.as_view(), name="lesson-complete"),

    # Admin Management
    path("admin/stats/", AdminStatsView.as_view(), name="admin-stats"),
    path("admin/students/", AdminStudentsListView.as_view(), name="admin-students"),
    path("admin/enrollments/", AdminEnrollmentsListView.as_view(), name="admin-enrollments"),
    path("admin/courses/<int:course_id>/lessons/", AdminCourseLessonsView.as_view(), name="admin-course-add-lesson"),
    path("admin/lessons/<int:pk>/", AdminLessonDetailView.as_view(), name="admin-lesson-detail"),
]
