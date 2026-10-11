content = open(r'c:\Users\LENOVO\Desktop\Code-Cy\main.py', 'r', encoding='utf-8').read()

# ============================================================
# Fix 8: Make output_box read-only after writing result
# We need to enable it before writing, then disable it
# ============================================================

# In run_encrypt: make output_box read-only after writing
old_enc_output = '            self.output_box.delete("1.0", "end")\n            self.output_box.insert("1.0", result)\n            self.status_bar.set_status("\u2705 " + t["status_ready"], "#10b981")\n\n            self.operations_count += 1\n            if hasattr(self, \'ops_label\'):\n                ops_text = "\u0639\u0645\u0644\u064a\u0627\u062a" if self.lang == "AR" else "operations"\n                self.ops_label.configure(text=f"{self.operations_count} {ops_text}")\n            self._add_to_history(self.current_cipher, text, result, "encrypt")'

new_enc_output = '            self.output_box.configure(state="normal")\n            self.output_box.delete("1.0", "end")\n            self.output_box.insert("1.0", result)\n            self.output_box.configure(state="disabled")\n            self.status_bar.set_status("\u2705 " + t["status_ready"], "#10b981")\n\n            self.operations_count += 1\n            if hasattr(self, \'ops_label\'):\n                ops_text = "\u0639\u0645\u0644\u064a\u0627\u062a" if self.lang == "AR" else "operations"\n                self.ops_label.configure(text=f"{self.operations_count} {ops_text}")\n            self._add_to_history(self.current_cipher, text, result, "encrypt")'

if old_enc_output in content:
    content = content.replace(old_enc_output, new_enc_output, 1)
    print('Fix 8a (output_box read-only encrypt): OK')
else:
    print('Fix 8a: pattern not found')
    idx = content.find('self.output_box.delete("1.0", "end")\n            self.output_box.insert("1.0", result)\n            self.status_bar.set_status')
    print('  found at:', idx)

# In run_decrypt: same
old_dec_output = '            self.output_box.delete("1.0", "end")\n            self.output_box.insert("1.0", result)\n            self.status_bar.set_status("\u2705 " + t["status_ready"], "#10b981")\n\n            self.operations_count += 1\n            if hasattr(self, \'ops_label\'):\n                ops_text = "\u0639\u0645\u0644\u064a\u0627\u062a" if self.lang == "AR" else "operations"\n                self.ops_label.configure(text=f"{self.operations_count} {ops_text}")\n            self._add_to_history(self.current_cipher, text, result, "decrypt")'

new_dec_output = '            self.output_box.configure(state="normal")\n            self.output_box.delete("1.0", "end")\n            self.output_box.insert("1.0", result)\n            self.output_box.configure(state="disabled")\n            self.status_bar.set_status("\u2705 " + t["status_ready"], "#10b981")\n\n            self.operations_count += 1\n            if hasattr(self, \'ops_label\'):\n                ops_text = "\u0639\u0645\u0644\u064a\u0627\u062a" if self.lang == "AR" else "operations"\n                self.ops_label.configure(text=f"{self.operations_count} {ops_text}")\n            self._add_to_history(self.current_cipher, text, result, "decrypt")'

if old_dec_output in content:
    content = content.replace(old_dec_output, new_dec_output, 1)
    print('Fix 8b (output_box read-only decrypt): OK')
else:
    print('Fix 8b: pattern not found')

# Also fix output_box in error handlers
old_err_enc = '        except Exception as e:\n            self.output_box.delete("1.0", "end")\n            self.output_box.insert("1.0", f"\u274c {fix_bidi(str(e))}")\n            self.status_bar.set_status("\u274c " + TRANSLATIONS[self.lang]["status_error"], "#ef4444")\n\n    def run_decrypt'
new_err_enc = '        except Exception as e:\n            self.output_box.configure(state="normal")\n            self.output_box.delete("1.0", "end")\n            self.output_box.insert("1.0", f"\u274c {fix_bidi(str(e))}")\n            self.output_box.configure(state="disabled")\n            self.status_bar.set_status("\u274c " + TRANSLATIONS[self.lang]["status_error"], "#ef4444")\n\n    def run_decrypt'
if old_err_enc in content:
    content = content.replace(old_err_enc, new_err_enc, 1)
    print('Fix 8c (output_box read-only error encrypt): OK')
else:
    print('Fix 8c: pattern not found')

