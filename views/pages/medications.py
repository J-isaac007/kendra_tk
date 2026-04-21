"""
views/pages/medications.py — Kendra Pro
"""
import tkinter as tk
from assets.styles.theme import COLORS, font
from views.pages.base import (
    ScrollableFrame, ProgressBar, TabBar,
    primary_btn, ghost_btn, danger_btn,
    form_label, styled_entry, styled_combobox,
    EmptyState, NoPetWidget, check_btn, page_header
)


class MedDialog(tk.Toplevel):
    def __init__(self, parent, pet_id, med=None, on_save=None):
        super().__init__(parent)
        self.pet_id = pet_id
        self.med = med
        self._on_save = on_save
        self.title("Edit Medication" if med else "Add Medication")
        self.configure(bg=COLORS["bg_surface"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build()

    def _build(self):
        bg = COLORS["bg_surface"]
        tk.Label(self, text="Edit Medication" if self.med else "Add Medication",
                 bg=bg, fg=COLORS["text_primary"],
                 font=font("lg", "bold")).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 16))

        row1 = tk.Frame(self, bg=bg)
        row1.pack(fill="x", padx=24, pady=(0, 12))

        n = tk.Frame(row1, bg=bg)
        n.pack(side="left", fill="x", expand=True, padx=(0, 12))
        form_label(n, "Name", bg=bg).pack(anchor="w")
        self._name_f = styled_entry(n, placeholder="Flea treatment", bg=bg)
        self._name_f.pack(fill="x", pady=(4, 0))
        if self.med and self.med.name: self._name_f.set(self.med.name)

        d = tk.Frame(row1, bg=bg)
        d.pack(side="left", fill="x", expand=True)
        form_label(d, "Dosage", bg=bg).pack(anchor="w")
        self._dosage_f = styled_entry(d, placeholder="1 tablet", bg=bg)
        self._dosage_f.pack(fill="x", pady=(4, 0))
        if self.med and self.med.dosage: self._dosage_f.set(self.med.dosage)

        row2 = tk.Frame(self, bg=bg)
        row2.pack(fill="x", padx=24, pady=(0, 12))

        f = tk.Frame(row2, bg=bg)
        f.pack(side="left", fill="x", expand=True, padx=(0, 12))
        form_label(f, "Frequency", bg=bg).pack(anchor="w")
        self._freq_var = tk.StringVar(value=self.med.frequency if self.med else "daily")
        styled_combobox(f, ["daily","twice daily","weekly","monthly","as needed"],
                        self._freq_var, width=16).pack(fill="x", pady=(4, 0))

        t = tk.Frame(row2, bg=bg)
        t.pack(side="left", fill="x", expand=True)
        form_label(t, "Time", bg=bg).pack(anchor="w")
        self._time_f = styled_entry(t, placeholder="08:00", width=10, bg=bg)
        self._time_f.pack(fill="x", pady=(4, 0))
        if self.med and self.med.time: self._time_f.set(self.med.time)

        row3 = tk.Frame(self, bg=bg)
        row3.pack(fill="x", padx=24, pady=(0, 12))

        s = tk.Frame(row3, bg=bg)
        s.pack(side="left", fill="x", expand=True, padx=(0, 12))
        form_label(s, "Start Date", bg=bg).pack(anchor="w")
        self._start_f = styled_entry(s, placeholder="YYYY-MM-DD", bg=bg)
        self._start_f.pack(fill="x", pady=(4, 0))
        if self.med and self.med.start_date: self._start_f.set(self.med.start_date)

        e = tk.Frame(row3, bg=bg)
        e.pack(side="left", fill="x", expand=True)
        form_label(e, "End Date (optional)", bg=bg).pack(anchor="w")
        self._end_f = styled_entry(e, placeholder="YYYY-MM-DD", bg=bg)
        self._end_f.pack(fill="x", pady=(4, 0))
        if self.med and self.med.end_date: self._end_f.set(self.med.end_date)

        form_label(self, "Notes", bg=bg).pack(anchor="w", padx=24)
        self._notes_f = styled_entry(self, placeholder="Give with food…", bg=bg)
        self._notes_f.pack(fill="x", padx=24, pady=(4, 16))
        if self.med and self.med.notes: self._notes_f.set(self.med.notes)

        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 12))
        acts = tk.Frame(self, bg=bg)
        acts.pack(fill="x", padx=24, pady=(0, 20))
        ghost_btn(acts, "Cancel", self.destroy).pack(side="right", padx=(8, 0))
        primary_btn(acts, "Save" if self.med else "Add", self._submit).pack(side="right")

    def _submit(self):
        name = self._name_f.get().strip()
        if not name: return
        if self._on_save:
            self._on_save({
                "pet_id": self.pet_id,
                "name": name,
                "dosage": self._dosage_f.get().strip() or None,
                "frequency": self._freq_var.get(),
                "time": self._time_f.get().strip() or None,
                "start_date": self._start_f.get().strip(),
                "end_date": self._end_f.get().strip() or None,
                "notes": self._notes_f.get().strip() or None,
                "med_id": self.med.id if self.med else None,
            })
        self.destroy()


class MedicationsPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._pet = None
        self._today = []
        self._all = []
        self.cb_mark_given = None
        self.cb_skip_dose = None
        self.cb_add_med = None
        self.cb_edit_med = None
        self.cb_delete_med = None

        self._hdr = page_header(self, "Medications", action_text="＋  Add Medication",
                                action_cmd=self._open_add)
        self._hdr.pack(fill="x", padx=32, pady=(28, 0))
        self._subtitle = tk.Label(self, text="", bg=COLORS["bg_base"],
                                  fg=COLORS["text_secondary"], font=font("sm"), anchor="w")
        self._subtitle.pack(fill="x", padx=32, pady=(2, 16))

        self._content = tk.Frame(self, bg=COLORS["bg_base"])
        self._content.pack(fill="both", expand=True, padx=32, pady=(0, 24))

    def show_no_pet(self):
        self._clear()
        NoPetWidget(self._content, "medications").pack(fill="both", expand=True)

    def load(self, pet, today, all_meds):
        self._pet = pet
        self._today = today
        self._all = all_meds
        self._subtitle.config(text=f"{pet.name}'s medication tracker")
        self._refresh()

    def _refresh(self):
        self._clear()
        done = sum(1 for m in self._today if m.get("given_today"))
        total = len(self._today)
        if total:
            pb = ProgressBar(self._content, "Today's medications", bg=COLORS["bg_base"])
            pb.pack(fill="x", pady=(0, 16))
            pb.update_progress(done, total)

        self._tab_today = tk.Frame(self._content, bg=COLORS["bg_base"])
        self._tab_all   = tk.Frame(self._content, bg=COLORS["bg_base"])

        def switch(idx):
            if idx == 0:
                self._tab_today.pack(fill="both", expand=True)
                self._tab_all.pack_forget()
            else:
                self._tab_all.pack(fill="both", expand=True)
                self._tab_today.pack_forget()

        TabBar(self._content, ["Today", "All Medications"],
               on_change=switch).pack(fill="x", pady=(0, 12))
        self._build_today()
        self._build_all()
        self._tab_today.pack(fill="both", expand=True)

    def _build_today(self):
        sf = ScrollableFrame(self._tab_today, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame
        if not self._today:
            EmptyState(f, "💊", "No medications due today",
                       bg=COLORS["bg_base"]).pack(fill="both", expand=True, pady=40)
            return
        for m in self._today:
            done = m.get("given_today", False)
            row = tk.Frame(f, bg=COLORS["bg_surface"])
            row.pack(fill="x", pady=(0, 1))
            accent = COLORS["accent_green"] if done else COLORS["accent_purple"]
            tk.Frame(row, bg=accent, width=3).pack(side="left", fill="y")
            inner = tk.Frame(row, bg=COLORS["bg_surface"], padx=14, pady=10)
            inner.pack(side="left", fill="both", expand=True)

            cb = check_btn(inner, done,
                           command=lambda mid=m["id"]: self.cb_mark_given and self.cb_mark_given(mid),
                           bg=COLORS["bg_surface"])
            cb.pack(side="left", padx=(0, 12))

            info = tk.Frame(inner, bg=COLORS["bg_surface"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=m["name"], bg=COLORS["bg_surface"],
                     fg=COLORS["text_primary"], font=font("sm", "bold"),
                     anchor="w").pack(fill="x")
            parts = [p for p in [m.get("dosage"), m.get("frequency"), m.get("time")] if p]
            tk.Label(info, text="  ·  ".join(parts), bg=COLORS["bg_surface"],
                     fg=COLORS["text_muted"], font=font("xs"), anchor="w").pack(fill="x")

            acts = tk.Frame(inner, bg=COLORS["bg_surface"])
            acts.pack(side="right")
            if done:
                tk.Label(acts, text="Given ✓", bg=COLORS["bg_surface"],
                         fg=COLORS["accent_green"], font=font("xs", "bold")).pack()
            else:
                ghost_btn(acts, "Skip",
                          command=lambda mn=m["name"], mid=m["id"]: self._skip(mid, mn)).pack()

    def _build_all(self):
        sf = ScrollableFrame(self._tab_all, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame
        if not self._all:
            EmptyState(f, "💊", "No medications added yet",
                       bg=COLORS["bg_base"]).pack(fill="both", expand=True, pady=40)
            return
        for m in self._all:
            row = tk.Frame(f, bg=COLORS["bg_surface"])
            row.pack(fill="x", pady=(0, 1))
            accent = COLORS["accent_green"] if m.active else COLORS["text_muted"]
            tk.Frame(row, bg=accent, width=3).pack(side="left", fill="y")
            inner = tk.Frame(row, bg=COLORS["bg_surface"], padx=14, pady=10)
            inner.pack(side="left", fill="both", expand=True)

            info = tk.Frame(inner, bg=COLORS["bg_surface"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=m.name, bg=COLORS["bg_surface"],
                     fg=COLORS["text_primary"], font=font("sm", "bold"),
                     anchor="w").pack(fill="x")
            parts = [p for p in [m.dosage, m.frequency,
                                  m.end_date and f"Until {m.end_date}"] if p]
            tk.Label(info, text="  ·  ".join(parts), bg=COLORS["bg_surface"],
                     fg=COLORS["text_muted"], font=font("xs"), anchor="w").pack(fill="x")

            acts = tk.Frame(inner, bg=COLORS["bg_surface"])
            acts.pack(side="right")
            ghost_btn(acts, "Edit",
                      command=lambda med=m: self._open_edit(med)).pack(side="left", padx=(0, 4))
            ghost_btn(acts, "✕",
                      command=lambda mid=m.id: self.cb_delete_med and self.cb_delete_med(mid),
                      fg=COLORS["accent_red"]).pack(side="left")

    def _skip(self, med_id, med_name):
        dlg = tk.Toplevel(self)
        dlg.title("Skip Dose")
        dlg.configure(bg=COLORS["bg_surface"])
        dlg.grab_set()
        dlg.transient(self)
        bg = COLORS["bg_surface"]
        tk.Label(dlg, text=f"Skip dose of {med_name}?", bg=bg,
                 fg=COLORS["text_primary"], font=font("md", "bold")).pack(padx=24, pady=(20, 4))
        tk.Frame(dlg, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 12))
        form_label(dlg, "Reason (optional)", bg=bg).pack(anchor="w", padx=24)
        reason_f = styled_entry(dlg, placeholder="Pet refused, out of medication…", bg=bg)
        reason_f.pack(fill="x", padx=24, pady=(4, 16))
        acts = tk.Frame(dlg, bg=bg)
        acts.pack(fill="x", padx=24, pady=(0, 20))
        ghost_btn(acts, "Cancel", dlg.destroy).pack(side="right", padx=(8, 0))
        def do_skip():
            if self.cb_skip_dose: self.cb_skip_dose(med_id, reason_f.get())
            dlg.destroy()
        danger_btn(acts, "Skip Dose", do_skip).pack(side="right")

    def _open_add(self):
        if not self._pet: return
        MedDialog(self, self._pet.id,
                  on_save=lambda d: self.cb_add_med and self.cb_add_med(d))

    def _open_edit(self, med):
        MedDialog(self, self._pet.id, med=med,
                  on_save=lambda d: self.cb_edit_med and self.cb_edit_med(d))

    def _clear(self):
        for w in self._content.winfo_children(): w.destroy()