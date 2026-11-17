from django.conf import settings
from django.db import models


class Course(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    level = models.CharField(
        max_length=30,
        default="Beginner"
    )
    instructor_name = models.CharField(
        max_length=120,
        blank=True
    )
    thumbnail_url = models.CharField(
        max_length=500,
        blank=True,
        default=""
    )
    duration = models.CharField(
        max_length=50,
        blank=True,
        default="8 Weeks"
    )
    is_published = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def lessons_count(self):
        return self.lessons.count()


class Lesson(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(
        blank=True,
        default=""
    )
    content_url = models.URLField(
        blank=True,
        default=""
    )
    duration = models.CharField(
        max_length=50,
        blank=True,
        default="15 mins"
    )
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.order}. {self.title}"


class Enrollment(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_enrollment"
            )
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.course.title}"

    def calculate_progress(self):
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return 0
        completed_count = self.progress_items.filter(status="completed").count()
        return round((completed_count / total_lessons) * 100)


class Progress(models.Model):

    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="progress_items"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="progress_items"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="not_started"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "lesson"],
                name="unique_enrollment_lesson_progress"
            )
        ]

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.lesson.title}: {self.status}"
