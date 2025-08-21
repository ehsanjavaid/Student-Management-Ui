from __future__ import annotations

from datetime import date
from typing import Iterable, List, Optional

from sqlalchemy import select

try:
    from ..database import get_session
    from ..models import Student
except ImportError:  # Running as a script without package context
    from database import get_session
    from models import Student


def create_student(
    full_name: str,
    email: str,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    date_of_birth: Optional[date] = None,
    enrollment_year: Optional[int] = None,
) -> Student:
    with get_session() as session:
        student = Student(
            full_name=full_name.strip(),
            email=email.strip().lower(),
            phone=(phone or "").strip() or None,
            address=(address or "").strip() or None,
            date_of_birth=date_of_birth,
            enrollment_year=enrollment_year,
        )
        session.add(student)
        session.flush()
        session.refresh(student)
        return student


def get_student(student_id: int) -> Optional[Student]:
    with get_session() as session:
        return session.get(Student, student_id)


def list_students(query: str | None = None) -> List[Student]:
    with get_session() as session:
        stmt = select(Student)
        if query:
            q = f"%{query.lower()}%"
            stmt = stmt.where((Student.full_name.ilike(q)) | (Student.email.ilike(q)))
        stmt = stmt.order_by(Student.full_name.asc())
        return list(session.scalars(stmt).all())


def update_student(
    student_id: int,
    *,
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    date_of_birth: Optional[date] = None,
    enrollment_year: Optional[int] = None,
) -> Optional[Student]:
    with get_session() as session:
        student = session.get(Student, student_id)
        if not student:
            return None
        if full_name is not None:
            student.full_name = full_name.strip()
        if email is not None:
            student.email = email.strip().lower()
        if phone is not None:
            student.phone = phone.strip() or None
        if address is not None:
            student.address = address.strip() or None
        if date_of_birth is not None or date_of_birth is None:
            student.date_of_birth = date_of_birth
        if enrollment_year is not None or enrollment_year is None:
            student.enrollment_year = enrollment_year
        session.flush()
        session.refresh(student)
        return student


def delete_students(student_ids: Iterable[int]) -> int:
    ids = list(student_ids)
    if not ids:
        return 0
    with get_session() as session:
        count = 0
        for student_id in ids:
            obj = session.get(Student, student_id)
            if obj is not None:
                session.delete(obj)
                count += 1
        return count


