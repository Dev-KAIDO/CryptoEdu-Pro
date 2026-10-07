content = open(r'c:\Users\LENOVO\Desktop\Code-Cy\main.py', 'r', encoding='utf-8').read()

old_rsa = '            for ch in input_text:\n                m = ord(ch)\n                c = pow(m, e, n)\n                self._rsa_lock_canvas(ch if ch.isprintable() else "\\u25a1", m, c, e, n, "#7c3aed")\n                self._rsa_power_canvas(ch if ch.isprintable() else "\\u25a1", m, c, e, n, "#7c3aed")'

new_rsa = '''            _rsa_max = 10
            _rsa_shown = input_text[:_rsa_max]
            if len(input_text) > _rsa_max:
                ctk.CTkLabel(self.analysis_content,
                    text=self._L(
                        f"\\u26a0\\ufe0f \\u062a\\u0645 \\u0639\\u0631\\u0636 \\u0623\\u0648\\u0644 {_rsa_max} \\u062d\\u0631\\u0648\\u0641 \\u0641\\u0642\\u0637 ({len(input_text)} \\u0625\\u062c\\u0645\\u0627\\u0644\\u064a\\u0627\\u064b) \\u0644\\u0644\\u062d\\u0641\\u0627\\u0638 \\u0639\\u0644\\u0649 \\u0627\\u0644\\u0633\\u0631\\u0639\\u0629",
                        f"\\u26a0\\ufe0f Showing first {_rsa_max} of {len(input_text)} chars for performance"
                    ),
                    font=("Segoe UI", 10), text_color=T["WARNING"]
                ).pack(pady=(0, 4))
            for ch in _rsa_shown:
                m = ord(ch)
                c = pow(m, e, n)
                self._rsa_lock_canvas(ch if ch.isprintable() else "\\u25a1", m, c, e, n, "#7c3aed")
                self._rsa_power_canvas(ch if ch.isprintable() else "\\u25a1", m, c, e, n, "#7c3aed")'''

if old_rsa in content:
    content = content.replace(old_rsa, new_rsa, 1)
    print('Fix 7 RSA limit: OK')
else:
    print('Fix 7: EXACT PATTERN NOT FOUND')
    # count occurrences
    print('occurrences of for ch in input_text:', content.count('for ch in input_text:'))

open(r'c:\Users\LENOVO\Desktop\Code-Cy\main.py', 'w', encoding='utf-8').write(content)
print('Saved, length:', len(content))
