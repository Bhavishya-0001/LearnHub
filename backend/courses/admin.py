from django.contrib import admin
from .models import Course, Lesson, Enrollment, Progress


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ("order", "title", "duration", "content_url", "description")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "level", "duration", "is_published", "created_at")
    search_fields = ("title", "category", "instructor_name")
    list_filter = ("category", "level", "is_published")
    list_editable = ("is_published",)
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "order", "duration")
    list_filter = ("course",)
    search_fields = ("title", "course__title")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "course", "enrolled_at")
    search_fields = ("user__email", "user__name", "course__title")
    list_filter = ("course",)


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "lesson", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("enrollment__user__email", "lesson__title")
