# fix_bugs.py — يُصلح المشاكل الحرجة في main.py
import re

filepath = r'c:\Users\LENOVO\Desktop\Code-Cy\main.py'
content = open(filepath, 'r', encoding='utf-8').read()

print("Original length:", len(content))

# ============================================================
# Fix 1: Add datetime import at top (CRLF aware)
# ============================================================
if 'import datetime' not in content:
    content = content.replace(
        'import pyperclip\r\n',
        'import datetime\r\nimport pyperclip\r\n',
        1
    )
    print("Fix 1 (datetime import):", "OK" if 'import datetime' in content else "FAILED")
else:
    print("Fix 1 (datetime import): already present")

# ============================================================
# Fix 2: Remove inner import datetime from _add_to_history
# ============================================================
content = content.replace(
    '    def _add_to_history(self, cipher, input_text, output_text, op_type):\r\n        import datetime\r\n',
    '    def _add_to_history(self, cipher, input_text, output_text, op_type):\r\n',
    1
)
print("Fix 2 (remove inner import datetime): done")

# ============================================================
# Fix 3: Add else clause in run_encrypt to prevent UnboundLocalError
# ============================================================
# Find the decrypt DES block inside run_encrypt followed by output
pattern_encrypt = (
    '                result = CryptoCore.des_encrypt(pt, key)\r\n'
    '\r\n'
    '            self.output_box.delete("1.0", "end")\r\n'
    '            self.output_box.insert("1.0", result)\r\n'
    '            self.status_bar.set_status("\u2705 " + t["status_ready"], "#10b981")\r\n'
    '\r\n'
    '            self.operations_count += 1\r\n'
    '            if hasattr(self, \'ops_label\'):\r\n'
    '                ops_text = "\u0639\u0645\u0644\u064a\u0627\u062a" if self.lang == "AR" else "operations"\r\n'
    '                self.ops_label.configure(text=f"{self.operations_count} {ops_text}")\r\n'
    '            self._add_to_history(self.current_cipher, text, result, "encrypt")'
)
replace_encrypt = (
    '                result = CryptoCore.des_encrypt(pt, key)\r\n'
    '            else:\r\n'
    '                raise ValueError(f"Cipher not implemented: {self.current_cipher}")\r\n'
    '\r\n'
    '            self.output_box.delete("1.0", "end")\r\n'
    '            self.output_box.insert("1.0", result)\r\n'
    '            self.status_bar.set_status("\u2705 " + t["status_ready"], "#10b981")\r\n'
    '\r\n'
    '            self.operations_count += 1\r\n'
    '            if hasattr(self, \'ops_label\'):\r\n'
    '                ops_text = "\u0639\u0645\u0644\u064a\u0627\u062a" if self.lang == "AR" else "operations"\r\n'
    '                self.ops_label.configure(text=f"{self.operations_count} {ops_text}")\r\n'
    '            self._add_to_history(self.current_cipher, text, result, "encrypt")'
)
if pattern_encrypt in content:
    content = content.replace(pattern_encrypt, replace_encrypt, 1)
    print("Fix 3 (run_encrypt else): OK")
else:
    print("Fix 3 (run_encrypt else): pattern not found, trying fallback")
    # Fallback: use simpler approach - find des_encrypt block near operations_count encrypt
    idx = content.find("result = CryptoCore.des_encrypt(pt, key)")
    if idx != -1:
        # Find the next empty line after this
        after = content[idx:]
        nl_pos = after.find('\r\n\r\n')
        if nl_pos != -1:
            insert_pos = idx + nl_pos
            content = content[:insert_pos] + '\r\n            else:\r\n                raise ValueError(f"Cipher not implemented: {self.current_cipher}")' + content[insert_pos:]
            print("Fix 3 (run_encrypt else): OK via fallback")

# ============================================================
# Fix 4: Add else clause in run_decrypt to prevent UnboundLocalError
# ============================================================
pattern_decrypt = (
    '                result = CryptoCore.des_decrypt(ct, key)\r\n'
    '\r\n'
    '            self.output_box.delete("1.0", "end")\n'
    '            self.output_box.insert("1.0", result)\r\n'
    '            self.status_bar.set_status("\u2705 " + t["status_ready"], "#10b981")\r\n'
    '\r\n'
    '            self.operations_count += 1\r\n'
    '            if hasattr(self, \'ops_label\'):\r\n'
    '                ops_text = "\u0639\u0645\u0644\u064a\u0627\u062a" if self.lang == "AR" else "operations"\r\n'
    '                self.ops_label.configure(text=f"{self.operations_count} {ops_text}")\r\n'
    '            self._add_to_history(self.current_cipher, text, result, "decrypt")'
)
replace_decrypt = (
    '                result = CryptoCore.des_decrypt(ct, key)\r\n'
    '            else:\r\n'
    '                raise ValueError(f"Cipher not implemented: {self.current_cipher}")\r\n'
    '\r\n'
    '            self.output_box.delete("1.0", "end")\n'
    '            self.output_box.insert("1.0", result)\r\n'
    '            self.status_bar.set_status("\u2705 " + t["status_ready"], "#10b981")\r\n'
    '\r\n'
    '            self.operations_count += 1\r\n'
    '            if hasattr(self, \'ops_label\'):\r\n'
    '                ops_text = "\u0639\u0645\u0644\u064a\u0627\u062a" if self.lang == "AR" else "operations"\r\n'
    '                self.ops_label.configure(text=f"{self.operations_count} {ops_text}")\r\n'
    '            self._add_to_history(self.current_cipher, text, result, "decrypt")'
)
if pattern_decrypt in content:
    content = content.replace(pattern_decrypt, replace_decrypt, 1)
    print("Fix 4 (run_decrypt else): OK")
