"""
views/pages/medications.py
"""
import tkinter as tk
from assets.styles.theme import COLORS, font
from views.pages.base import (
    ScrollableFrame, ProgressBar, TabBar, primary_btn,
    ghost_btn, danger_btn, form_label, styled_entry,
    styled_combobox, EmptyState, NoPetWidget, badge
)


class MedDialog(tk.Toplevel):
    def __init__(self, parent, pet_id, med=None, on_save=None):
        super().__init__(parent)
        self.pet_id  = pet_id
        self.med     = med
        self._on_save = on_save
        self.title("Edit Medication" if med else "Add Medication")
        self.configure(bg=COLORS["bg_card"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build()

    def _build(self):
        tk.Label(
            self,
            text="Edit Medication" if self.med else "Add Medication",
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            font=font("lg", "bold"),
        ).pack(anchor="w", padx=20, pady=(20, 8))

        row1 = tk.Frame(self, bg=COLORS["bg_card"])
        row1.pack(fill="x", padx=20, pady=(0, 8))

        n_col = tk.Frame(row1, bg=COLORS["bg_card"])
        n_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        form_label(n_col, "Name").pack(anchor="w")
        self._name_var = tk.StringVar(value=self.med.name if self.med else "")
        styled_entry(n_col, self._name_var, placeholder="e.g. Flea treatment").pack(fill="x")

        d_col = tk.Frame(row1, bg=COLORS["bg_card"])
        d_col.pack(side="left", fill="x", expand=True)
        form_label(d_col, "Dosage").pack(anchor="w")
        self._dosage_var = tk.StringVar(value=self.med.dosage or "" if self.med else "")
        styled_entry(d_col, self._dosage_var, placeholder="e.g. 1 tablet").pack(fill="x")

        row2 = tk.Frame(self, bg=COLORS["bg_card"])
        row2.pack(fill="x", padx=20, pady=(0, 8))

        f_col = tk.Frame(row2, bg=COLORS["bg_card"])
        f_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        form_label(f_col, "Frequency").pack(anchor="w")
        self._freq_var = tk.StringVar(value=self.med.frequency if self.med else "daily")
        cb = styled_combobox(
            f_col,
            ["daily","twice daily","weekly","monthly","as needed"],
            self._freq_var, width=16
        )
        cb.pack(fill="x")

        t_col = tk.Frame(row2, bg=COLORS["bg_card"])
        t_col.pack(side="left", fill="x", expand=True)
        form_label(t_col, "Reminder Time").pack(anchor="w")
        self._time_var = tk.StringVar(value=self.med.time or "08:00" if self.med else "08:00")
        styled_entry(t_col, self._time_var, placeholder="08:00", width=10).pack(fill="x")

        row3 = tk.Frame(self, bg=COLORS["bg_card"])
        row3.pack(fill="x", padx=20, pady=(0, 8))

        s_col = tk.Frame(row3, bg=COLORS["bg_card"])
        s_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        form_label(s_col, "Start Date").pack(anchor="w")
        self._start_var = tk.StringVar(value=self.med.start_date if self.med else "")
        styled_entry(s_col, self._start_var, placeholder="YYYY-MM-DD").pack(fill="x")

        e_col = tk.Frame(row3, bg=COLORS["bg_card"])
        e_col.pack(side="left", fill="x", expand=True)
        form_label(e_col, "End Date (optional)").pack(anchor="w")
        self._end_var = tk.StringVar(value=self.med.end_date or "" if self.med else "")
        styled_entry(e_col, self._end_var, placeholder="YYYY-MM-DD").pack(fill="x")

        form_label(self, "Notes").pack(anchor="w", padx=20)
        self._notes_var = tk.StringVar(value=self.med.notes or "" if self.med else "")
        styled_entry(self, self._notes_var, placeholder="Give with food…").pack(
            fill="x", padx=20, pady=(0, 12)
        )

        actions = tk.Frame(self, bg=COLORS["bg_card"])
        actions.pack(fill="x", padx=20, pady=(0, 20))
        ghost_btn(actions, "Cancel", self.destroy).pack(side="right", padx=(8,0))
        primary_btn(
            actions,
            "Save" if self.med else "Add",
            self._on_submit
        ).pack(side="right")

    def _on_submit(self):
        name = self._name_var.get().strip()
        if not name: return
        end = self._end_var.get().strip() or None
        if self._on_save:
            self._on_save({
                "pet_id":     self.pet_id,
                "name":       name,
                "dosage":     self._dosage_var.get().strip() or None,
                "frequency":  self._freq_var.get(),
                "time":       self._time_var.get().strip() or None,
                "start_date": self._start_var.get().strip(),
                "end_date":   end,
                "notes":      self._notes_var.get().strip() or None,
                "med_id":     self.med.id if self.med else None,
            })
        self.destroy()


class MedicationsPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._pet    = None
        self._today  = []
        self._all    = []
        self.cb_add_med    = None
        self.cb_edit_med   = None
        self.cb_delete_med = None
        self.cb_mark_given = None
        self.cb_skip_dose  = None
        self._build_header()
        self._content = tk.Frame(self, bg=COLORS["bg_base"])
        self._content.pack(fill="both", expand=True, padx=32)

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_base"])
        hdr.pack(fill="x", padx=32, pady=(32, 16))
        left = tk.Frame(hdr, bg=COLORS["bg_base"])
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text="Medications", bg=COLORS["bg_base"],
                 fg=COLORS["text_primary"], font=font("hero","bold"),
                 anchor="w").pack(fill="x")
        self._subtitle = tk.Label(left, text="", bg=COLORS["bg_base"],
                                  fg=COLORS["text_muted"], font=font("sm"), anchor="w")
        self._subtitle.pack(fill="x")
        primary_btn(hdr, "＋  Add Medication", self._open_add).pack(side="right", anchor="n")

    def show_no_pet(self):
        self._clear_content()
        NoPetWidget(self._content, "medications").pack(fill="both", expand=True)

    def load(self, pet, today, all_meds):
        self._pet   = pet
        self._today = today
        self._all   = all_meds
        self._subtitle.config(text=f"{pet.name}'s medication tracker")
        self._refresh()

    def _refresh(self):
        self._clear_content()
        done  = sum(1 for m in self._today if m.get("given_today"))
        total = len(self._today)
        if total:
            pb = ProgressBar(self._content, "Today's medications")
            pb.pack(fill="x", pady=(0, 16))
            pb.update_progress(done, total)

        self._stack_today = tk.Frame(self._content, bg=COLORS["bg_base"])
        self._stack_all   = tk.Frame(self._content, bg=COLORS["bg_base"])

        def on_tab(idx):
            if idx == 0:
                self._stack_today.pack(fill="both", expand=True)
                self._stack_all.pack_forget()
            else:
                self._stack_all.pack(fill="both", expand=True)
                self._stack_today.pack_forget()

        TabBar(self._content, ["Today","All Medications"], on_change=on_tab).pack(fill="x", pady=(0,12))
        self._build_today()
        self._build_all()
        self._stack_today.pack(fill="both", expand=True)

    def _build_today(self):
        sf = ScrollableFrame(self._stack_today, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame
        if not self._today:
            EmptyState(f, "💊", "No medications today").pack(fill="both", expand=True, pady=40)
            return
        for m in self._today:
            row = tk.Frame(f, bg=COLORS["bg_card"], pady=12, padx=14)
            row.pack(fill="x", pady=(0,6))
            done = m.get("given_today", False)
            cb = tk.Button(row, text="✓" if done else "○",
                bg=COLORS["accent_sage"] if done else COLORS["bg_elevated"],
                fg="white" if done else COLORS["text_muted"],
                font=font("base","bold"), relief="flat", bd=0, width=3,
                cursor="hand2" if not done else "arrow")
            cb.pack(side="left", padx=(0,12))
            if not done:
                cb.config(command=lambda mid=m["id"]: self.cb_mark_given and self.cb_mark_given(mid))
            info = tk.Frame(row, bg=COLORS["bg_card"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=m["name"], bg=COLORS["bg_card"],
                     fg=COLORS["text_primary"], font=font("base","bold"), anchor="w").pack(fill="x")
            parts = [p for p in [m.get("dosage"), m.get("frequency"), m.get("time")] if p]
            tk.Label(info, text=" · ".join(parts), bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"], font=font("sm"), anchor="w").pack(fill="x")
            acts = tk.Frame(row, bg=COLORS["bg_card"])
            acts.pack(side="right")
            if not done:
                ghost_btn(acts, "Skip", command=lambda mn=m["name"], mid=m["id"]: self._skip(mid, mn)).pack()
            else:
                tk.Label(acts, text="Given", bg=COLORS["badge_done_bg"],
                         fg=COLORS["badge_done_fg"], font=font("xs","bold"), padx=8, pady=3).pack()

    def _build_all(self):
        sf = ScrollableFrame(self._stack_all, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame
        if not self._all:
            EmptyState(f, "💊", "No medications added yet").pack(fill="both", expand=True, pady=40)
            return
        for m in self._all:
            row = tk.Frame(f, bg=COLORS["bg_card"], pady=12, padx=14)
            row.pack(fill="x", pady=(0,6))
            dot_color = COLORS["accent_sage"] if m.active else COLORS["text_muted"]
            tk.Label(row, text="●", bg=COLORS["bg_card"], fg=dot_color, font=font("xs")).pack(side="left", padx=(0,10))
            info = tk.Frame(row, bg=COLORS["bg_card"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=m.name, bg=COLORS["bg_card"],
                     fg=COLORS["text_primary"], font=font("base","bold"), anchor="w").pack(fill="x")
            parts = [p for p in [m.dosage, m.frequency, m.end_date and f"Until {m.end_date}"] if p]
            tk.Label(info, text=" · ".join(parts), bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"], font=font("sm"), anchor="w").pack(fill="x")
            acts = tk.Frame(row, bg=COLORS["bg_card"])
            acts.pack(side="right")
            ghost_btn(acts, "Edit", command=lambda med=m: self._open_edit(med)).pack(side="left", padx=(0,4))
            ghost_btn(acts, "✕", command=lambda mid=m.id: self.cb_delete_med and self.cb_delete_med(mid)).pack(side="left")

    def _skip(self, med_id, med_name):
        dlg = tk.Toplevel(self)
        dlg.title("Skip Dose")
        dlg.configure(bg=COLORS["bg_card"])
        dlg.grab_set()
        dlg.transient(self)
        tk.Label(dlg, text=f"Skip dose of {med_name}?", bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"], font=font("md","bold")).pack(padx=20, pady=(20,8))
        form_label(dlg, "Reason (optional)").pack(anchor="w", padx=20)
        reason_var = tk.StringVar()
        styled_entry(dlg, reason_var, placeholder="Pet refused…").pack(fill="x", padx=20, pady=(0,12))
        acts = tk.Frame(dlg, bg=COLORS["bg_card"])
        acts.pack(fill="x", padx=20, pady=(0,20))
        ghost_btn(acts, "Cancel", dlg.destroy).pack(side="right", padx=(8,0))
        def do_skip():
            if self.cb_skip_dose: self.cb_skip_dose(med_id, reason_var.get())
            dlg.destroy()
        danger_btn(acts, "Skip Dose", do_skip).pack(side="right")

    def _open_add(self):
        if not self._pet: return
        MedDialog(self, self._pet.id,
                  on_save=lambda d: self.cb_add_med and self.cb_add_med(d))

    def _open_edit(self, med):
        MedDialog(self, self._pet.id, med=med,
                  on_save=lambda d: self.cb_edit_med and self.cb_edit_med(d))

    def _clear_content(self):
        for w in self._content.winfo_children(): w.destroy()