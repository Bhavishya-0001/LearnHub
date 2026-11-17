from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "accounts_user"

    id = Column(BigInteger, primary_key=True, index=True)
    password = Column(String(128), nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_superuser = Column(Boolean, default=False)
    name = Column(String(120), nullable=False)
    email = Column(String(254), unique=True, index=True, nullable=False)
    role = Column(String(20), default="student", nullable=False)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    date_joined = Column(DateTime, default=datetime.utcnow)

    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses_course"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    level = Column(String(30), default="Beginner", nullable=False)
    instructor_name = Column(String(120), default="", nullable=False)
    thumbnail_url = Column(String(500), default="", nullable=False)
    duration = Column(String(50), default="8 Weeks", nullable=False)
    is_published = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan", order_by="Lesson.order")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "courses_lesson"

    id = Column(BigInteger, primary_key=True, index=True)
    course_id = Column(BigInteger, ForeignKey("courses_course.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="", nullable=False)
    content_url = Column(String(200), default="", nullable=False)
    duration = Column(String(50), default="15 mins", nullable=False)
    order = Column(Integer, default=1, nullable=False)

    course = relationship("Course", back_populates="lessons")
    progress_items = relationship("Progress", back_populates="lesson", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "courses_enrollment"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("accounts_user.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(BigInteger, ForeignKey("courses_course.id", ondelete="CASCADE"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="unique_user_course_enrollment"),
    )

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    progress_items = relationship("Progress", back_populates="enrollment", cascade="all, delete-orphan")


class Progress(Base):
    __tablename__ = "courses_progress"

    id = Column(BigInteger, primary_key=True, index=True)
    enrollment_id = Column(BigInteger, ForeignKey("courses_enrollment.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(BigInteger, ForeignKey("courses_lesson.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="not_started", nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("enrollment_id", "lesson_id", name="unique_enrollment_lesson_progress"),
    )

    enrollment = relationship("Enrollment", back_populates="progress_items")
    lesson = relationship("Lesson", back_populates="progress_items")
