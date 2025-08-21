from __future__ import annotations

from datetime import date
from typing import Dict, Any

from sqlalchemy import Integer, String, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

try:
    from .database import Base
except ImportError:  # Running as a script without package context
    from database import Base


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("email", name="uq_students_email"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    enrollment_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone or "",
            "address": self.address or "",
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else "",
            "enrollment_year": self.enrollment_year if self.enrollment_year is not None else "",
        }

    def __repr__(self) -> str:  # pragma: no cover - debug helper only
        return f"<Student id={self.id} name={self.full_name!r} email={self.email!r}>"


