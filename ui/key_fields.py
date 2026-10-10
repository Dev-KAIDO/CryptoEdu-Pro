"""Key-field construction and access for CryptoEdu Pro."""

import customtkinter as ctk

from ui.translations import TRANSLATIONS


class KeyFieldsMixin:
    def update_keys(self):
        T = self._T
        # إزالة مراجع الحقول القديمة قبل إعادة بناء حقول الخوارزمية الجديدة.
        # وجود مرجع Tkinter قديم يجعل hasattr ينجح رغم أن العنصر دُمّر فعليًا.
        for index in range(1, 5):
            setattr(self, f"key{index}", None)
        for widget in self.key_frame.winfo_children():
            widget.destroy()

        t = TRANSLATIONS[self.lang]

        entry_style = {
            "font": ("Segoe UI", 14),
            "fg_color": T["BG_INPUT"],
            "border_width": 2,
            "border_color": T["BORDER_COLOR"],
            "corner_radius": 8
        }

        label_style = {
            "font": ("Segoe UI", 14, "bold"),
            "text_color": T["TEXT_LIGHT"]
        }

        if self.current_cipher == "Caesar":
            ctk.CTkLabel(self.key_frame, text=t["key"] + ":", **label_style).pack(side="left", padx=10)
            self.key1 = ctk.CTkEntry(self.key_frame, width=100, **entry_style)
            self.key1.insert(0, "3")
            self.key1.pack(side="left", padx=5)
            ctk.CTkLabel(self.key_frame, text="(1-25)", font=("Segoe UI", 11), text_color=T["TEXT_MUTED"]).pack(side="left", padx=5)

        elif self.current_cipher == "Affine":
            ctk.CTkLabel(self.key_frame, text=t["key_m"] + ":", **label_style).pack(side="left", padx=10)
            self.key1 = ctk.CTkEntry(self.key_frame, width=80, **entry_style)
            self.key1.insert(0, "7")
            self.key1.pack(side="left", padx=5)

            ctk.CTkLabel(self.key_frame, text=t["key_k"] + ":", **label_style).pack(side="left", padx=10)
            self.key2 = ctk.CTkEntry(self.key_frame, width=80, **entry_style)
            self.key2.insert(0, "10")
            self.key2.pack(side="left", padx=5)

        elif self.current_cipher == "Hill":
            ctk.CTkLabel(self.key_frame, text=t["key"] + ":", **label_style).pack(side="left", padx=10)
            self.key1 = ctk.CTkEntry(self.key_frame, width=200, placeholder_text="HILL \u0644\u0627 3,2,5,7", **entry_style)
            self.key1.insert(0, "HILL")
            self.key1.pack(side="left", padx=5)
            ctk.CTkLabel(self.key_frame, text="(4 \u062d\u0631\u0648\u0641 \u0623\u0648 4 \u0623\u0631\u0642\u0627\u0645)", font=("Segoe UI", 11), text_color=T["TEXT_MUTED"]).pack(side="left", padx=5)

        elif self.current_cipher == "DiffieHellman":
            ctk.CTkLabel(self.key_frame, text=t["key_p"] + ":", **label_style).pack(side="left", padx=(5, 2))
            self.key1 = ctk.CTkEntry(self.key_frame, width=50, **entry_style)
            self.key1.insert(0, "23")
            self.key1.pack(side="left", padx=2)

            ctk.CTkLabel(self.key_frame, text=t["key_g"] + ":", **label_style).pack(side="left", padx=(5, 2))
            self.key2 = ctk.CTkEntry(self.key_frame, width=50, **entry_style)
            self.key2.insert(0, "5")
            self.key2.pack(side="left", padx=2)

            ctk.CTkLabel(self.key_frame, text=t["key_a"] + ":", **label_style).pack(side="left", padx=(5, 2))
            self.key3 = ctk.CTkEntry(self.key_frame, width=50, **entry_style)
            self.key3.insert(0, "6")
            self.key3.pack(side="left", padx=2)

            ctk.CTkLabel(self.key_frame, text=t["key_b"] + ":", **label_style).pack(side="left", padx=(5, 2))
            self.key4 = ctk.CTkEntry(self.key_frame, width=50, **entry_style)
            self.key4.insert(0, "15")
            self.key4.pack(side="left", padx=2)

        elif self.current_cipher == "RSA":
            ctk.CTkLabel(self.key_frame, text=t["key_p"] + ":", **label_style).pack(side="left", padx=(10, 2))
            self.key1 = ctk.CTkEntry(self.key_frame, width=60, **entry_style)
            self.key1.insert(0, "23")
            self.key1.pack(side="left", padx=2)

            ctk.CTkLabel(self.key_frame, text=t["key_q"] + ":", **label_style).pack(side="left", padx=(10, 2))
            self.key2 = ctk.CTkEntry(self.key_frame, width=60, **entry_style)
            self.key2.insert(0, "113")
            self.key2.pack(side="left", padx=2)

            ctk.CTkLabel(self.key_frame, text=t["key_e"] + ":", **label_style).pack(side="left", padx=(10, 2))
            self.key3 = ctk.CTkEntry(self.key_frame, width=60, **entry_style)
            self.key3.insert(0, "207")
            self.key3.pack(side="left", padx=2)

        elif self.current_cipher == "SDES":
            ctk.CTkLabel(self.key_frame, text=t.get("key_binary_key", "Key (10-bit)") + ":", **label_style).pack(side="left", padx=10)
            self.key1 = ctk.CTkEntry(self.key_frame, width=160, placeholder_text="1010110011", **entry_style)
            self.key1.insert(0, "1010110011")
            self.key1.pack(side="left", padx=5)
            ctk.CTkLabel(self.key_frame, text=self._fb("(10 \u0628\u062a \u062b\u0646\u0627\u0626\u064a)"), font=("Segoe UI", 11), text_color=T["TEXT_MUTED"]).pack(side="left", padx=5)

        elif self.current_cipher == "DES":
            ctk.CTkLabel(self.key_frame, text=t.get("key_des_key", "Key (64-bit)") + ":", **label_style).pack(side="left", padx=10)
            self.key1 = ctk.CTkEntry(self.key_frame, width=300, placeholder_text="0001001100110100010101110111100110011011101111001101111111110001", **entry_style)
            self.key1.insert(0, "0001001100110100010101110111100110011011101111001101111111110001")
            self.key1.pack(side="left", padx=5)
            ctk.CTkLabel(self.key_frame, text=self._fb("(64 \u0628\u062a \u062b\u0646\u0627\u0626\u064a / 56 \u0641\u0639\u0627\u0644)"), font=("Segoe UI", 11), text_color=T["TEXT_MUTED"]).pack(side="left", padx=5)

        else:
            ctk.CTkLabel(self.key_frame, text=t["key"] + ":", **label_style).pack(side="left", padx=10)
            self.key1 = ctk.CTkEntry(self.key_frame, width=250, **entry_style)
            self.key1.insert(0, "KEY")
            self.key1.pack(side="left", padx=5)

    def get_key_values(self):
        """Return current key-field values without exposing widget details to callers."""
        return tuple(
            field.get() if field is not None else ""
            for field in (getattr(self, f"key{index}", None) for index in range(1, 5))
        )
