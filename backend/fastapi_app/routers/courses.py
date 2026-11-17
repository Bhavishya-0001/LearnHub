from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from ..models import Course, Lesson, Enrollment, Progress, User
from ..auth import get_optional_user

router = APIRouter(prefix="/courses", tags=["courses"])


def serialize_course_list(course: Course, user: Optional[User], db: Session):
    is_enrolled = False
    progress_percentage = 0
    if user:
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == user.id,
            Enrollment.course_id == course.id
        ).first()
        if enrollment:
            is_enrolled = True
            total = len(course.lessons)
            completed = db.query(Progress).filter(
                Progress.enrollment_id == enrollment.id,
                Progress.status == "completed"
            ).count()
            progress_percentage = round((completed / total) * 100) if total > 0 else 0

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "category": course.category,
        "level": course.level,
        "instructor_name": course.instructor_name,
        "thumbnail_url": course.thumbnail_url,
        "duration": course.duration,
        "is_published": course.is_published,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "lessons_count": len(course.lessons),
        "is_enrolled": is_enrolled,
        "progress_percentage": progress_percentage,
    }


@router.get("/")
def list_courses(
    category: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    query = db.query(Course)

    # Published check for non-admins
    is_admin = current_user and (current_user.role == "admin" or current_user.is_staff)
    if not is_admin:
        query = query.filter(Course.is_published == True)

    if category and category.lower() != "all":
        query = query.filter(Course.category.ilike(category))

    if level and level.lower() != "all":
        query = query.filter(Course.level.ilike(level))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Course.title.ilike(search_pattern),
                Course.description.ilike(search_pattern),
                Course.category.ilike(search_pattern),
                Course.instructor_name.ilike(search_pattern),
            )
        )

    courses = query.order_by(Course.id.desc()).all()
    return [serialize_course_list(c, current_user, db) for c in courses]


@router.get("/{course_id}")
def get_course_detail(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    is_admin = current_user and (current_user.role == "admin" or current_user.is_staff)
    if not course.is_published and not is_admin:
        raise HTTPException(status_code=404, detail="Course is not published.")

    # Determine user enrollment and lesson completion
    is_enrolled = False
    progress_percentage = 0
    completed_lesson_ids = set()

    if current_user:
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course.id
        ).first()
        if enrollment:
            is_enrolled = True
            completed_records = db.query(Progress.lesson_id).filter(
                Progress.enrollment_id == enrollment.id,
                Progress.status == "completed"
            ).all()
            completed_lesson_ids = {r[0] for r in completed_records}
            total = len(course.lessons)
            progress_percentage = round((len(completed_lesson_ids) / total) * 100) if total > 0 else 0

    serialized_lessons = [
        {
            "id": l.id,
            "course": l.course_id,
            "title": l.title,
            "description": l.description,
            "content_url": l.content_url,
            "duration": l.duration,
            "order": l.order,
            "is_completed": l.id in completed_lesson_ids,
        }
        for l in course.lessons
    ]

    # Related courses in same category
    related = db.query(Course).filter(
        Course.category == course.category,
        Course.is_published == True,
        Course.id != course.id,
    ).limit(3).all()

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "category": course.category,
        "level": course.level,
        "instructor_name": course.instructor_name,
        "thumbnail_url": course.thumbnail_url,
        "duration": course.duration,
        "is_published": course.is_published,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "lessons_count": len(course.lessons),
        "is_enrolled": is_enrolled,
        "progress_percentage": progress_percentage,
        "lessons": serialized_lessons,
        "related_courses": [
            {
                "id": r.id,
                "title": r.title,
                "category": r.category,
                "level": r.level,
                "thumbnail_url": r.thumbnail_url,
            }
            for r in related
        ],
    }
