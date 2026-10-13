"""Key-field construction and access for CryptoEdu Pro."""

import customtkinter as ctk

from core.registry import get_algorithm


class KeyFieldsMixin:
    def update_keys(self):
        T = self._T
        for index in range(1, 5):
            setattr(self, f"key{index}", None)
        for widget in self.key_frame.winfo_children():
            widget.destroy()

        t = self.language_manager.current
        entry_style = {
            "font": ("Segoe UI", 14),
            "fg_color": T["BG_INPUT"],
            "border_width": 2,
            "border_color": T["BORDER_COLOR"],
            "corner_radius": 8,
        }
        label_style = {"font": ("Segoe UI", 14, "bold"), "text_color": T["TEXT_LIGHT"]}

        for index, field in enumerate(get_algorithm(self.current_cipher).key_fields, start=1):
            label = t.get(field.label_key, field.name)
            ctk.CTkLabel(self.key_frame, text=f"{label}:", **label_style).pack(
                side="left", padx=(10 if index == 1 else 5, 2)
            )
            entry = ctk.CTkEntry(
                self.key_frame,
                width=field.width,
                placeholder_text=field.placeholder,
                **entry_style,
            )
            entry.insert(0, field.default)
            entry.pack(side="left", padx=5)
            setattr(self, f"key{index}", entry)
            if field.note:
                note = field.note
                if note.startswith("(") and self.language_manager.is_rtl:
                    note = self._fb(note)
                ctk.CTkLabel(
                    self.key_frame,
                    text=note,
                    font=("Segoe UI", 11),
                    text_color=T["TEXT_MUTED"],
                ).pack(side="left", padx=5)

    def get_key_values(self):
        """Return current key-field values without exposing widget details to callers."""
        return tuple(
            field.get() if field is not None else ""
            for field in (getattr(self, f"key{index}", None) for index in range(1, 5))
        )
