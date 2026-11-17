from rest_framework import serializers
from .models import Course, Lesson, Enrollment, Progress


class LessonSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "course",
            "title",
            "description",
            "content_url",
            "duration",
            "order",
            "is_completed",
        )
        read_only_fields = ("id", "is_completed")

    def get_is_completed(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        # Find enrollment for current user
        enrollment = Enrollment.objects.filter(user=request.user, course=obj.course).first()
        if not enrollment:
            return False
        prog = Progress.objects.filter(enrollment=enrollment, lesson=obj, status="completed").exists()
        return prog


class LessonAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseListSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "category",
            "level",
            "instructor_name",
            "thumbnail_url",
            "duration",
            "is_published",
            "created_at",
            "lessons_count",
            "is_enrolled",
            "progress_percentage",
        )

    def get_is_enrolled(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return Enrollment.objects.filter(user=request.user, course=obj).exists()

    def get_progress_percentage(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return 0
        enrollment = Enrollment.objects.filter(user=request.user, course=obj).first()
        if not enrollment:
            return 0
        return enrollment.calculate_progress()


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.IntegerField(read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    related_courses = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "category",
            "level",
            "instructor_name",
            "thumbnail_url",
            "duration",
            "is_published",
            "created_at",
            "lessons_count",
            "is_enrolled",
            "progress_percentage",
            "lessons",
            "related_courses",
        )

    def get_is_enrolled(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return Enrollment.objects.filter(user=request.user, course=obj).exists()

    def get_progress_percentage(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return 0
        enrollment = Enrollment.objects.filter(user=request.user, course=obj).first()
        if not enrollment:
            return 0
        return enrollment.calculate_progress()

    def get_related_courses(self, obj):
        related = Course.objects.filter(
            category=obj.category,
            is_published=True
        ).exclude(id=obj.id)[:3]
        return [
            {
                "id": c.id,
                "title": c.title,
                "category": c.category,
                "level": c.level,
                "thumbnail_url": c.thumbnail_url,
            }
            for c in related
        ]


class ProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    lesson_order = serializers.IntegerField(source="lesson.order", read_only=True)

    class Meta:
        model = Progress
        fields = ("id", "lesson", "lesson_title", "lesson_order", "status", "updated_at")


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    completed_lessons_count = serializers.SerializerMethodField()
    total_lessons_count = serializers.SerializerMethodField()
    last_accessed_lesson = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = (
            "id",
            "course",
            "enrolled_at",
            "progress_percentage",
            "completed_lessons_count",
            "total_lessons_count",
            "last_accessed_lesson",
        )
        read_only_fields = ("id", "enrolled_at", "progress_percentage")

    def get_progress_percentage(self, obj):
        return obj.calculate_progress()

    def get_completed_lessons_count(self, obj):
        return obj.progress_items.filter(status="completed").count()

    def get_total_lessons_count(self, obj):
        return obj.course.lessons.count()

    def get_last_accessed_lesson(self, obj):
        recent_progress = obj.progress_items.order_by("-updated_at").first()
        if recent_progress:
            return {
                "id": recent_progress.lesson.id,
                "title": recent_progress.lesson.title,
                "order": recent_progress.lesson.order,
                "status": recent_progress.status,
            }
        first_lesson = obj.course.lessons.first()
        if first_lesson:
            return {
                "id": first_lesson.id,
                "title": first_lesson.title,
                "order": first_lesson.order,
                "status": "not_started",
            }
        return None
