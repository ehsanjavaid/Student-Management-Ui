from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional

import ttkbootstrap as ttkb
from ttkbootstrap.constants import BOTH, LEFT, RIGHT, X, Y, YES, NO
from ttkbootstrap.dialogs import Messagebox

try:
    from ..config import load_settings, save_settings
    from ..services.student_service import (
        create_student,
        list_students,
        update_student,
        delete_students,
    )
except ImportError:  # Running as a script without package context
    from config import load_settings, save_settings
    from services.student_service import (
        create_student,
        list_students,
        update_student,
        delete_students,
    )
from .student_form import StudentForm, StudentFormData


class StudentManagementApp(ttkb.Window):
    def __init__(self, theme_name: str = "flatly"):
        super().__init__(themename=theme_name)
        self.title("Student Management System")

        self.settings = load_settings()
        geometry = self.settings.get("geometry", "1024x640")
        self.geometry(geometry)
        if self.settings.get("zoomed"):
            try:
                self.state('zoomed')
            except Exception:
                pass

        self._build_toolbar()
        self._build_table()
        self._refresh_table()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_toolbar(self) -> None:
        bar = ttkb.Frame(self, padding=(10, 8))
        bar.pack(fill=X)

        self.search_var = ttkb.StringVar()
        ttkb.Entry(bar, textvariable=self.search_var, width=40).pack(side=LEFT, padx=(0, 8))
        ttkb.Button(bar, text="Search", bootstyle="secondary", command=self._on_search).pack(side=LEFT, padx=(0, 8))
        ttkb.Button(bar, text="Add", bootstyle="success", command=self._on_add).pack(side=LEFT)
        ttkb.Button(bar, text="Edit", bootstyle="warning", command=self._on_edit).pack(side=LEFT, padx=(8, 0))
        ttkb.Button(bar, text="Delete", bootstyle="danger", command=self._on_delete).pack(side=LEFT, padx=(8, 0))

        bar2 = ttkb.Frame(self)
        bar2.pack(fill=X)
        ttkb.Button(bar2, text="Import CSV", bootstyle="info", command=self._on_import).pack(side=LEFT)
        ttkb.Button(bar2, text="Export CSV", bootstyle="info", command=self._on_export).pack(side=LEFT, padx=(8, 0))

        ttkb.Button(bar2, text="Toggle Theme", bootstyle="secondary", command=self._on_toggle_theme).pack(side=RIGHT)

    def _build_table(self) -> None:
        columns = ("id", "full_name", "email", "phone", "address", "date_of_birth", "enrollment_year")
        tree = ttkb.Treeview(self, columns=columns, show="headings", height=20, bootstyle="table")
        self.tree = tree
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, anchor="w", width=140 if col != "address" else 240)
        tree.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        tree.bind("<Double-1>", lambda e: self._on_edit())

    def _refresh_table(self, query: Optional[str] = None) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)
        students = list_students(query=query)
        for s in students:
            self.tree.insert("", "end", iid=str(s.id), values=(
                s.id,
                s.full_name,
                s.email,
                s.phone or "",
                s.address or "",
                s.date_of_birth.isoformat() if s.date_of_birth else "",
                s.enrollment_year if s.enrollment_year is not None else "",
            ))

    def _get_selected_ids(self) -> List[int]:
        sel = self.tree.selection()
        return [int(s) for s in sel]

    def _on_search(self) -> None:
        self._refresh_table(self.search_var.get().strip() or None)

    def _on_add(self) -> None:
        dialog = StudentForm(self, "Add Student")
        self.wait_window(dialog)
        if dialog.result:
            data = dialog.result
            create_student(
                full_name=data.full_name,
                email=data.email,
                phone=data.phone or None,
                address=data.address or None,
                date_of_birth=data.date_of_birth,
                enrollment_year=data.enrollment_year,
            )
            self._refresh_table(self.search_var.get().strip() or None)

    def _on_edit(self) -> None:
        ids = self._get_selected_ids()
        if not ids:
            Messagebox.show_info("Please select a row to edit.")
            return
        if len(ids) > 1:
            Messagebox.show_info("Please select only one row to edit.")
            return
        row_id = ids[0]
        item = self.tree.item(str(row_id))
        values = item.get("values", [])
        initial = StudentFormData(
            full_name=values[1] or "",
            email=values[2] or "",
            phone=values[3] or "",
            address=values[4] or "",
            date_of_birth=(None if not values[5] else None),  # show as text only
            enrollment_year=(None if values[6] == "" else int(values[6])),
        )
        dialog = StudentForm(self, "Edit Student", initial=initial)
        self.wait_window(dialog)
        if dialog.result:
            data = dialog.result
            update_student(
                row_id,
                full_name=data.full_name,
                email=data.email,
                phone=data.phone or None,
                address=data.address or None,
                date_of_birth=data.date_of_birth,
                enrollment_year=data.enrollment_year,
            )
            self._refresh_table(self.search_var.get().strip() or None)

    def _on_delete(self) -> None:
        ids = self._get_selected_ids()
        if not ids:
            Messagebox.show_info("Please select at least one row to delete.")
            return
        if Messagebox.okcancel("Delete selected students? This cannot be undone.") == "OK":
            delete_students(ids)
            self._refresh_table(self.search_var.get().strip() or None)

    def _on_import(self) -> None:
        from tkinter import filedialog

        path = filedialog.askopenfilename(
            title="Import Students CSV",
            filetypes=[["CSV Files", "*.csv"], ["All Files", "*.*"]],
        )
        if not path:
            return
        created = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                full_name = (row.get("full_name") or row.get("name") or "").strip()
                email = (row.get("email") or "").strip()
                phone = (row.get("phone") or "").strip() or None
                address = (row.get("address") or "").strip() or None
                dob = (row.get("date_of_birth") or row.get("dob") or "").strip()
                enrollment_year = (row.get("enrollment_year") or row.get("year") or "").strip()
                from datetime import date
                dob_value = None
                if dob:
                    try:
                        dob_value = date.fromisoformat(dob)
                    except ValueError:
                        dob_value = None
                year_val = int(enrollment_year) if enrollment_year.isdigit() else None

                if full_name and email and "@" in email:
                    try:
                        create_student(full_name, email, phone, address, dob_value, year_val)
                        created += 1
                    except Exception:
                        pass
        Messagebox.show_info(f"Imported {created} students.")
        self._refresh_table(self.search_var.get().strip() or None)

    def _on_export(self) -> None:
        from tkinter import filedialog

        path = filedialog.asksaveasfilename(
            title="Export Students CSV",
            defaultextension=".csv",
            filetypes=[["CSV Files", "*.csv"], ["All Files", "*.*"]],
        )
        if not path:
            return
        students = list_students(query=self.search_var.get().strip() or None)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "id",
                    "full_name",
                    "email",
                    "phone",
                    "address",
                    "date_of_birth",
                    "enrollment_year",
                ],
            )
            writer.writeheader()
            for s in students:
                writer.writerow({
                    "id": s.id,
                    "full_name": s.full_name,
                    "email": s.email,
                    "phone": s.phone or "",
                    "address": s.address or "",
                    "date_of_birth": s.date_of_birth.isoformat() if s.date_of_birth else "",
                    "enrollment_year": s.enrollment_year if s.enrollment_year is not None else "",
                })
        Messagebox.show_info(f"Exported {len(students)} students.")

    def _on_toggle_theme(self) -> None:
        current = self.style.theme.name
        alt = "darkly" if current != "darkly" else "flatly"
        self.style.theme_use(alt)
        self.settings["theme"] = alt
        save_settings(self.settings)

    def _on_close(self) -> None:
        try:
            self.settings["geometry"] = self.winfo_geometry()
            self.settings["zoomed"] = (self.state() == 'zoomed')
            save_settings(self.settings)
        finally:
            self.destroy()