else:
    print("Fix 4 (run_decrypt else): pattern not found, trying fallback")
    idx = content.find("result = CryptoCore.des_decrypt(ct, key)")
    if idx != -1:
        after = content[idx:]
        nl_pos = after.find('\r\n\r\n')
        if nl_pos != -1:
            insert_pos = idx + nl_pos
            content = content[:insert_pos] + '\r\n            else:\r\n                raise ValueError(f"Cipher not implemented: {self.current_cipher}")' + content[insert_pos:]
            print("Fix 4 (run_decrypt else): OK via fallback")

print("Cipher not implemented count:", content.count('Cipher not implemented'))

# ============================================================
# Fix 5: Add _playfair_prepare method before _analyze_playfair
# ============================================================
playfair_prepare_method = '''
    def _playfair_prepare(self, text):
        """تجهيز النص لشفرة بلايفير: تحويل لكبير وإزالة J واضافة X للأزواج المتماثلة."""
        text = text.upper().replace("J", "I").replace(" ", "")
        text = "".join(c for c in text if c.isalpha())
        prepared = ""
        i = 0
        while i < len(text):
            prepared += text[i]
            if i + 1 < len(text):
                if text[i] == text[i + 1]:
                    prepared += "X"
                else:
                    prepared += text[i + 1]
                    i += 1
            else:
                prepared += "X"
            i += 1
        if len(prepared) % 2 != 0:
            prepared += "X"
        return prepared

'''

if '_playfair_prepare' not in content:
    # Insert before _analyze_playfair
    target = '    # ---------- Playfair ----------\r\n    def _analyze_playfair'
    if target in content:
        content = content.replace(target, playfair_prepare_method + '    # ---------- Playfair ----------\r\n    def _analyze_playfair', 1)
        print("Fix 5 (_playfair_prepare): OK")
    else:
        print("Fix 5 (_playfair_prepare): target not found")
else:
    print("Fix 5 (_playfair_prepare): already present")

# ============================================================
# Fix 6: Protect Vigenere analysis from ZeroDivisionError (empty key)
# ============================================================
old_vigenere = "        key = self.key1.get().upper()\r\n        self._analysis_hero(\r\n            self._L(\"\u0634\u064a\u0641\u0631\u0629 \u0641\u064a\u062c\u064a\u0646\u064a\u0631  Vigen\\u00e8re\""
new_vigenere = "        key = self.key1.get().upper()\r\n        if not key:\r\n            key = \"A\"\r\n        self._analysis_hero(\r\n            self._L(\"\u0634\u064a\u0641\u0631\u0629 \u0641\u064a\u062c\u064a\u0646\u064a\u0631  Vigen\\u00e8re\""
if old_vigenere in content:
    content = content.replace(old_vigenere, new_vigenere, 1)
    print("Fix 6 (vigenere key guard): OK")
else:
    print("Fix 6 (vigenere key guard): pattern not found")

# ============================================================
# Fix 7: Limit RSA analysis canvas to MAX 10 chars to prevent freeze
# ============================================================
old_rsa_loop = '            for ch in input_text:\r\n                m = ord(ch)\r\n                c = pow(m, e, n)\r\n                self._rsa_lock_canvas(ch if ch.isprintable() else "\u25a1", m, c, e, n, "#7c3aed")\r\n                self._rsa_power_canvas(ch if ch.isprintable() else "\u25a1", m, c, e, n, "#7c3aed")'
new_rsa_loop = '            _rsa_max = 10\r\n            _rsa_shown = input_text[:_rsa_max]\r\n            if len(input_text) > _rsa_max:\r\n                ctk.CTkLabel(self.analysis_content, text=self._L(\r\n                    f"\u26a0\ufe0f \u062a\u0645 \u0639\u0631\u0636 \u0623\u0648\u0644 {_rsa_max} \u062d\u0631\u0648\u0641 \u0641\u0642\u0637 ({len(input_text)} \u0625\u062c\u0645\u0627\u0644\u064a\u0627\u064b) \u0644\u0644\u062d\u0641\u0627\u0638 \u0639\u0644\u0649 \u0627\u0644\u0633\u0631\u0639\u0629",\r\n                    f"\u26a0\ufe0f Showing first {_rsa_max} of {len(input_text)} chars for performance"\r\n                ), font=("Segoe UI", 10), text_color=T["WARNING"]).pack(pady=(0, 4))\r\n            for ch in _rsa_shown:\r\n                m = ord(ch)\r\n                c = pow(m, e, n)\r\n                self._rsa_lock_canvas(ch if ch.isprintable() else "\u25a1", m, c, e, n, "#7c3aed")\r\n                self._rsa_power_canvas(ch if ch.isprintable() else "\u25a1", m, c, e, n, "#7c3aed")'
if old_rsa_loop in content:
    content = content.replace(old_rsa_loop, new_rsa_loop, 1)
    print("Fix 7 (RSA canvas limit): OK")
else:
    print("Fix 7 (RSA canvas limit): pattern not found")

# ============================================================
# Save
# ============================================================
open(filepath, 'w', encoding='utf-8').write(content)
print("\nAll fixes applied and file saved!")
print("New length:", len(content))
