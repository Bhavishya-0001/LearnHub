from django.db.models import Q, Count
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import User
from accounts.permissions import IsAdminRole, IsOwnerOrAdmin

from .models import Course, Lesson, Enrollment, Progress
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    EnrollmentSerializer,
    LessonSerializer,
    LessonAdminSerializer,
    ProgressSerializer,
)


class CourseListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminRole()]
        return [permissions.AllowAny()]

    def get(self, request):
        queryset = Course.objects.all().order_by("-id")

        # Non-admins only see published courses
        is_admin = (
            request.user.is_authenticated and
            (request.user.role == "admin" or request.user.is_staff or request.user.is_superuser)
        )
        if not is_admin:
            queryset = queryset.filter(is_published=True)
        else:
            published_param = request.query_params.get("published")
            if published_param is not None:
                queryset = queryset.filter(is_published=published_param.lower() == "true")

        # Category filter
        category = request.query_params.get("category")
        if category and category.lower() != "all":
            queryset = queryset.filter(category__iexact=category)

        # Level filter
        level = request.query_params.get("level")
        if level and level.lower() != "all":
            queryset = queryset.filter(level__iexact=level)

        # Search query
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(category__icontains=search) |
                Q(instructor_name__icontains=search)
            )

        serializer = CourseListSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CourseDetailSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        return Response(CourseDetailSerializer(course, context={"request": request}).data, status=status.HTTP_201_CREATED)


class CourseDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminRole()]
        return [permissions.AllowAny()]

    def get_object(self, pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return None

    def get(self, request, pk):
        course = self.get_object(pk)
        if not course:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = (
            request.user.is_authenticated and
            (request.user.role == "admin" or request.user.is_staff or request.user.is_superuser)
        )
        if not course.is_published and not is_admin:
            return Response({"detail": "Course is not published."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseDetailSerializer(course, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        course = self.get_object(pk)
        if not course:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CourseDetailSerializer(course, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        return Response(CourseDetailSerializer(course, context={"request": request}).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        course = self.get_object(pk)
        if not course:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        course.delete()
        return Response({"message": "Course deleted successfully."}, status=status.HTTP_200_OK)


class EnrollmentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(user=request.user).select_related("course").order_by("-enrolled_at")
        serializer = EnrollmentSerializer(enrollments, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        course_id = request.data.get("course_id")
        if not course_id:
            return Response({"detail": "course_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        if not course.is_published:
            return Response({"detail": "Cannot enroll in an unpublished course."}, status=status.HTTP_400_BAD_REQUEST)

        # Strict identification from token: request.user
        existing = Enrollment.objects.filter(user=request.user, course=course).first()
        if existing:
            return Response(
                {"detail": "You are already enrolled in this course.", "enrollment_id": existing.id},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollment = Enrollment.objects.create(user=request.user, course=course)
        serializer = EnrollmentSerializer(enrollment, context={"request": request})
        return Response(
            {
                "message": f"Successfully enrolled in {course.title}!",
                "enrollment": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class EnrollmentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            enrollment = Enrollment.objects.select_related("course", "user").get(pk=pk)
        except Enrollment.DoesNotExist:
            return Response({"detail": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND)

        # Multi-user isolation: user can only see their own enrollment unless admin
        is_admin = request.user.role == "admin" or request.user.is_staff or request.user.is_superuser
        if enrollment.user != request.user and not is_admin:
            return Response({"detail": "You do not have permission to view this enrollment."}, status=status.HTTP_403_FORBIDDEN)

        serializer = EnrollmentSerializer(enrollment, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class LessonCompleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.select_related("course").get(pk=lesson_id)
        except Lesson.DoesNotExist:
            return Response({"detail": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)

        # Find enrollment for this student
        enrollment = Enrollment.objects.filter(user=request.user, course=lesson.course).first()
        if not enrollment:
            return Response(
                {"detail": "You must be enrolled in this course to mark lessons complete."},
                status=status.HTTP_403_FORBIDDEN
            )

        progress, created = Progress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={"status": "completed"}
        )

        # Toggle or ensure completed
        action = request.data.get("action", "complete")
        if action == "toggle" and not created:
            progress.status = "not_started" if progress.status == "completed" else "completed"
            progress.save()
        else:
            progress.status = "completed"
            progress.save()

        updated_percentage = enrollment.calculate_progress()
        completed_count = enrollment.progress_items.filter(status="completed").count()
        total_lessons = lesson.course.lessons.count()

        return Response(
            {
                "message": f"Lesson marked as {progress.status}!",
                "lesson_id": lesson.id,
                "lesson_status": progress.status,
                "course_progress_percentage": updated_percentage,
                "completed_lessons_count": completed_count,
                "total_lessons_count": total_lessons,
            },
            status=status.HTTP_200_OK
        )


class UserProgressOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        enrollments = Enrollment.objects.filter(user=user).select_related("course")

        total_enrolled = enrollments.count()
        completed_courses = 0
        in_progress_courses = 0
        course_summaries = []

        for e in enrollments:
            pct = e.calculate_progress()
            if pct == 100:
                completed_courses += 1
            elif pct > 0:
                in_progress_courses += 1

            course_summaries.append({
                "enrollment_id": e.id,
                "course_id": e.course.id,
                "course_title": e.course.title,
                "category": e.course.category,
                "thumbnail_url": e.course.thumbnail_url,
                "progress_percentage": pct,
                "completed_lessons": e.progress_items.filter(status="completed").count(),
                "total_lessons": e.course.lessons.count(),
            })

        overall_progress = round(
            sum(c["progress_percentage"] for c in course_summaries) / total_enrolled
        ) if total_enrolled > 0 else 0

        return Response(
            {
                "student_name": user.name,
                "student_email": user.email,
                "total_enrolled": total_enrolled,
                "completed_courses": completed_courses,
                "in_progress_courses": in_progress_courses,
                "overall_progress": overall_progress,
                "courses": course_summaries,
            },
            status=status.HTTP_200_OK
        )


# =====================================================================
# ADMIN ENDPOINTS
# =====================================================================

class AdminStatsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        total_students = User.objects.filter(role="student").count()
        total_courses = Course.objects.count()
        published_courses = Course.objects.filter(is_published=True).count()
        unpublished_courses = Course.objects.filter(is_published=False).count()
        total_enrollments = Enrollment.objects.count()

        # Count completed enrollments (all lessons completed)
        completed_enrollments = 0
        for e in Enrollment.objects.all():
            if e.calculate_progress() == 100:
                completed_enrollments += 1

        return Response(
            {
                "total_students": total_students,
                "total_courses": total_courses,
                "published_courses": published_courses,
                "unpublished_courses": unpublished_courses,
                "total_enrollments": total_enrollments,
                "completed_enrollments": completed_enrollments,
            },
            status=status.HTTP_200_OK
        )


class AdminStudentsListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        students = User.objects.filter(role="student").order_by("-date_joined")
        data = []
        for s in students:
            enrolled = Enrollment.objects.filter(user=s)
            data.append({
                "id": s.id,
                "name": s.name,
                "email": s.email,
                "role": s.role,
                "date_joined": s.date_joined,
                "total_enrollments": enrolled.count(),
                "completed_courses": sum(1 for e in enrolled if e.calculate_progress() == 100),
            })
        return Response(data, status=status.HTTP_200_OK)


class AdminEnrollmentsListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        enrollments = Enrollment.objects.select_related("user", "course").order_by("-enrolled_at")
        data = [
            {
                "id": e.id,
                "student_id": e.user.id,
                "student_name": e.user.name,
                "student_email": e.user.email,
                "course_id": e.course.id,
                "course_title": e.course.title,
                "enrolled_at": e.enrolled_at,
                "progress_percentage": e.calculate_progress(),
            }
            for e in enrollments
        ]
        return Response(data, status=status.HTTP_200_OK)


class AdminCourseLessonsView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data["course"] = course.id
        serializer = LessonAdminSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save()
        return Response(LessonSerializer(lesson).data, status=status.HTTP_201_CREATED)


class AdminLessonDetailView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        try:
            lesson = Lesson.objects.get(pk=pk)
        except Lesson.DoesNotExist:
            return Response({"detail": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LessonAdminSerializer(lesson, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(LessonSerializer(updated).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            lesson = Lesson.objects.get(pk=pk)
        except Lesson.DoesNotExist:
            return Response({"detail": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)

        lesson.delete()
        return Response({"message": "Lesson deleted successfully."}, status=status.HTTP_200_OK)
