from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Course, Enrollment, Progress, User
from ..auth import get_current_user

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


class EnrollmentCreate(BaseModel):
    course_id: int


def serialize_enrollment(enrollment: Enrollment, db: Session):
    course = enrollment.course
    total_lessons = len(course.lessons) if course else 0
    completed_count = db.query(Progress).filter(
        Progress.enrollment_id == enrollment.id,
        Progress.status == "completed"
    ).count()

    progress_pct = round((completed_count / total_lessons) * 100) if total_lessons > 0 else 0

    recent = db.query(Progress).filter(
        Progress.enrollment_id == enrollment.id
    ).order_by(Progress.updated_at.desc()).first()

    last_lesson = None
    if recent and recent.lesson:
        last_lesson = {
            "id": recent.lesson.id,
            "title": recent.lesson.title,
            "order": recent.lesson.order,
            "status": recent.status,
        }
    elif course and course.lessons:
        first_l = course.lessons[0]
        last_lesson = {
            "id": first_l.id,
            "title": first_l.title,
            "order": first_l.order,
            "status": "not_started",
        }

    return {
        "id": enrollment.id,
        "enrolled_at": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
        "progress_percentage": progress_pct,
        "completed_lessons_count": completed_count,
        "total_lessons_count": total_lessons,
        "last_accessed_lesson": last_lesson,
        "course": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "category": course.category,
            "level": course.level,
            "instructor_name": course.instructor_name,
            "thumbnail_url": course.thumbnail_url,
            "duration": course.duration,
            "is_published": course.is_published,
            "lessons_count": total_lessons,
        } if course else None,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_enrollment(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    if not course.is_published:
        raise HTTPException(status_code=400, detail="Cannot enroll in an unpublished course.")

    # Prevent duplicate enrollment for this authenticated student
    existing = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="You are already enrolled in this course.",
        )

    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course.id,
        enrolled_at=datetime.utcnow(),
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return {
        "message": f"Successfully enrolled in {course.title}!",
        "enrollment": serialize_enrollment(enrollment, db),
    }


@router.get("/my/")
def list_my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Strict multi-user isolation: only retrieve current_user.id enrollments
    enrollments = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id
    ).order_by(Enrollment.enrolled_at.desc()).all()

    return [serialize_enrollment(e, db) for e in enrollments]


@router.get("/{enrollment_id}")
def get_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found.")

    # Isolation check: only owner or admin can view
    is_admin = current_user.role == "admin" or current_user.is_staff
    if enrollment.user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="You do not have permission to view this enrollment.")

    return serialize_enrollment(enrollment, db)
