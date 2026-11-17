from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Course, Lesson, Enrollment, Progress, User
from ..auth import get_current_user

router = APIRouter(prefix="/progress", tags=["progress"])


class ProgressAction(BaseModel):
    action: Optional[str] = "complete"


@router.post("/lessons/{lesson_id}/complete/")
def mark_lesson_complete(
    lesson_id: int,
    payload: Optional[ProgressAction] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    # Multi-user security: verify student is enrolled in the lesson's course
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == lesson.course_id
    ).first()
    if not enrollment:
        raise HTTPException(
            status_code=403,
            detail="You must be enrolled in this course to complete its lessons."
        )

    progress = db.query(Progress).filter(
        Progress.enrollment_id == enrollment.id,
        Progress.lesson_id == lesson.id
    ).first()

    action = payload.action if payload else "complete"

    if not progress:
        progress = Progress(
            enrollment_id=enrollment.id,
            lesson_id=lesson.id,
            status="completed",
            updated_at=datetime.utcnow()
        )
        db.add(progress)
    else:
        if action == "toggle":
            progress.status = "not_started" if progress.status == "completed" else "completed"
        else:
            progress.status = "completed"
        progress.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(progress)

    # Calculate updated progress
    total_lessons = db.query(Lesson).filter(Lesson.course_id == lesson.course_id).count()
    completed_count = db.query(Progress).filter(
        Progress.enrollment_id == enrollment.id,
        Progress.status == "completed"
    ).count()

    progress_percentage = round((completed_count / total_lessons) * 100) if total_lessons > 0 else 0

    return {
        "message": f"Lesson marked as {progress.status}!",
        "lesson_id": lesson.id,
        "lesson_status": progress.status,
        "course_progress_percentage": progress_percentage,
        "completed_lessons_count": completed_count,
        "total_lessons_count": total_lessons,
    }


@router.get("/my/")
def get_user_progress_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollments = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id
    ).all()

    total_enrolled = len(enrollments)
    completed_courses = 0
    in_progress_courses = 0
    course_summaries = []

    for e in enrollments:
        course = e.course
        total_l = len(course.lessons) if course else 0
        completed_l = db.query(Progress).filter(
            Progress.enrollment_id == e.id,
            Progress.status == "completed"
        ).count()

        pct = round((completed_l / total_l) * 100) if total_l > 0 else 0
        if pct == 100:
            completed_courses += 1
        elif pct > 0:
            in_progress_courses += 1

        course_summaries.append({
            "enrollment_id": e.id,
            "course_id": course.id if course else None,
            "course_title": course.title if course else "Unknown",
            "category": course.category if course else "",
            "thumbnail_url": course.thumbnail_url if course else "",
            "progress_percentage": pct,
            "completed_lessons": completed_l,
            "total_lessons": total_l,
        })

    overall_progress = round(
        sum(c["progress_percentage"] for c in course_summaries) / total_enrolled
    ) if total_enrolled > 0 else 0

    return {
        "student_name": current_user.name,
        "student_email": current_user.email,
        "total_enrolled": total_enrolled,
        "completed_courses": completed_courses,
        "in_progress_courses": in_progress_courses,
        "overall_progress": overall_progress,
        "courses": course_summaries,
    }
