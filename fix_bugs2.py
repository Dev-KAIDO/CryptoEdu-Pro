content = open(r'c:\Users\LENOVO\Desktop\Code-Cy\main.py', 'r', encoding='utf-8').read()

# Fix 3: run_encrypt else clause
old = 'CryptoCore.des_encrypt(pt, key)\n\n            self.output_box'
new = 'CryptoCore.des_encrypt(pt, key)\n            else:\n                raise ValueError(f"Cipher not implemented: {self.current_cipher}")\n\n            self.output_box'
if old in content:
    content = content.replace(old, new, 1)
    print('Fix 3 encrypt else: OK')
else:
    print('Fix 3: NOT FOUND')

# Fix 4: run_decrypt else clause
old2 = 'CryptoCore.des_decrypt(ct, key)\n\n            self.output_box'
new2 = 'CryptoCore.des_decrypt(ct, key)\n            else:\n                raise ValueError(f"Cipher not implemented: {self.current_cipher}")\n\n            self.output_box'
if old2 in content:
    content = content.replace(old2, new2, 1)
    print('Fix 4 decrypt else: OK')
else:
    print('Fix 4: NOT FOUND')

print('Cipher not implemented count:', content.count('Cipher not implemented'))

# Fix 6: Vigenere ZeroDivisionError guard
idx = content.find('def _analyze_vigenere')
if idx != -1:
    snippet = content[idx:idx+500]
    print('Vigenere snippet found')
    # Find key = self.key1.get().upper() inside _analyze_vigenere
    old_v = 'def _analyze_vigenere(self, text, operation):\n        T = self._T\n        key = self.key1.get().upper()\n        self._analysis_hero('
    new_v = 'def _analyze_vigenere(self, text, operation):\n        T = self._T\n        key = self.key1.get().upper()\n        if not key:\n            key = "A"\n        self._analysis_hero('
    if old_v in content:
        content = content.replace(old_v, new_v, 1)
        print('Fix 6 vigenere guard: OK')
    else:
        print('Fix 6: vigenere exact pattern not found, trying snippet:')
        print(repr(snippet[:300]))

# Fix 7: RSA canvas limit
old_rsa = '            for ch in input_text:\n                m = ord(ch)\n                c = pow(m, e, n)\n                self._rsa_lock_canvas(ch if ch.isprintable() else "\u25a1", m, c, e, n, "#7c3aed")\n                self._rsa_power_canvas(ch if ch.isprintable() else "\u25a1", m, c, e, n, "#7c3aed")'
new_rsa = '            _rsa_max = 10\n            _rsa_shown = input_text[:_rsa_max]\n            if len(input_text) > _rsa_max:\n                ctk.CTkLabel(self.analysis_content, text=self._L(\n                    f"\u26a0\ufe0f Showing first {_rsa_max} of {len(input_text)} chars for performance",\n                    f"\u26a0\ufe0f Showing first {_rsa_max} of {len(input_text)} chars for performance"\n                ), font=("Segoe UI", 10), text_color=T["WARNING"]).pack(pady=(0, 4))\n            for ch in _rsa_shown:\n                m = ord(ch)\n                c = pow(m, e, n)\n                self._rsa_lock_canvas(ch if ch.isprintable() else "\u25a1", m, c, e, n, "#7c3aed")\n                self._rsa_power_canvas(ch if ch.isprintable() else "\u25a1", m, c, e, n, "#7c3aed")'
if old_rsa in content:
    content = content.replace(old_rsa, new_rsa, 1)
    print('Fix 7 RSA limit: OK')
else:
    idx_rsa = content.find('for ch in input_text:\n                m = ord(ch)\n                c = pow(m, e, n)')
    print('Fix 7: RSA for loop found at:', idx_rsa)
    if idx_rsa != -1:
        print(repr(content[idx_rsa-10:idx_rsa+200]))

open(r'c:\Users\LENOVO\Desktop\Code-Cy\main.py', 'w', encoding='utf-8').write(content)
print('Saved OK, length:', len(content))
