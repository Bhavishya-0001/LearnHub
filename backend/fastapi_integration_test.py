"""
LearnHub FastAPI Service Verification
Tests FastAPI endpoints, database ORM queries, JWT authentication decoding,
and multi-user isolation on the live PostgreSQL database.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import jwt
from fastapi_app.database import SessionLocal
from fastapi_app.routers import courses, enrollments, progress
from fastapi_app.models import User as FUser, Course as FCourse
from fastapi_app.auth import JWT_SIGNING_KEY
from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def run_fastapi_tests():
    print("=" * 70)
    print("STARTING FASTAPI CORE SERVICES VERIFICATION")
    print("=" * 70)

    db = SessionLocal()
    try:
        # Test 1: Course listing via FastAPI router
        all_courses = courses.list_courses(db=db, current_user=None)
        assert len(all_courses) >= 15, f"Expected >= 15 courses, got {len(all_courses)}"
        print(f" -> FastAPI courses.list_courses returned {len(all_courses)} courses.")

        # Test 2: Category filtering via FastAPI router
        prog_courses = courses.list_courses(category="Programming", db=db, current_user=None)
        assert len(prog_courses) >= 1
        assert any("python" in c["title"].lower() for c in prog_courses)
        print(" -> FastAPI category filtering verified.")

        # Test 3: JWT decoding compatibility
        user_a = User.objects.filter(email="student_a_verify@learnhub.internal").first()
        assert user_a is not None
        token_a = str(RefreshToken.for_user(user_a).access_token)

        payload_a = jwt.decode(token_a, JWT_SIGNING_KEY, algorithms=["HS256"])
        assert int(payload_a["user_id"]) == user_a.id
        print(" -> FastAPI JWT decode verified (matches Django Simple JWT signing key).")

        user_b = User.objects.filter(email="student_b_verify@learnhub.internal").first()
        assert user_b is not None

        f_user_a = db.query(FUser).filter(FUser.id == user_a.id).first()
        f_user_b = db.query(FUser).filter(FUser.id == user_b.id).first()

        # Test 4: Student A enrollments via FastAPI
        enr_a = enrollments.list_my_enrollments(db=db, current_user=f_user_a)
        titles_a = [e["course"]["title"] for e in enr_a]
        print(" -> FastAPI Student A enrolled courses:", titles_a)

        # Test 5: Student B enrollments via FastAPI
        enr_b = enrollments.list_my_enrollments(db=db, current_user=f_user_b)
        titles_b = [e["course"]["title"] for e in enr_b]
        print(" -> FastAPI Student B enrolled courses:", titles_b)

        # Test 6: Verify strict multi-user isolation
        assert "Full-Stack Web Development Bootcamp" in titles_a
        assert "Full-Stack Web Development Bootcamp" not in titles_b
        print(" -> FastAPI strict multi-user isolation confirmed!")

        # Test 7: Student Progress via FastAPI
        prog_a = progress.get_user_progress_overview(db=db, current_user=f_user_a)
        prog_b = progress.get_user_progress_overview(db=db, current_user=f_user_b)

        assert prog_a["student_name"] == user_a.name
        assert prog_b["student_name"] == user_b.name
        assert prog_a["courses"][0]["progress_percentage"] > 0
        assert prog_b["courses"][0]["progress_percentage"] == 0
        print(f" -> Student A progress: {prog_a['courses'][0]['progress_percentage']}%")
        print(f" -> Student B progress: {prog_b['courses'][0]['progress_percentage']}%")
        print(" -> Multi-user progress separation confirmed in FastAPI!")

        print("\n" + "=" * 70)
        print("ALL FASTAPI CORE SERVICE VERIFICATIONS PASSED (100% SUCCESS)!")
        print("=" * 70)
    finally:
        db.close()


if __name__ == "__main__":
    run_fastapi_tests()
