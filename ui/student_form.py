from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from typing import Optional

import ttkbootstrap as ttkb
from ttkbootstrap.dialogs import Messagebox


@dataclass
class StudentFormData:
    full_name: str
    email: str
    phone: str
    address: str
    date_of_birth: Optional[_dt.date]
    enrollment_year: Optional[int]


class StudentForm(ttkb.Toplevel):
    def __init__(self, master, title: str, initial: Optional[StudentFormData] = None):
        super().__init__(master=master)
        self.title(title)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.var_full_name = ttkb.StringVar(value=(initial.full_name if initial else ""))
        self.var_email = ttkb.StringVar(value=(initial.email if initial else ""))
        self.var_phone = ttkb.StringVar(value=(initial.phone if initial else ""))
        self.var_address = ttkb.StringVar(value=(initial.address if initial else ""))
        self.var_dob = ttkb.StringVar(value=(initial.date_of_birth.isoformat() if (initial and initial.date_of_birth) else ""))
        self.var_year = ttkb.StringVar(value=(str(initial.enrollment_year) if (initial and initial.enrollment_year is not None) else ""))

        self.result: Optional[StudentFormData] = None

        frm = ttkb.Frame(self, padding=15)
        frm.grid(row=0, column=0, sticky="nsew")

        labels = [
            ("Full name", self.var_full_name),
            ("Email", self.var_email),
            ("Phone", self.var_phone),
            ("Address", self.var_address),
            ("Date of Birth (YYYY-MM-DD)", self.var_dob),
            ("Enrollment Year", self.var_year),
        ]

        for i, (text, var) in enumerate(labels):
            ttkb.Label(frm, text=text).grid(row=i, column=0, sticky="w", pady=(0, 6))
            ttkb.Entry(frm, textvariable=var, width=40).grid(row=i, column=1, sticky="ew", pady=(0, 6))

        btns = ttkb.Frame(frm)
        btns.grid(row=len(labels), column=0, columnspan=2, pady=(10, 0), sticky="e")
        ttkb.Button(btns, text="Cancel", bootstyle="secondary", command=self._on_cancel).pack(side="right", padx=(6, 0))
        ttkb.Button(btns, text="Save", bootstyle="primary", command=self._on_save).pack(side="right")

        self.bind("<Return>", lambda e: self._on_save())
        self.bind("<Escape>", lambda e: self._on_cancel())

        self.wait_visibility()
        self.focus()

    def _on_cancel(self) -> None:
        self.result = None
        self.destroy()

    def _on_save(self) -> None:
        full_name = self.var_full_name.get().strip()
        email = self.var_email.get().strip().lower()

        if not full_name:
            Messagebox.show_error("Full name is required.")
            return
        if not email or "@" not in email:
            Messagebox.show_error("A valid email is required.")
            return

        phone = self.var_phone.get().strip()
        address = self.var_address.get().strip()

        dob_text = self.var_dob.get().strip()
        date_of_birth: Optional[_dt.date]
        if dob_text:
            try:
                date_of_birth = _dt.date.fromisoformat(dob_text)
            except ValueError:
                Messagebox.show_error("Date of birth must be YYYY-MM-DD.")
                return
        else:
            date_of_birth = None

        year_text = self.var_year.get().strip()
        enrollment_year: Optional[int]
        if year_text:
            if not year_text.isdigit():
                Messagebox.show_error("Enrollment year must be an integer.")
                return
            enrollment_year = int(year_text)
        else:
            enrollment_year = None

        self.result = StudentFormData(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            date_of_birth=date_of_birth,
            enrollment_year=enrollment_year,
        )
        self.destroy()


