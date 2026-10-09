# core/algorithms.py
import math
import re

class CryptoCore:
    """النواة الأساسية لخوارزميات التشفير"""

    MAX_EDUCATIONAL_PRIME = 1_000_000

    @staticmethod
    def _require_latin_text(text, field="النص"):
        """ترفض الأحرف غير اللاتينية بدل تحويلها إلى نتائج خاطئة بصمت."""
        if any(char.isalpha() and not ("A" <= char.upper() <= "Z") for char in text):
            raise ValueError(f"{field} يجب أن يحتوي على أحرف إنجليزية فقط")

    @staticmethod
    def _require_latin_key(key, algorithm):
        key = key.strip()
        if not key or not key.isascii() or not key.isalpha():
            raise ValueError(f"مفتاح {algorithm} يجب أن يحتوي على أحرف إنجليزية فقط")
        return key.upper()
    
    @staticmethod
    def caesar_encrypt(text, key):
        """شفرة قيصر: إزاحة كل حرف بمقدار المفتاح"""
        CryptoCore._require_latin_text(text)
        result = ""
        for char in text.upper():
            if "A" <= char <= "Z":
                result += chr((ord(char) - 65 + key) % 26 + 65)
            else:
                result += char
        return result

    @staticmethod
    def caesar_decrypt(text, key):
        return CryptoCore.caesar_encrypt(text, -key)
    

    @staticmethod
    def mod_inverse(a, m=26):
        """حساب المعكوس الضربي باستخدام خوارزمية Euclidean الموسعة.
        يعمل مع أي قيمة لـ m (سواء m=26 لخوارزميات الأبجدية أو phi كبير لـ RSA)."""
        a = a % m
        if a == 0:
            return None
        # Extended Euclidean Algorithm
        old_r, r = a, m
        old_s, s = 1, 0
        while r != 0:
            q = old_r // r
            old_r, r = r, old_r - q * r
            old_s, s = s, old_s - q * s
        # old_r = gcd(a, m)
        if old_r != 1:
            return None  # لا يوجد معكوس ضربي
        return old_s % m

    @staticmethod
    def affine_encrypt(text, m, k):
        """شفرة أفاين: (m * x + k) mod 26"""
        CryptoCore._require_latin_text(text)
        if math.gcd(m, 26) != 1:
            raise ValueError("يجب أن يكون المفتاح m أولي مع 26")
        result = ""
        for char in text.upper():
            if "A" <= char <= "Z":
                x = ord(char) - 65
                result += chr((m * x + k) % 26 + 65)
            else:
                result += char
        return result

    @staticmethod
    def affine_decrypt(text, m, k):
        CryptoCore._require_latin_text(text)
        inv = CryptoCore.mod_inverse(m, 26)
        if inv is None:
            raise ValueError("لا يوجد معكوس ضربي للمفتاح m")
        result = ""
        for char in text.upper():
            if "A" <= char <= "Z":
                y = ord(char) - 65
                result += chr((inv * (y - k)) % 26 + 65)
            else:
                result += char
        return result

    @staticmethod
    def vigenere_encrypt(text, key):
        """شفرة فيجينير: إزاحة دورية بناءً على كلمة مفتاحية"""
        CryptoCore._require_latin_text(text)
        key = CryptoCore._require_latin_key(key, "Vigenère")
        text = text.upper()
        result = ""
        key_idx = 0
        for char in text:
            if "A" <= char <= "Z":
                shift = ord(key[key_idx % len(key)]) - 65
                result += chr((ord(char) - 65 + shift) % 26 + 65)
                key_idx += 1
            else:
                result += char
        return result

    @staticmethod
    def vigenere_decrypt(text, key):
        CryptoCore._require_latin_text(text)
        key = CryptoCore._require_latin_key(key, "Vigenère")
        text = text.upper()
        result = ""
        key_idx = 0
        for char in text:
            if "A" <= char <= "Z":
                shift = ord(key[key_idx % len(key)]) - 65
                result += chr((ord(char) - 65 - shift) % 26 + 65)
                key_idx += 1
            else:
                result += char
        return result

    @staticmethod
    def playfair_matrix(key):
        """بناء مصفوفة بلايفير 5x5"""
        key = CryptoCore._require_latin_key(key, "Playfair").replace("J", "I")
        matrix = []
        seen = set()
        for char in key + "ABCDEFGHIKLMNOPQRSTUVWXYZ":
            if char not in seen and "A" <= char <= "Z":
                matrix.append(char)
                seen.add(char)
        return [matrix[i:i+5] for i in range(0, 25, 5)]

    @staticmethod
    def playfair_encrypt(text, key):
        """شفرة بلايفير: تشفير أزواج الحروف باستخدام شبكة 5x5"""
        CryptoCore._require_latin_text(text)
        if any(not (char.isalpha() or char.isspace()) for char in text):
            raise ValueError("نص Playfair يجب أن يحتوي على أحرف ومسافات فقط")
        matrix = CryptoCore.playfair_matrix(key)
        text = text.upper().replace("J", "I").replace(" ", "")
        text = "".join(char for char in text if "A" <= char <= "Z")
        
        # تجهيز النص لأزواج
        prepared = ""
        i = 0
        while i < len(text):
            prepared += text[i]
            if i + 1 < len(text):
                if text[i] == text[i+1]:
                    prepared += "X"
                else:
                    prepared += text[i+1]
                    i += 1
            else:
                prepared += "X"
            i += 1
        
        if len(prepared) % 2 != 0:
            prepared += "X"
        
        def find_pos(char):
            for r in range(5):
                for c in range(5):
                    if matrix[r][c] == char:
                        return r, c
            return None

        result = ""
        for i in range(0, len(prepared), 2):
            r1, c1 = find_pos(prepared[i])
            r2, c2 = find_pos(prepared[i+1])
            if r1 == r2:
                result += matrix[r1][(c1+1)%5] + matrix[r2][(c2+1)%5]
            elif c1 == c2:
                result += matrix[(r1+1)%5][c1] + matrix[(r2+1)%5][c2]
            else:
                result += matrix[r1][c2] + matrix[r2][c1]
        return result

    @staticmethod
    def playfair_decrypt(text, key):
        """فك تشفير بلايفير"""
        CryptoCore._require_latin_text(text, "النص المشفر")
        if any(not (char.isalpha() or char.isspace()) for char in text):
            raise ValueError("نص Playfair المشفر يجب أن يحتوي على أحرف ومسافات فقط")
        matrix = CryptoCore.playfair_matrix(key)
        text = text.upper().replace(" ", "")
        if len(text) % 2:
            raise ValueError("نص Playfair المشفر يجب أن يتكون من عدد زوجي من الأحرف")
        
        def find_pos(char):
            for r in range(5):
                for c in range(5):
                    if matrix[r][c] == char:
                        return r, c
            return None
            
        result = ""
        for i in range(0, len(text), 2):
            if i+1 >= len(text):
                break
            r1, c1 = find_pos(text[i])
            r2, c2 = find_pos(text[i+1])
            if r1 == r2:
                result += matrix[r1][(c1-1)%5] + matrix[r2][(c2-1)%5]
            elif c1 == c2:
                result += matrix[(r1-1)%5][c1] + matrix[(r2-1)%5][c2]
            else:
                result += matrix[r1][c2] + matrix[r2][c1]

        result = re.sub(r'([A-Z])X\1', r'\1\1', result)
        return result

    @staticmethod
    def hill_matrix(key):
        """بناء مصفوفة المفتاح 2x2 من كلمة مفتاحية أو أرقام"""
        key = key.strip().upper()
        if len(key) == 4 and key.isascii() and key.isalpha():
            nums = [ord(char) - 65 for char in key]
        else:
            try:
                nums = [int(value.strip()) for value in key.split(",")]
            except (TypeError, ValueError):
                raise ValueError("مفتاح Hill يجب أن يكون 4 أحرف أو 4 أرقام مفصولة بفواصل") from None
            if len(nums) != 4:
                raise ValueError("مفتاح Hill يجب أن يحتوي على 4 قيم بالضبط")
        return [[nums[0] % 26, nums[1] % 26], [nums[2] % 26, nums[3] % 26]]

    @staticmethod
    def hill_encrypt(text, key):
        """شفرة هيل: تشفير باستخدام ضرب المصفوفات mod 26"""
        matrix = CryptoCore.hill_matrix(key)
        CryptoCore._require_latin_text(text)
        if any(not (char.isalpha() or char.isspace()) for char in text):
            raise ValueError("نص Hill يجب أن يحتوي على أحرف ومسافات فقط")
        text = text.upper().replace(" ", "")
        text = ''.join(c for c in text if "A" <= c <= "Z")

        if len(text) % 2 != 0:
            text += "X"

        result = ""
        for i in range(0, len(text), 2):
            p1 = ord(text[i]) - 65
            p2 = ord(text[i + 1]) - 65
            c1 = (matrix[0][0] * p1 + matrix[0][1] * p2) % 26
            c2 = (matrix[1][0] * p1 + matrix[1][1] * p2) % 26
            result += chr(c1 + 65) + chr(c2 + 65)
        return result

    @staticmethod
    def hill_decrypt(text, key):
        """فك تشفير هيل: استخدام المصفوفة العكسية mod 26"""
        matrix = CryptoCore.hill_matrix(key)
        CryptoCore._require_latin_text(text, "النص المشفر")
        if any(not (char.isalpha() or char.isspace()) for char in text):
            raise ValueError("نص Hill المشفر يجب أن يحتوي على أحرف ومسافات فقط")
        det = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 26
        inv_det = CryptoCore.mod_inverse(det, 26)
        if inv_det is None:
            raise ValueError("المصفوفة غير قابلة للعكس (det لا يقبل المعكوس)")

        inv_matrix = [
            [(matrix[1][1] * inv_det) % 26, (-matrix[0][1] * inv_det) % 26],
            [(-matrix[1][0] * inv_det) % 26, (matrix[0][0] * inv_det) % 26]
        ]

        text = text.upper().replace(" ", "")
        if len(text) % 2:
            raise ValueError("نص Hill المشفر يجب أن يتكون من عدد زوجي من الأحرف")
        result = ""
        for i in range(0, len(text), 2):
            c1 = ord(text[i]) - 65
            c2 = ord(text[i + 1]) - 65
            p1 = (inv_matrix[0][0] * c1 + inv_matrix[0][1] * c2) % 26
            p2 = (inv_matrix[1][0] * c1 + inv_matrix[1][1] * c2) % 26
            result += chr(p1 + 65) + chr(p2 + 65)
        return result

    @staticmethod
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0: return False
        return True

    @staticmethod
    def diffie_hellman_exchange(p, g, a, b, lang="AR"):
        if p > CryptoCore.MAX_EDUCATIONAL_PRIME:
            raise ValueError("قيمة p كبيرة جدًا للوضع التعليمي (الحد الأقصى 1000000)" if lang == "AR" else "p is too large for educational mode (maximum 1000000)")
        if not CryptoCore.is_prime(p):
            raise ValueError("العدد p يجب أن يكون أولياً" if lang == "AR" else "Number p must be prime")
        if not (1 < g < p):
            raise ValueError("المولد g يجب أن يكون بين 2 و p-1" if lang == "AR" else "Generator g must be between 2 and p-1")
        if not (0 < a < p and 0 < b < p):
            raise ValueError("المفاتيح الخاصة يجب أن تكون موجبة وأصغر من p" if lang == "AR" else "Private keys must be positive and less than p")

        A = pow(g, a, p)
        B = pow(g, b, p)
        ka = pow(B, a, p)
        kb = pow(A, b, p)

        if ka != kb:
            raise ValueError("خطأ في الحساب! المفاتيح غير متطابقة" if lang == "AR" else "Calculation error! Keys do not match")

        return str(ka)

    @staticmethod
    def dh_encrypt(text, p, g, a, b, lang="AR"):
        """تبادل مفاتيح ديفي-هيلمان + تشفير فعلي للنص بالمفتاح المشترك.
        يُشتقّ المفتاح المشترك ثم يُستعمل كإزاحة (shift) لكل حرف ليعطي ناتج مشفّر حقيقي."""
        CryptoCore._require_latin_text(text)
        ka = int(CryptoCore.diffie_hellman_exchange(p, g, a, b, lang))
        shift = (ka % 26) if (ka % 26) != 0 else 26
        result = ""
        for ch in text.upper():
            if "A" <= ch <= "Z":
                result += chr((ord(ch) - 65 + shift) % 26 + 65)
            else:
                result += ch
        return result

    @staticmethod
    def dh_decrypt(text, p, g, a, b, lang="AR"):
        """عكس dh_encrypt: يُشتق نفس المفتاح المشترك ويُعكَس إزاحة كل حرف لاسترجاع النص الأصلي."""
        CryptoCore._require_latin_text(text, "النص المشفر")
        ka = int(CryptoCore.diffie_hellman_exchange(p, g, a, b, lang))
        shift = (ka % 26) if (ka % 26) != 0 else 26
        result = ""
        for ch in text.upper():
            if "A" <= ch <= "Z":
                result += chr((ord(ch) - 65 - shift) % 26 + 65)
            else:
                result += ch
        return result

    @staticmethod
    def rsa_encrypt(text, p, q, e, lang="AR"):
        if p > CryptoCore.MAX_EDUCATIONAL_PRIME or q > CryptoCore.MAX_EDUCATIONAL_PRIME:
            raise ValueError("قيم p و q كبيرة جدًا للوضع التعليمي (الحد الأقصى 1000000)" if lang == "AR" else "p and q are too large for educational mode (maximum 1000000)")
        if not CryptoCore.is_prime(p) or not CryptoCore.is_prime(q):
            raise ValueError("يجب أن تكون الأعداد p و q أولية" if lang == "AR" else "Numbers p and q must be prime")
        if p == q:
            raise ValueError("يجب أن يكون p و q عددين أوليين مختلفين" if lang == "AR" else "p and q must be distinct primes")
        if e <= 1:
            raise ValueError("يجب أن يكون e أكبر من 1" if lang == "AR" else "e must be greater than 1")
        n = p * q
        phi = (p - 1) * (q - 1)
        if e >= phi:
            raise ValueError("يجب أن يكون e أصغر من phi" if lang == "AR" else "e must be less than phi")
        if math.gcd(e, phi) != 1:
            raise ValueError(f"الأس e ({e}) يجب أن يكون أولياً نسبياً مع phi ({phi})" if lang == "AR" else f"Exponent e ({e}) must be coprime to phi ({phi})")

        d = CryptoCore.mod_inverse(e, phi)
        if d is None:
            raise ValueError("لا يوجد معكوس ضربي لـ e مع phi" if lang == "AR" else "No modular inverse for e modulo phi")

        if any(ord(char) >= n for char in text):
            raise ValueError("كل قيمة حرف يجب أن تكون أصغر من n" if lang == "AR" else "Every character value must be less than n")
        cipher_nums = [pow(ord(char), e, n) for char in text]
        return ",".join(str(c) for c in cipher_nums)

    @staticmethod
    def rsa_decrypt(text, p, q, e, lang="AR"):
        if p > CryptoCore.MAX_EDUCATIONAL_PRIME or q > CryptoCore.MAX_EDUCATIONAL_PRIME:
            raise ValueError("قيم p و q كبيرة جدًا للوضع التعليمي (الحد الأقصى 1000000)" if lang == "AR" else "p and q are too large for educational mode (maximum 1000000)")
        if not CryptoCore.is_prime(p) or not CryptoCore.is_prime(q):
            raise ValueError("الأعداد p و q يجب أن تكون أولية" if lang == "AR" else "Numbers p and q must be prime")
        if p == q:
            raise ValueError("يجب أن يكون p و q عددين أوليين مختلفين" if lang == "AR" else "p and q must be distinct primes")
        if e <= 1:
            raise ValueError("يجب أن يكون e أكبر من 1" if lang == "AR" else "e must be greater than 1")
        n = p * q
        phi = (p - 1) * (q - 1)
        if e >= phi:
            raise ValueError("يجب أن يكون e أصغر من phi" if lang == "AR" else "e must be less than phi")
        d = CryptoCore.mod_inverse(e, phi)
        if d is None:
            raise ValueError("لا يوجد معكوس ضربي لـ e مع phi" if lang == "AR" else "No modular inverse for e modulo phi")

        import re
        nums = [int(x) for x in re.findall(r'\d+', text)]
        if not nums:
            raise ValueError("لم يتم العثور على أرقام صالحة لفك التشفير" if lang == "AR" else "No valid ciphertext numbers found")
        if any(number < 0 or number >= n for number in nums):
            raise ValueError("أرقام RSA يجب أن تكون بين 0 و n-1" if lang == "AR" else "RSA values must be between 0 and n-1")

        decrypted_chars = [chr(pow(c, d, n)) for c in nums]
        return "".join(decrypted_chars)

    # ============================================================
    # Simplified DES (S-DES)
    # ============================================================
    SDES_P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
    SDES_P8 = [6, 3, 7, 4, 8, 5, 10, 9]
    SDES_IP = [2, 6, 3, 1, 4, 8, 5, 7]
    SDES_IP_INV = [4, 1, 3, 5, 7, 2, 8, 6]
    SDES_EP = [4, 1, 2, 3, 2, 3, 4, 1]
    SDES_P4 = [2, 4, 3, 1]
    SDES_S0 = [
        [1, 0, 3, 2],
        [3, 2, 1, 0],
        [0, 2, 1, 3],
        [3, 1, 3, 2]
    ]
    SDES_S1 = [
        [0, 1, 2, 3],
        [2, 0, 1, 3],
        [3, 0, 1, 0],
        [2, 1, 0, 3]
    ]

    @staticmethod
    def _sdes_permute(bits, table):
        return ''.join(bits[i - 1] for i in table)

    @staticmethod
    def _sdes_xor(a, b):
        return ''.join(str(int(x) ^ int(y)) for x, y in zip(a, b))

    @staticmethod
    def _sdes_left_shift(bits, n):
        return bits[n:] + bits[:n]

    @staticmethod
    def _sdes_sbox(bits, sbox):
        row = int(bits[0] + bits[3], 2)
        col = int(bits[1] + bits[2], 2)
        val = sbox[row][col]
        return format(val, '02b')

    @staticmethod
    def _sdes_generate_keys(key_10bit):
        key = CryptoCore._sdes_permute(key_10bit, CryptoCore.SDES_P10)
        C = key[:5]
        D = key[5:]
        C1 = CryptoCore._sdes_left_shift(C, 1)
        D1 = CryptoCore._sdes_left_shift(D, 1)
        K1 = CryptoCore._sdes_permute(C1 + D1, CryptoCore.SDES_P8)
        C2 = CryptoCore._sdes_left_shift(C1, 2)
        D2 = CryptoCore._sdes_left_shift(D1, 2)
        K2 = CryptoCore._sdes_permute(C2 + D2, CryptoCore.SDES_P8)
        return K1, K2

    @staticmethod
    def _sdes_f(right_4bit, subkey_8bit):
        expanded = CryptoCore._sdes_permute(right_4bit, CryptoCore.SDES_EP)
        xored = CryptoCore._sdes_xor(expanded, subkey_8bit)
        s0_out = CryptoCore._sdes_sbox(xored[:4], CryptoCore.SDES_S0)
        s1_out = CryptoCore._sdes_sbox(xored[4:], CryptoCore.SDES_S1)
        return CryptoCore._sdes_permute(s0_out + s1_out, CryptoCore.SDES_P4)

    @staticmethod
    def sdes_encrypt(text, key):
        text = text.replace(' ', '')
        key = key.replace(' ', '')
        if len(text) != 8 or not all(c in '01' for c in text):
            raise ValueError("النص يجب أن يكون 8 بت ثنائي (مثل 10101101)")
        if len(key) != 10 or not all(c in '01' for c in key):
            raise ValueError("المفتاح يجب أن يكون 10 بت ثنائي (مثل 1010110011)")
        K1, K2 = CryptoCore._sdes_generate_keys(key)
        block = CryptoCore._sdes_permute(text, CryptoCore.SDES_IP)
        L0 = block[:4]
        R0 = block[4:]
        f1 = CryptoCore._sdes_f(R0, K1)
        L1 = R0
        R1 = CryptoCore._sdes_xor(L0, f1)
        L2 = R1
        R2 = CryptoCore._sdes_xor(L1, CryptoCore._sdes_f(R1, K2))
        return CryptoCore._sdes_permute(R2 + L2, CryptoCore.SDES_IP_INV)

    @staticmethod
    def sdes_decrypt(text, key):
        text = text.replace(' ', '')
        key = key.replace(' ', '')
        if len(text) != 8 or not all(c in '01' for c in text):
            raise ValueError("النص المشفر يجب أن يكون 8 بت ثنائي")
        if len(key) != 10 or not all(c in '01' for c in key):
            raise ValueError("المفتاح يجب أن يكون 10 بت ثنائي")
        K1, K2 = CryptoCore._sdes_generate_keys(key)
        block = CryptoCore._sdes_permute(text, CryptoCore.SDES_IP)
        L0 = block[:4]
        R0 = block[4:]
        f2 = CryptoCore._sdes_f(R0, K2)
        L1 = R0
        R1 = CryptoCore._sdes_xor(L0, f2)
        L2 = R1
        R2 = CryptoCore._sdes_xor(L1, CryptoCore._sdes_f(R1, K1))
        return CryptoCore._sdes_permute(R2 + L2, CryptoCore.SDES_IP_INV)

    @staticmethod
    def sdes_keygen(key):
        key = key.replace(' ', '')
        if len(key) != 10 or not all(c in '01' for c in key):
            raise ValueError("المفتاح يجب أن يكون 10 بت ثنائي")
        K1, K2 = CryptoCore._sdes_generate_keys(key)
        return K1, K2

    # ============================================================
    # Data Encryption Standard (DES)
    # ============================================================
    DES_IP = [
        58,50,42,34,26,18,10,2,
        60,52,44,36,28,20,12,4,
        62,54,46,38,30,22,14,6,
        64,56,48,40,32,24,16,8,
        57,49,41,33,25,17,9,1,
        59,51,43,35,27,19,11,3,
        61,53,45,37,29,21,13,5,
        63,55,47,39,31,23,15,7
    ]
    DES_FP = [
        40,8,48,16,56,24,64,32,
        39,7,47,15,55,23,63,31,
        38,6,46,14,54,22,62,30,
        37,5,45,13,53,21,61,29,
        36,4,44,12,52,20,60,28,
        35,3,43,11,51,19,59,27,
        34,2,42,10,50,18,58,26,
        33,1,41,9,49,17,57,25
    ]
    DES_PC1 = [
        57,49,41,33,25,17,9,
        1,58,50,42,34,26,18,
        10,2,59,51,43,35,27,
        19,11,3,60,52,44,36,
        63,55,47,39,31,23,15,
        7,62,54,46,38,30,22,
        14,6,61,53,45,37,29,
        21,13,5,28,20,12,4
    ]
    DES_PC2 = [
        14,17,11,24,1,5,
        3,28,15,6,21,10,
        23,19,12,4,26,8,
        16,7,27,20,13,2,
        41,52,31,37,47,55,
        30,40,51,45,33,48,
        44,49,39,56,34,53,
        46,42,50,36,29,32
    ]
    DES_E = [
        32,1,2,3,4,5,
        4,5,6,7,8,9,
        8,9,10,11,12,13,
        12,13,14,15,16,17,
        16,17,18,19,20,21,
        20,21,22,23,24,25,
        24,25,26,27,28,29,
        28,29,30,31,32,1
    ]
    DES_P = [
        16,7,20,21,
        29,12,28,17,
        1,15,23,26,
        5,18,31,10,
        2,8,24,14,
        32,27,3,9,
        19,13,30,6,
        22,11,4,25
    ]
    DES_SHIFT = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]
    DES_S = [
        [
            [14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],
            [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
            [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],
            [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]
        ],
        [
            [15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],
            [3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],
            [0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],
            [13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]
        ],
        [
            [10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],
            [13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],
            [13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],
            [1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]
        ],
        [
            [7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],
            [13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],
            [10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],
            [3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]
        ],
        [
            [2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],
            [14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],
            [4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],
            [11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]
        ],
        [
            [12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],
            [10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],
            [9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],
            [4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]
        ],
        [
            [4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],
            [13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],
            [1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],
            [6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]
        ],
        [
            [13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],
            [1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],
            [7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],
            [2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]
        ]
    ]

    @staticmethod
    def _des_permute(bits, table):
        return ''.join(bits[i - 1] for i in table)

    @staticmethod
    def _des_xor(a, b):
        return ''.join(str(int(x) ^ int(y)) for x, y in zip(a, b))

    @staticmethod
    def _des_left_shift(bits, n):
        return bits[n:] + bits[:n]

    @staticmethod
    def _des_sbox_8(bits):
        result = ""
        for i in range(8):
            block = bits[i * 6:(i + 1) * 6]
            row = int(block[0] + block[5], 2)
            col = int(block[1:5], 2)
            value = CryptoCore.DES_S[i][row][col]
            result += format(value, '04b')
        return result

    @staticmethod
    def _des_f(right_32, subkey_48):
        expanded = CryptoCore._des_permute(right_32, CryptoCore.DES_E)
        xored = CryptoCore._des_xor(expanded, subkey_48)
        substituted = CryptoCore._des_sbox_8(xored)
        return CryptoCore._des_permute(substituted, CryptoCore.DES_P)

    @staticmethod
    def des_keygen(key):
        key = key.replace(' ', '')
        if len(key) != 64 or not all(c in '01' for c in key):
            raise ValueError("المفتاح يجب أن يكون 64 بت ثنائي (56 بت فعال بعد إزالة Parity bits)")
        key56 = CryptoCore._des_permute(key, CryptoCore.DES_PC1)
        C = key56[:28]
        D = key56[28:]
        keys = []
        for n in CryptoCore.DES_SHIFT:
            C = CryptoCore._des_left_shift(C, n)
            D = CryptoCore._des_left_shift(D, n)
            keys.append(CryptoCore._des_permute(C + D, CryptoCore.DES_PC2))
        return keys

    @staticmethod
    def _des_core(block64, key64, decrypt=False):
        keys = CryptoCore.des_keygen(key64)
        if decrypt:
            keys = keys[::-1]
        block = CryptoCore._des_permute(block64, CryptoCore.DES_IP)
        L = block[:32]
        R = block[32:]
        for k in keys:
            L, R = R, CryptoCore._des_xor(L, CryptoCore._des_f(R, k))
        return CryptoCore._des_permute(R + L, CryptoCore.DES_FP)

    @staticmethod
    def des_encrypt(text, key):
        text = text.replace(' ', '')
        key = key.replace(' ', '')
        if len(text) != 64 or not all(c in '01' for c in text):
            raise ValueError("النص يجب أن يكون 64 بت ثنائي")
        if len(key) != 64 or not all(c in '01' for c in key):
            raise ValueError("المفتاح يجب أن يكون 64 بت ثنائي")
        return CryptoCore._des_core(text, key, decrypt=False)

    @staticmethod
    def des_decrypt(text, key):
        text = text.replace(' ', '')
        key = key.replace(' ', '')
        if len(text) != 64 or not all(c in '01' for c in text):
            raise ValueError("النص المشفر يجب أن يكون 64 بت ثنائي")
        if len(key) != 64 or not all(c in '01' for c in key):
            raise ValueError("المفتاح يجب أن يكون 64 بت ثنائي")
        return CryptoCore._des_core(text, key, decrypt=True)

    @staticmethod
    def get_full_code(cipher_name):
        """واجهة توافق لكتالوج الأكواد التعليمية المنفصل."""
        from .education import EducationCatalog
        return EducationCatalog.get_full_code(cipher_name)

    @staticmethod
    def get_explanation(cipher_name, lang="AR"):
        """واجهة توافق لكتالوج الشروحات التعليمي المنفصل."""
        from .education import EducationCatalog
        return EducationCatalog.get_explanation(cipher_name, lang)