old_err_dec = '        except Exception as e:\n            self.output_box.delete("1.0", "end")\n            self.output_box.insert("1.0", f"\u274c {fix_bidi(str(e))}")\n            self.status_bar.set_status("\u274c " + TRANSLATIONS[self.lang]["status_error"], "#ef4444")\n\n    def copy_result'
new_err_dec = '        except Exception as e:\n            self.output_box.configure(state="normal")\n            self.output_box.delete("1.0", "end")\n            self.output_box.insert("1.0", f"\u274c {fix_bidi(str(e))}")\n            self.output_box.configure(state="disabled")\n            self.status_bar.set_status("\u274c " + TRANSLATIONS[self.lang]["status_error"], "#ef4444")\n\n    def copy_result'
if old_err_dec in content:
    content = content.replace(old_err_dec, new_err_dec, 1)
    print('Fix 8d (output_box read-only error decrypt): OK')
else:
    print('Fix 8d: pattern not found')

# Also fix swap_texts: output_box.delete needs state=normal first
old_swap = '    def swap_texts(self):\n        output_text = self.output_box.get("1.0", "end-1c")\n\n        self.output_box.delete("1.0", "end")\n\n        self.input_box.delete("1.0", "end")\n        self.input_box.insert("1.0", output_text)'
new_swap = '    def swap_texts(self):\n        output_text = self.output_box.get("1.0", "end-1c")\n\n        self.output_box.configure(state="normal")\n        self.output_box.delete("1.0", "end")\n        self.output_box.configure(state="disabled")\n\n        self.input_box.delete("1.0", "end")\n        self.input_box.insert("1.0", output_text)'
if old_swap in content:
    content = content.replace(old_swap, new_swap, 1)
    print('Fix 8e (swap_texts output_box): OK')
else:
    print('Fix 8e: pattern not found')

# Also fix clear_texts
old_clear = '    def clear_texts(self):\n        self.input_box.delete("1.0", "end")\n        self.output_box.delete("1.0", "end")'
new_clear = '    def clear_texts(self):\n        self.input_box.delete("1.0", "end")\n        self.output_box.configure(state="normal")\n        self.output_box.delete("1.0", "end")\n        self.output_box.configure(state="disabled")'
if old_clear in content:
    content = content.replace(old_clear, new_clear, 1)
    print('Fix 8f (clear_texts output_box): OK')
else:
    print('Fix 8f: pattern not found')

# ============================================================
# Fix 9: Add key validation helper
# ============================================================
# We add a helper _validate_key that shows a friendly error
key_validation_method = '''
    def _validate_caesar_key(self):
        """التحقق من صحة مفتاح قيصر قبل التشفير."""
        try:
            k = int(self.key1.get())
            return True, k
        except ValueError:
            self.status_bar.set_status(
                "\u26a0\ufe0f " + ("\u0645\u0641\u062a\u0627\u062d \u0642\u064a\u0635\u0631 \u064a\u062c\u0628 \u0623\u0646 \u064a\u0643\u0648\u0646 \u0631\u0642\u0645\u0627\u064b \u0635\u062d\u064a\u062d\u0627\u064b" if self.lang == "AR" else "Caesar key must be a valid integer"),
                "#f59e0b"
            )
            return False, None

'''

# Insert before run_encrypt
old_target = '    def run_encrypt(self):'
if key_validation_method not in content and old_target in content:
    content = content.replace(old_target, key_validation_method + '    def run_encrypt(self):', 1)
    print('Fix 9 (key validation method): OK')
else:
    print('Fix 9: already present or target not found')

# Apply validation in run_encrypt for Caesar
old_caesar_enc = '            if self.current_cipher == "Caesar":\n                key = int(self.key1.get())\n                result = CryptoCore.caesar_encrypt(text, key)'
new_caesar_enc = '            if self.current_cipher == "Caesar":\n                valid, key = self._validate_caesar_key()\n                if not valid:\n                    return\n                result = CryptoCore.caesar_encrypt(text, key)'
if old_caesar_enc in content:
    content = content.replace(old_caesar_enc, new_caesar_enc, 1)
    print('Fix 9a (caesar encrypt validation): OK')
else:
    print('Fix 9a: pattern not found')

open(r'c:\Users\LENOVO\Desktop\Code-Cy\main.py', 'w', encoding='utf-8').write(content)
print('\nAll saved! Length:', len(content))
