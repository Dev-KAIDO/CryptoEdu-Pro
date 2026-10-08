# core/algorithms.py
import math
import inspect
import re

class CryptoCore:
    """النواة الأساسية لخوارزميات التشفير"""

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
        """الحصول على الكود الكامل للخوارزمية المختارة مع الشرح"""
        
        # كود كامل لكل خوارزمية مع شرح مفصل
        full_codes = {
            "Caesar": '''# ============================================================
# شفرة قيصر (Caesar Cipher)
# ============================================================

def caesar_encrypt(text, key):
    """
    دالة تشفير قيصر
    المعاملات:
        text: النص المراد تشفيره
        key:  مفتاح الإزاحة (عدد صحيح)
    المخرجات:
        النص المشفر
    """
    result = ""  # متغير لتخزين النتيجة النهائية
    for char in text.upper():  # المرور على كل حرف بعد تحويله لكبير
        if char.isalpha():  # التحقق من أن الحرف أبجدي
            # تحويل الحرف إلى رقم (A=0, B=1, ...) ثم الإزاحة ثم التحويل مرة أخرى
            result += chr((ord(char) - 65 + key) % 26 + 65)
        else:
            result += char  # الاحتفاظ بالرموز غير الأبجدية كما هي
    return result  # إرجاع النص المشفر

def caesar_decrypt(text, key):
    """
    دالة فك تشفير قيصر
    المعاملات:
        text: النص المشفر
        key:  مفتاح الإزاحة
    المخرجات:
        النص الأصلي
    """
    # فك التشفير هو نفس التشفير ولكن بإزاحة سالبة
    return caesar_encrypt(text, -key)

# ============================================================
# مثال على الاستخدام:
# النص: HELLO
# المفتاح: 3
# النتيجة المشفرة: KHOOR
# ============================================================''',
            
            "Affine": '''# ============================================================
# شفرة أفاين (Affine Cipher)
# ============================================================

import math

def mod_inverse(a, m=26):
    """
    حساب المعكوس الضربي لـ a في modulo m
    المعاملات:
        a: العدد المطلوب معكوسه
        m: المعامل (افتراضي 26)
    المخرجات:
        المعكوس الضربي أو None إذا لم يكن موجوداً
    """
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def affine_encrypt(text, m, k):
    """
    دالة تشفير أفاين: (m * x + k) mod 26
    المعاملات:
        text: النص المراد تشفيره
        m:    المفتاح الأول (يجب أن يكون أولي مع 26)
        k:    المفتاح الثاني
    المخرجات:
        النص المشفر
    """
    # التحقق من أن m أولي مع 26
    if math.gcd(m, 26) != 1:
        raise ValueError("يجب أن يكون المفتاح m أولي مع 26")
    
    result = ""
    for char in text.upper():
        if char.isalpha():
            x = ord(char) - 65  # تحويل الحرف إلى رقم (A=0)
            # تطبيق معادلة التشفير
            result += chr((m * x + k) % 26 + 65)
        else:
            result += char
    return result

def affine_decrypt(text, m, k):
    """
    دالة فك تشفير أفاين
    المعاملات:
        text: النص المشفر
        m:    المفتاح الأول
        k:    المفتاح الثاني
    المخرجات:
        النص الأصلي
    """
    inv = mod_inverse(m, 26)  # حساب المعكوس الضربي
    if inv is None:
        raise ValueError("لا يوجد معكوس ضربي للمفتاح m")
    
    result = ""
    for char in text.upper():
        if char.isalpha():
            y = ord(char) - 65  # تحويل الحرف إلى رقم
            # تطبيق معادلة فك التشفير
            result += chr((inv * (y - k)) % 26 + 65)
        else:
            result += char
    return result

# ============================================================
# مثال على الاستخدام:
# النص: HELLO
# المفتاح m: 7
# المفتاح k: 10
# النتيجة المشفرة: ... (حسب الحساب)
# ============================================================''',
            
            "Vigenere": '''# ============================================================
# شفرة فيجينير (Vigenere Cipher)
# ============================================================

def vigenere_encrypt(text, key):
    """
    دالة تشفير فيجينير
    المعاملات:
        text: النص المراد تشفيره
        key:  الكلمة المفتاحية
    المخرجات:
        النص المشفر
    """
    text = text.upper()  # تحويل النص لحروف كبيرة
    key = key.upper()    # تحويل المفتاح لحروف كبيرة
    result = ""          # متغير النتيجة
    key_idx = 0          # مؤشر لتتبع موقعنا في المفتاح
    
    for char in text:
        if char.isalpha():
            # حساب مقدار الإزاحة من المفتاح
            shift = ord(key[key_idx % len(key)]) - 65
            # تطبيق الإزاحة على الحرف
            result += chr((ord(char) - 65 + shift) % 26 + 65)
            key_idx += 1  # التقدم إلى الحرف التالي في المفتاح
        else:
            result += char  # الاحتفاظ بالرموز غير الأبجدية
    return result

def vigenere_decrypt(text, key):
    """
    دالة فك تشفير فيجينير
    المعاملات:
        text: النص المشفر
        key:  الكلمة المفتاحية
    المخرجات:
        النص الأصلي
    """
    text = text.upper()
    key = key.upper()
    result = ""
    key_idx = 0
    
    for char in text:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)]) - 65
            # فك التشفير بطرح الإزاحة
            result += chr((ord(char) - 65 - shift) % 26 + 65)
            key_idx += 1
        else:
            result += char
    return result

# ============================================================
# مثال على الاستخدام:
# النص: HELLO
# المفتاح: KEY
# النتيجة المشفرة: ... (حسب الحساب)
# ============================================================''',
            
            "Playfair": '''# ============================================================
# شفرة بلايفير (Playfair Cipher)
# ============================================================

def playfair_matrix(key):
    """
    بناء مصفوفة بلايفير 5x5
    المعاملات:
        key: الكلمة المفتاحية
    المخرجات:
        مصفوفة 5x5 من الحروف
    """
    key = key.upper().replace("J", "I").replace(" ", "")
    matrix = []
    seen = set()
    # إضافة المفتاح ثم باقي الحروف الأبجدية
    for char in key + "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if char not in seen and char.isalpha():
            matrix.append(char)
            seen.add(char)
    return [matrix[i:i+5] for i in range(0, 25, 5)]

def playfair_encrypt(text, key):
    """
    دالة تشفير بلايفير
    المعاملات:
        text: النص المراد تشفيره
        key:  الكلمة المفتاحية
    المخرجات:
        النص المشفر
    """
    matrix = playfair_matrix(key)
    text = text.upper().replace("J", "I").replace(" ", "")
    
    # تجهيز النص لأزواج
    prepared = ""
    i = 0
    while i < len(text):
        prepared += text[i]
        if i + 1 < len(text):
            if text[i] == text[i+1]:
                prepared += "X"  # إضافة X للفصل بين الحروف المتكررة
            else:
                prepared += text[i+1]
                i += 1
        else:
            prepared += "X"  # إضافة X لإكمال الزوج الأخير
        i += 1
    
    if len(prepared) % 2 != 0:
        prepared += "X"
    
    def find_pos(char):
        """إيجاد موقع الحرف في المصفوفة"""
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
            # نفس الصف: إزاحة لليمين
            result += matrix[r1][(c1+1)%5] + matrix[r2][(c2+1)%5]
        elif c1 == c2:
            # نفس العمود: إزاحة لأسفل
            result += matrix[(r1+1)%5][c1] + matrix[(r2+1)%5][c2]
        else:
            # مستطيل: تبادل الأعمدة
            result += matrix[r1][c2] + matrix[r2][c1]
    return result

def playfair_decrypt(text, key):
    """
    دالة فك تشفير بلايفير
    المعاملات:
        text: النص المشفر
        key:  الكلمة المفتاحية
    المخرجات:
        النص الأصلي
    """
    matrix = playfair_matrix(key)
    
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
            # نفس الصف: إزاحة لليسار
            result += matrix[r1][(c1-1)%5] + matrix[r2][(c2-1)%5]
        elif c1 == c2:
            # نفس العمود: إزاحة لأعلى
            result += matrix[(r1-1)%5][c1] + matrix[(r2-1)%5][c2]
        else:
            # مستطيل: تبادل الأعمدة
            result += matrix[r1][c2] + matrix[r2][c1]
    result = re.sub(r'([A-Z])X\1', r'\1\1', result)
    return result

# ============================================================
# مثال على الاستخدام:
# النص: HELLO
# المفتاح: KEY
# النتيجة المشفرة: ... (حسب الحساب)
# ============================================================''',
            
            "Hill": '''# ============================================================
# شفرة هيل (Hill Cipher)
# ============================================================

def mod_inverse(a, m=26):
    """
    حساب المعكوس الضربي لـ a في modulo m
    """
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def hill_matrix(key):
    """
    بناء مصفوفة المفتاح 2x2 من كلمة مفتاحية
    المعاملات:
        key: كلمة مفتاحية من 4 حروف (مثل "HILL") أو أرقام مفصولة بفاصلة
    المخرجات:
        مصفوفة 2x2
    """
    key = key.upper().replace(" ", "")
    if len(key) >= 4 and not key.isdigit():
        # تحويل الحروف لأرقام (A=0, B=1, ...)
        matrix = []
        for char in key[:4]:
            matrix.append(ord(char) - 65)
        return [[matrix[0], matrix[1]], [matrix[2], matrix[3]]]
    else:
        # إدخال الأرقام مباشرة مفصولة بفاصلة
        nums = [int(x) for x in key.split(",")]
        return [[nums[0], nums[1]], [nums[2], nums[3]]]

def hill_encrypt(text, key):
    """
    دالة تشفير هيل: استخدام ضرب المصفوفات mod 26
    المعاملات:
        text: النص المراد تشفيره
        key:  المفتاح (كلمة من 4 حروف أو مصفوفة 2x2)
    المخرجات:
        النص المشفر
    """
    matrix = hill_matrix(key)
    text = text.upper().replace(" ", "")
    text = ''.join(c for c in text if c.isalpha())
    
    # إضافة X إذا كان طول النص فردي
    if len(text) % 2 != 0:
        text += "X"
    
    result = ""
    for i in range(0, len(text), 2):
        # تحويل الزوج إلى أرقام
        p1 = ord(text[i]) - 65      # الحرف الأول
        p2 = ord(text[i + 1]) - 65  # الحرف الثاني
        # ضرب المصفوفة: C = K * P (mod 26)
        c1 = (matrix[0][0] * p1 + matrix[0][1] * p2) % 26
        c2 = (matrix[1][0] * p1 + matrix[1][1] * p2) % 26
        result += chr(c1 + 65) + chr(c2 + 65)
    return result

def hill_decrypt(text, key):
    """
    دالة فك تشفير هيل: استخدام المصفوفة العكسية
    المعاملات:
        text: النص المشفر
        key:  المفتاح
    المخرجات:
        النص الأصلي
    """
    matrix = hill_matrix(key)
    # حساب المحدد (determinant)
    det = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 26
    inv_det = mod_inverse(det, 26)
    if inv_det is None:
        raise ValueError("المصفوفة غير قابلة للعكس")
    
    # بناء المصفوفة العكسية
    inv_matrix = [
        [(matrix[1][1] * inv_det) % 26, (-matrix[0][1] * inv_det) % 26],
        [(-matrix[1][0] * inv_det) % 26, (matrix[0][0] * inv_det) % 26]
    ]
    
    text = text.upper().replace(" ", "")
    result = ""
    for i in range(0, len(text), 2):
        c1 = ord(text[i]) - 65
        c2 = ord(text[i + 1]) - 65
        # ضرب المصفوفة العكسية: P = K^(-1) * C (mod 26)
        p1 = (inv_matrix[0][0] * c1 + inv_matrix[0][1] * c2) % 26
        p2 = (inv_matrix[1][0] * c1 + inv_matrix[1][1] * c2) % 26
        result += chr(p1 + 65) + chr(p2 + 65)
    return result

# ============================================================
# مثال على الاستخدام:
# النص: HELLO
# المفتاح: HILL (يتحول إلى مصفوفة [[7,8],[11,11]])
# النتيجة المشفرة: ... (حسب الحساب)
# ============================================================''',
            
            "DiffieHellman": '''# ============================================================
# تبادل مفاتيح ديفي-هيلمان (Diffie-Hellman Key Exchange)
# ============================================================

def diffie_hellman_demo():
    # 1. القيم العامة المشتركة (Public Parameters)
    p = 23  # عدد أولي (Prime number)
    g = 5   # مولد مناسب (Generator)

    # 2. اختيار المفاتيح الخاصة لكل طرف (Private Keys)
    a = 6   # مفتاح KAIDO الخاص (يبقى سرياً)
    b = 15  # مفتاح ALEX الخاص (يبقى سرياً)

    # 3. حساب المفاتيح العامة (Public Keys)
    A = pow(g, a, p)  # مفتاح KAIDO العام: A = g^a mod p
    B = pow(g, b, p)  # مفتاح ALEX العام: B = g^b mod p

    # 4. حساب المفتاح السري المشترك (Shared Secret)
    ka = pow(B, a, p)  # عند KAIDO: K = B^a mod p
    kb = pow(A, b, p)  # عند ALEX: K = A^b mod p

    print(f"KAIDO حصل على: {ka}")
    print(f"ALEX حصل على: {kb}")
    print(f"هل المفتاحان متطابقان؟ {ka == kb}")
''',

            "RSA": '''# ============================================================
# خوارزمية التشفير RSA (RSA Cryptosystem)
# ============================================================

def rsa_encrypt(plaintext, p, q, e):
    """
    تشفير الرسالة باستخدام المفتاح العام
    """
    n = p * q
    # تشفير كل حرف بشكل مستقل: C = P^e mod n
    ciphertext = [pow(ord(char), e, n) for char in plaintext]
    return ciphertext

def rsa_decrypt(ciphertext_list, p, q, d):
    """
    فك تشفير الرسالة باستخدام المفتاح الخاص
    """
    n = p * q
    # فك تشفير كل رقم: P = C^d mod n
    plaintext = "".join(chr(pow(num, d, n)) for num in ciphertext_list)
    return plaintext
'''
,
            "SDES": '''# ============================================================
# شفرة S-DES (Simplified DES)
# ============================================================

P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
P8  = [6, 3, 7, 4, 8, 5, 10, 9]
IP  = [2, 6, 3, 1, 4, 8, 5, 7]
IP_INV = [4, 1, 3, 5, 7, 2, 8, 6]
EP  = [4, 1, 2, 3, 2, 3, 4, 1]
P4  = [2, 4, 3, 1]

S0 = [[1,0,3,2],[3,2,1,0],[0,2,1,3],[3,1,3,2]]
S1 = [[0,1,2,3],[2,0,1,3],[3,0,1,0],[2,1,0,3]]

def permute(bits, table):
    return ''.join(bits[i-1] for i in table)

def xor(a, b):
    return ''.join(str(int(x)^int(y)) for x,y in zip(a,b))

def left_shift(bits, n):
    return bits[n:] + bits[:n]

def sbox(bits, sbox_table):
    row = int(bits[0]+bits[3], 2)
    col = int(bits[1]+bits[2], 2)
    return format(sbox_table[row][col], '02b')

def generate_keys(key_10bit):
    key = permute(key_10bit, P10)
    C, D = key[:5], key[5:]
    C1, D1 = left_shift(C, 1), left_shift(D, 1)
    K1 = permute(C1+D1, P8)
    C2, D2 = left_shift(C1, 2), left_shift(D1, 2)
    K2 = permute(C2+D2, P8)
    return K1, K2

def f(right_4bit, subkey):
    expanded = permute(right_4bit, EP)
    xored = xor(expanded, subkey)
    s0_out = sbox(xored[:4], S0)
    s1_out = sbox(xored[4:], S1)
    return permute(s0_out + s1_out, P4)

def sdes_encrypt(text, key):
    K1, K2 = generate_keys(key)
    block = permute(text, IP)
    L0, R0 = block[:4], block[4:]
    L1, R1 = R0, xor(L0, f(R0, K1))
    L2, R2 = R1, xor(L1, f(R1, K2))
    return permute(R2+L2, IP_INV)

def sdes_decrypt(text, key):
    K1, K2 = generate_keys(key)
    block = permute(text, IP)
    L0, R0 = block[:4], block[4:]
    L1, R1 = R0, xor(L0, f(R0, K2))
    L2, R2 = R1, xor(L1, f(R1, K1))
    return permute(R2+L2, IP_INV)

# مثال: plaintext=10101101, key=1010110011 → ciphertext=00111100
'''
,
            "DES": '''# ============================================================
# DES (Data Encryption Standard)
# ============================================================

IP = [58,50,42,34,26,18,10,2,60,52,44,36,28,20,12,4,
      62,54,46,38,30,22,14,6,64,56,48,40,32,24,16,8,
      57,49,41,33,25,17,9,1,59,51,43,35,27,19,11,3,
      61,53,45,37,29,21,13,5,63,55,47,39,31,23,15,7]

FP = [40,8,48,16,56,24,64,32,39,7,47,15,55,23,63,31,
      38,6,46,14,54,22,62,30,37,5,45,13,53,21,61,29,
      36,4,44,12,52,20,60,28,35,3,43,11,51,19,59,27,
      34,2,42,10,50,18,58,26,33,1,41,9,49,17,57,25]

PC1 = [57,49,41,33,25,17,9,1,58,50,42,34,26,18,
       10,2,59,51,43,35,27,19,11,3,60,52,44,36,
       63,55,47,39,31,23,15,7,62,54,46,38,30,22,
       14,6,61,53,45,37,29,21,13,5,28,20,12,4]

PC2 = [14,17,11,24,1,5,3,28,15,6,21,10,
       23,19,12,4,26,8,16,7,27,20,13,2,
       41,52,31,37,47,55,30,40,51,45,33,48,
       44,49,39,56,34,53,46,42,50,36,29,32]

E = [32,1,2,3,4,5,4,5,6,7,8,9,
     8,9,10,11,12,13,12,13,14,15,16,17,
     16,17,18,19,20,21,20,21,22,23,24,25,
     24,25,26,27,28,29,28,29,30,31,32,1]

P = [16,7,20,21,29,12,28,17,1,15,23,26,
     5,18,31,10,2,8,24,14,32,27,3,9,
     19,13,30,6,22,11,4,25]

SHIFT = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]

S = [
    [[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],
     [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
     [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],
     [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]],
    [[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],
     [3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],
     [0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],
     [13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]],
    [[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],
     [13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],
     [13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],
     [1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]],
    [[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],
     [13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],
     [10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],
     [3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],
    [[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],
     [14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],
     [4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],
     [11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]],
    [[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],
     [10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],
     [9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],
     [4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]],
    [[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],
     [13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],
     [1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],
     [6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]],
    [[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],
     [1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],
     [7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],
     [2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]]
]

def permute(bits, table):
    return ''.join(bits[i-1] for i in table)

def xor(a, b):
    return ''.join(str(int(x) ^ int(y)) for x, y in zip(a, b))

def shift(bits, n):
    return bits[n:] + bits[:n]

def generate_keys(key):
    key = permute(key, PC1)
    C, D = key[:28], key[28:]
    keys = []
    for n in SHIFT:
        C = shift(C, n)
        D = shift(D, n)
        keys.append(permute(C + D, PC2))
    return keys

def sbox(bits):
    result = ""
    for i in range(8):
        block = bits[i*6:(i+1)*6]
        row = int(block[0] + block[5], 2)
        col = int(block[1:5], 2)
        result += format(S[i][row][col], '04b')
    return result

def f(right, key):
    right = permute(right, E)      # 32 → 48
    right = xor(right, key)        # XOR with subkey
    right = sbox(right)            # 48 → 32
    return permute(right, P)       # P permutation

def des(block, key, decrypt=False):
    keys = generate_keys(key)
    if decrypt:
        keys.reverse()
    block = permute(block, IP)
    L, R = block[:32], block[32:]
    for k in keys:
        L, R = R, xor(L, f(R, k))
    return permute(R + L, FP)

# مثال: plaintext=0123456789ABCDEF (64 bits)، key=133457799BBCDFF1 (64 bits)
# كود التشفير الناتج: 85E813540F0AB405
'''
        }
        
        return full_codes.get(cipher_name, "لا يوجد كود متاح لهذه الخوارزمية")

    @staticmethod
    def get_explanation(cipher_name, lang="AR"):
        """الحصول على شرح تفصيلي للخوارزمية مفصل خطوة بخطوة"""
        explanations = {
            "Caesar": {
                "AR": [
                    ("🔹 def caesar_encrypt(text, key):", "تعريف دالة التشفير التي تستقبل النص الصريح ومفتاح الإزاحة (k)"),
                    ("   result = \"\"", "تهيئة متغير نصي فارغ لتجميع حروف النص المشفر"),
                    ("   for char in text.upper():", "تحويل جميع الحروف إلى كبيرة والتكرار على كل حرف في النص"),
                    ("       if char.isalpha():", "فحص ما إذا كان الرمز حرفاً أبجدياً أجنبياً (A-Z)"),
                    ("           p = ord(char) - 65", "تحويل الحرف إلى ترتيبه الرقمي بين 0 و 25 بطرح 65 (ASCII A)"),
                    ("           c = (p + key) % 26", "تطبيق معادلة التشفير: إضافة الإزاحة k ثم أخذ باقي القسمة على 26"),
                    ("           result += chr(c + 65)", "تحويل الرقم الناتج c إلى حرفه المقابل بإضافة 65"),
                    ("       else:", "في حال كان الرمز مسافة أو رقماً أو علامة ترقيم"),
                    ("           result += char", "إضافة الرمز كما هو بدون تغيير لمرحلة التشفير"),
                    ("   return result", "إرجاع النص المشفر النهائي كامل الحروف"),
                    ("", ""),
                    ("🔹 def caesar_decrypt(text, key):", "تعريف دالة فك التشفير لقيصر"),
                    ("   return caesar_encrypt(text, -key)", "فك التشفير يعتمد نفس الدالة مع عكس اتجاه الإزاحة (-k)")
                ],
                "EN": [
                    ("🔹 def caesar_encrypt(text, key):", "Define encryption function taking plaintext and shift key (k)"),
                    ("   result = \"\"", "Initialize empty string accumulator for ciphertext"),
                    ("   for char in text.upper():", "Convert input text to uppercase and iterate character by character"),
                    ("       if char.isalpha():", "Check if current character is an alphabetic letter (A-Z)"),
                    ("           p = ord(char) - 65", "Convert character to 0-25 index by subtracting 65 (ASCII A)"),
                    ("           c = (p + key) % 26", "Apply formula: add shift key k and take modulo 26"),
                    ("           result += chr(c + 65)", "Convert numeric result c back to character by adding 65"),
                    ("       else:", "If character is a space, digit, or punctuation symbol"),
                    ("           result += char", "Retain non-alphabet character unchanged"),
                    ("   return result", "Return final accumulated ciphertext string"),
                    ("", ""),
                    ("🔹 def caesar_decrypt(text, key):", "Define decryption function for Caesar cipher"),
                    ("   return caesar_encrypt(text, -key)", "Decryption reuses encryption function with negative shift (-k)")
                ]
            },
            "Affine": {
                "AR": [
                    ("🔹 def mod_inverse(a, m=26):", "دالة البحث عن المعكوس الضربي النمطي a⁻¹ mod m"),
                    ("   for x in range(1, m):", "اختبار جميع الأعداد المحتملة x من 1 إلى m-1"),
                    ("       if (a * x) % m == 1:", "شرط المعكوس الضربي: ضرب العدد مع معكوسه يُعطي باقي 1 mod m"),
                    ("           return x", "إرجاع المعكوس الضربي x فور العثور عليه"),
                    ("   return None", "إرجاع لا شيء إذا لم يوجد معكوس (عندما يكون gcd(a,m) ≠ 1)"),
                    ("", ""),
                    ("🔹 def affine_encrypt(text, m, k):", "دالة تشفير أفاين بتمرير النص والمفتاحين m و k"),
                    ("   if math.gcd(m, 26) != 1:", "التحقق من أن المفتاح m أوليّ نسبياً مع 26 (شرط القابلية للعكس)"),
                    ("       raise ValueError", "إطلاق استثناء إذا كان m غير أوليّ نسبياً مع 26"),
                    ("   for char in text.upper():", "التكرار على حروف النص الكبير"),
                    ("       x = ord(char) - 65", "تحويل الحرف الأصلي إلى قيمة رقمية x بين 0 و 25"),
                    ("       c = (m * x + k) % 26", "تطبيق معادلة التشفير المتآلفة: E(x) = (m·x + k) mod 26"),
                    ("       result += chr(c + 65)", "تحويل النتيجة الرقمية c إلى حرف مشفر وإضافته للنتيجة"),
                    ("", ""),
                    ("🔹 def affine_decrypt(text, m, k):", "دالة فك تشفير أفاين باستخدام المعكوس الضربي"),
                    ("   inv = mod_inverse(m, 26)", "حساب المعكوس الضربي للمفتاح الأول m⁻¹ mod 26"),
                    ("   for char in text.upper():", "التكرار على حروف النص المشفر"),
                    ("       y = ord(char) - 65", "تحويل الحرف المشفر إلى قيمة رقمية y بين 0 و 25"),
                    ("       p = (inv * (y - k)) % 26", "تطبيق معادلة فك التشفير: D(y) = m⁻¹·(y - k) mod 26"),
                    ("       result += chr(p + 65)", "تحويل النتيجة p إلى الحرف الأصلي وإضافته للنص التفكيكي")
                ],
                "EN": [
                    ("🔹 def mod_inverse(a, m=26):", "Function to compute modular multiplicative inverse a⁻¹ mod m"),
                    ("   for x in range(1, m):", "Iterate over candidate values x from 1 to m-1"),
                    ("       if (a * x) % m == 1:", "Condition: product of number and its inverse equals 1 mod m"),
                    ("           return x", "Return modular inverse x once found"),
                    ("   return None", "Return None if inverse does not exist (when gcd(a,m) ≠ 1)"),
                    ("", ""),
                    ("🔹 def affine_encrypt(text, m, k):", "Affine encryption function with multipliers m and shift k"),
                    ("   if math.gcd(m, 26) != 1:", "Validate multiplier m is coprime to 26 (invertibility condition)"),
                    ("       raise ValueError", "Raise exception if m is not coprime to 26"),
                    ("   for char in text.upper():", "Iterate through each character in uppercase text"),
                    ("       x = ord(char) - 65", "Convert plaintext letter to numeric index x (0-25)"),
                    ("       c = (m * x + k) % 26", "Apply Affine formula: E(x) = (m·x + k) mod 26"),
                    ("       result += chr(c + 65)", "Convert output value c back to ciphertext character"),
                    ("", ""),
                    ("🔹 def affine_decrypt(text, m, k):", "Affine decryption function using modular inverse"),
                    ("   inv = mod_inverse(m, 26)", "Compute modular inverse inv = m⁻¹ mod 26"),
                    ("   for char in text.upper():", "Iterate through each character in ciphertext"),
                    ("       y = ord(char) - 65", "Convert ciphertext character to numeric index y (0-25)"),
                    ("       p = (inv * (y - k)) % 26", "Apply decryption formula: D(y) = m⁻¹·(y - k) mod 26"),
                    ("       result += chr(p + 65)", "Convert numeric plaintext p back to letter")
                ]
            },
            "Vigenere": {
                "AR": [
                    ("🔹 def vigenere_encrypt(text, key):", "تعريف دالة تشفير فيجينير التعددية الإزاحات"),
                    ("   text = text.upper()", "تحويل النص المراد تشفيره إلى حروف كبيرة"),
                    ("   key = key.upper()", "تحويل كلمة المفتاح إلى حروف كبيرة"),
                    ("   key_idx = 0", "مؤشر لتتبع موقع الحرف الحالي من كلمة المفتاح"),
                    ("   for char in text:", "التكرار على كل حرف في النص الأصلي"),
                    ("       if char.isalpha():", "التحقق من أن العنصر حرف أبجدي"),
                    ("           kv = key[key_idx % len(key)]", "استخراج حرف المفتاح المقابل مع التكرار الدوري دورياً"),
                    ("           shift = ord(kv) - 65", "حساب قيمة الإزاحة k المستخرجة من حرف المفتاح"),
                    ("           c = (ord(char) - 65 + shift) % 26", "تطبيق إزاحة قيصر المتغيرة بحرف المفتاح المقابل"),
                    ("           result += chr(c + 65)", "تحويل القيمة المشفرة c إلى حرف وإضافته للنتيجة"),
                    ("           key_idx += 1", "تحديث المؤشر للانتقال للحرف التالي في كلمة المفتاح"),
                    ("       else: result += char", "الحفاظ على المسافات والرموز غير الأبجدية دون تغيير مؤشر المفتاح"),
                    ("", ""),
                    ("🔹 def vigenere_decrypt(text, key):", "دالة فك تشفير فيجينير"),
                    ("   shift = ord(key[key_idx % len(key)]) - 65", "استخراج إزاحة المفتاح للحرف الحالي"),
                    ("   p = (ord(char) - 65 - shift) % 26", "طرح الإزاحة لفك التشفير: P = (C - K) mod 26"),
                    ("   result += chr(p + 65)", "تحويل القيمة الرقمية p للحرف الأصلي")
                ],
                "EN": [
                    ("🔹 def vigenere_encrypt(text, key):", "Polyalphabetic Vigenere encryption function"),
                    ("   text = text.upper()", "Normalize input plaintext to uppercase"),
                    ("   key = key.upper()", "Normalize key phrase to uppercase"),
                    ("   key_idx = 0", "Index tracker for stepping through keyword characters"),
                    ("   for char in text:", "Loop through each character in plaintext"),
                    ("       if char.isalpha():", "Verify character is alphabetic"),
                    ("           kv = key[key_idx % len(key)]", "Get current keyword character cyclically using modulo"),
                    ("           shift = ord(kv) - 65", "Convert keyword letter to numerical shift value"),
                    ("           c = (ord(char) - 65 + shift) % 26", "Shift letter by keyword value: C = (P + K) mod 26"),
                    ("           result += chr(c + 65)", "Convert numeric value c back to ciphertext character"),
                    ("           key_idx += 1", "Advance keyword index only when an alphabetic letter is processed"),
                    ("       else: result += char", "Keep punctuation/spaces intact without incrementing key index"),
                    ("", ""),
                    ("🔹 def vigenere_decrypt(text, key):", "Vigenere decryption function"),
                    ("   shift = ord(key[key_idx % len(key)]) - 65", "Extract key shift value for current character"),
                    ("   p = (ord(char) - 65 - shift) % 26", "Subtract shift to decrypt: P = (C - K) mod 26"),
                    ("   result += chr(p + 65)", "Convert numeric index p back to original plaintext letter")
                ]
            },
            "Playfair": {
                "AR": [
                    ("🔹 def playfair_matrix(key):", "بناء شبكة بلايفير 5×5 من كلمة المفتاح"),
                    ("   key = key.upper().replace('J', 'I')", "دمج حرف J مع I واستبداله في المفتاح"),
                    ("   seen = set()", "مجموعة متغيرة لتجنب تكرار أي حرف في الشبكة"),
                    ("   for char in key + 'ABCDEFGHIKLMNOPQRSTUVWXYZ':", "دمج المفتاح مع الأبجدية كاملة (بدون J)"),
                    ("       if char not in seen and char.isalpha():", "التحقق من عدم وجود الحرف سابقاً في الشبكة"),
                    ("           matrix.append(char)", "إضافة الحرف للشبكة وتحديث قائمة الملاحظات"),
                    ("   return [matrix[i:i+5] for i in range(0, 25, 5)]", "تقسيم المصفوفة المكونة من 25 حرفاً إلى 5 صفوف"),
                    ("", ""),
                    ("🔹 def playfair_encrypt(text, key):", "دالة تشفير أزواج بلايفير"),
                    ("   text = text.upper().replace('J', 'I')", "تحويل النص واستبدال J بـ I"),
                    ("   prepared = '' ...", "تجهيز النص بتقسيمه لأزواج وإضافة X بين الحروف المتكررة في الزوج"),
                    ("   if r1 == r2:", "قاعدة الصف الواحد: الحرفان في نفس الصف"),
                    ("       matrix[r1][(c1+1)%5] + matrix[r2][(c2+1)%5]", "الإزاحة لليمين مع التدوير الحلقي mod 5"),
                    ("   elif c1 == c2:", "قاعدة العمود الواحد: الحرفان في نفس العمود"),
                    ("       matrix[(r1+1)%5][c1] + matrix[(r2+1)%5][c2]", "الإزاحة لأسفل مع التدوير الحلقي mod 5"),
                    ("   else:", "قاعدة المستطيل: الحرفان في زوايا مختلفة"),
                    ("       matrix[r1][c2] + matrix[r2][c1]", "تبادل أعمدة الزوايا المتقابلة للمستطيل"),
                    ("", ""),
                    ("🔹 def playfair_decrypt(text, key):", "دالة فك تشفير بلايفير"),
                    ("   if r1 == r2: matrix[r1][(c1-1)%5] ...", "في نفس الصف: الإزاحة لليسار mod 5"),
                    ("   elif c1 == c2: matrix[(r1-1)%5][c1] ...", "في نفس العمود: الإزاحة لأعلى mod 5"),
                    ("   else: matrix[r1][c2] + matrix[r2][c1]", "في المستطيل: تبادل الأعمدة نفس القاعدة العكسية")
                ],
                "EN": [
                    ("🔹 def playfair_matrix(key):", "Construct 5x5 Playfair grid from key phrase"),
                    ("   key = key.upper().replace('J', 'I')", "Replace J with I and convert key to uppercase"),
                    ("   seen = set()", "Set tracker to prevent duplicating characters in grid"),
                    ("   for char in key + 'ABCDEFGHIKLMNOPQRSTUVWXYZ':", "Append alphabet (minus J) after unique key letters"),
                    ("       if char not in seen and char.isalpha():", "Ensure character has not been inserted yet"),
                    ("           matrix.append(char)", "Insert unique character into flat grid list"),
                    ("   return [matrix[i:i+5] for i in range(0, 25, 5)]", "Chunk 25 characters into 5 rows of 5 columns"),
                    ("", ""),
                    ("🔹 def playfair_encrypt(text, key):", "Playfair digraph encryption function"),
                    ("   text = text.upper().replace('J', 'I')", "Prepare plaintext: replace J with I"),
                    ("   prepared = '' ...", "Split text into digraph pairs, inserting filler 'X' between duplicate letters"),
                    ("   if r1 == r2:", "Same Row Rule: Both letters are in the same grid row"),
                    ("       matrix[r1][(c1+1)%5] + matrix[r2][(c2+1)%5]", "Shift each letter 1 step RIGHT (mod 5)"),
                    ("   elif c1 == c2:", "Same Column Rule: Both letters are in the same grid column"),
                    ("       matrix[(r1+1)%5][c1] + matrix[(r2+1)%5][c2]", "Shift each letter 1 step DOWN (mod 5)"),
                    ("   else:", "Rectangle Rule: Letters form opposite corners of a rectangle"),
                    ("       matrix[r1][c2] + matrix[r2][c1]", "Swap columns to take horizontal opposite corners"),
                    ("", ""),
                    ("🔹 def playfair_decrypt(text, key):", "Playfair digraph decryption function"),
                    ("   if r1 == r2: matrix[r1][(c1-1)%5] ...", "Same row: Shift 1 step LEFT (mod 5)"),
                    ("   elif c1 == c2: matrix[(r1-1)%5][c1] ...", "Same column: Shift 1 step UP (mod 5)"),
                    ("   else: matrix[r1][c2] + matrix[r2][c1]", "Rectangle: Swap columns (same geometric rule)")
                ]
            },
            "Hill": {
                "AR": [
                    ("🔹 def hill_matrix(key):", "بناء مصفوفة التشفير 2x2 من كلمة المفتاح"),
                    ("   for char in key[:4]:", "أخذ الحروف الأربعة الأولى من المفتاح وتصفيفها"),
                    ("       matrix.append(ord(char) - 65)", "تحويل كل حرف إلى رقم بين 0 و 25"),
                    ("   return [[m0, m1], [m2, m3]]", "إرجاع مصفوفة المفتاح 2x2: K = [a b; c d]"),
                    ("", ""),
                    ("🔹 def hill_encrypt(text, key):", "دالة تشفير هيل بضرب المصفوفات mod 26"),
                    ("   if len(text) % 2 != 0: text += 'X'", "إضافة حرف حشو X إذا كان طول النص فردياً لتشكيل أزواج 2x1"),
                    ("   p1 = ord(text[i]) - 65", "تحويل الحرف الأول من الزوج إلى رقم p1"),
                    ("   p2 = ord(text[i+1]) - 65", "تحويل الحرف الثاني من الزوج إلى رقم p2"),
                    ("   c1 = (matrix[0][0]*p1 + matrix[0][1]*p2) % 26", "حساب الصف الأول للناتج: c1 = (k00·p1 + k01·p2) mod 26"),
                    ("   c2 = (matrix[1][0]*p1 + matrix[1][1]*p2) % 26", "حساب الصف الثاني للناتج: c2 = (k10·p1 + k11·p2) mod 26"),
                    ("   result += chr(c1 + 65) + chr(c2 + 65)", "تحويل النتائج c1, c2 إلى حروف وإضافتها للنص المشفر"),
                    ("", ""),
                    ("🔹 def hill_decrypt(text, key):", "دالة فك تشفير هيل باستخدام المصفوفة العكسية"),
                    ("   det = (k00·k11 - k01·k10) % 26", "حساب محدد المصفوفة determinant: det(K) = (a·d - b·c) mod 26"),
                    ("   inv_det = mod_inverse(det, 26)", "حساب المعكوس الضربي للمحدد: inv_det = det⁻¹ mod 26"),
                    ("   inv_matrix = [[(d·inv)%26, (-b·inv)%26], ...]", "بناء المصفوفة العكسية: K⁻¹ = det⁻¹ · [d -b; -c a] mod 26"),
                    ("   p1 = (inv00·c1 + inv01·c2) % 26", "ضرب الزوج المشفر في المصفوفة العكسية لفك الصف الأول"),
                    ("   p2 = (inv10·c1 + inv11·c2) % 26", "ضرب الزوج المشفر في المصفوفة العكسية لفك الصف الثاني")
                ],
                "EN": [
                    ("🔹 def hill_matrix(key):", "Construct 2x2 key matrix K from 4-character key"),
                    ("   for char in key[:4]:", "Extract first 4 characters of the key string"),
                    ("       matrix.append(ord(char) - 65)", "Convert each character to 0-25 numeric value"),
                    ("   return [[m0, m1], [m2, m3]]", "Return 2x2 matrix K = [a b; c d]"),
                    ("", ""),
                    ("🔹 def hill_encrypt(text, key):", "Hill matrix multiplication encryption function (mod 26)"),
                    ("   if len(text) % 2 != 0: text += 'X'", "Pad with 'X' if plaintext length is odd to form 2x1 vector pairs"),
                    ("   p1 = ord(text[i]) - 65", "Convert first letter of pair to numerical value p1"),
                    ("   p2 = ord(text[i+1]) - 65", "Convert second letter of pair to numerical value p2"),
                    ("   c1 = (matrix[0][0]*p1 + matrix[0][1]*p2) % 26", "Matrix dot product row 1: c1 = (k00·p1 + k01·p2) mod 26"),
                    ("   c2 = (matrix[1][0]*p1 + matrix[1][1]*p2) % 26", "Matrix dot product row 2: c2 = (k10·p1 + k11·p2) mod 26"),
                    ("   result += chr(c1 + 65) + chr(c2 + 65)", "Convert output values c1, c2 back to characters"),
                    ("", ""),
                    ("🔹 def hill_decrypt(text, key):", "Hill decryption function using inverse matrix K⁻¹"),
                    ("   det = (k00·k11 - k01·k10) % 26", "Calculate determinant: det(K) = (a·d - b·c) mod 26"),
                    ("   inv_det = mod_inverse(det, 26)", "Compute modular inverse of determinant: inv_det = det⁻¹ mod 26"),
                    ("   inv_matrix = [[(d·inv)%26, (-b·inv)%26], ...]", "Build inverse matrix: K⁻¹ = det⁻¹ · [d -b; -c a] mod 26"),
                    ("   p1 = (inv00·c1 + inv01·c2) % 26", "Multiply ciphertext vector by inverse matrix row 1"),
                    ("   p2 = (inv10·c1 + inv11·c2) % 26", "Multiply ciphertext vector by inverse matrix row 2")
                ]
            },
            "DiffieHellman": {
                "AR": [
                    ("🔹 def diffie_hellman_exchange():", "دالة توضيحية لبروتوكول تبادل المفاتيح لـ ديفي-هيلمان"),
                    ("   p = 23 # عدد أولي عام", "الاتفاق العلني بين KAIDO و ALEX على عدد أولي ضخم p"),
                    ("   g = 5  # مولد أولي عام", "الاتفاق العلني على المولد الرياضياتي g بحيث g < p"),
                    ("   a = 6  # مفتاح KAIDO الخاص", "اختيار KAIDO لمفتاحه الخاص a وسريته التامة دون إرساله"),
                    ("   b = 15 # مفتاح ALEX الخاص", "اختيار ALEX لمفتاحه الخاص b وسريته التامة دون إرساله"),
                    ("   A = pow(g, a, p)", "KAIDO يحسب مفتاحه العام المشترك: A = gᵃ mod p = 5⁶ mod 23 = 8"),
                    ("   B = pow(g, b, p)", "ALEX يحسب مفتاحه العام المشترك: B = gᵇ mod p = 5¹⁵ mod 23 = 19"),
                    ("   A و B تُرسلان عبر القناة العامة", "تبادل القيمة A لـ ALEX والقيمة B لـ KAIDO علنياً في القناة"),
                    ("   s_alice = pow(B, a, p)", "KAIDO يحسب السر المشترك: s = Bᵃ mod p = 19⁶ mod 23 = 2"),
                    ("   s_bob = pow(A, b, p)", "ALEX يحسب السر المشترك: s = Aᵇ mod p = 8¹⁵ mod 23 = 2"),
                    ("   s_alice == s_bob", "النتيجة: كلا الطرفين توصلا لنفس المفتاح السري المشترك بدون إرساله!")
                ],
                "EN": [
                    ("🔹 def diffie_hellman_exchange():", "Demonstration function for Diffie-Hellman Key Exchange protocol"),
                    ("   p = 23 # public prime", "KAIDO and ALEX publicly agree on a shared prime number p"),
                    ("   g = 5  # public generator", "KAIDO and ALEX publicly agree on a shared base generator g < p"),
                    ("   a = 6  # KAIDO's private key", "KAIDO chooses a secret private exponent a (never transmitted)"),
                    ("   b = 15 # ALEX's private key", "ALEX chooses a secret private exponent b (never transmitted)"),
                    ("   A = pow(g, a, p)", "KAIDO computes public value: A = gᵃ mod p = 5⁶ mod 23 = 8"),
                    ("   B = pow(g, b, p)", "ALEX computes public value: B = gᵇ mod p = 5¹⁵ mod 23 = 19"),
                    ("   A and B exchanged publicly", "KAIDO sends A to ALEX, ALEX sends B to KAIDO over insecure channel"),
                    ("   s_alice = pow(B, a, p)", "KAIDO computes shared secret: s = Bᵃ mod p = 19⁶ mod 23 = 2"),
                    ("   s_bob = pow(A, b, p)", "ALEX computes shared secret: s = Aᵇ mod p = 8¹⁵ mod 23 = 2"),
                    ("   s_alice == s_bob", "Success: Both parties derive identical secret key s without sending it!")
                ]
            },
            "RSA": {
                "AR": [
                    ("🔹 def rsa_encrypt(plaintext, p, q, e):", "دالة التشفير باستخدام المفتاح العام (e, n) في نظام RSA"),
                    ("   n = p * q", "حساب معامل التشفير Modulus n بضرب العددين الأولين p و q"),
                    ("   phi = (p - 1) * (q - 1)", "حساب دالة أويلر Totient φ(n) = (p-1)·(q-1)"),
                    ("   for char in plaintext:", "التكرار على حروف النص المراد تشفيره"),
                    ("       m = ord(char)", "تحويل الحرف إلى قيمته العددية مرمز ASCII m"),
                    ("       c = pow(m, e, n)", "تطبيق معادلة التشفير غير المتماثل: c = mᵉ mod n"),
                    ("   return ciphertext", "إرجاع قائمة الأعداد المشفرة c1, c2, ..."),
                    ("", ""),
                    ("🔹 def rsa_decrypt(ciphertext, p, q, d):", "دالة فك التشفير باستخدام المفتاح الخاص (d, n) في RSA"),
                    ("   d = mod_inverse(e, phi)", "حساب الأس الخاص d بحيث e·d ≡ 1 mod φ(n)"),
                    ("   for c in ciphertext:", "التكرار على القيم الرقمية المشفرة c"),
                    ("       m = pow(c, d, n)", "تطبيق معادلة فك التشفير بالرفع للأس الخاص: m = cᵈ mod n"),
                    ("       plaintext += chr(m)", "تحويل الرقم المفكوك m إلى الحرف الأصلي بتشفير ASCII")
                ],
                "EN": [
                    ("🔹 def rsa_encrypt(plaintext, p, q, e):", "RSA asymmetric encryption function using public key (e, n)"),
                    ("   n = p * q", "Calculate RSA modulus n by multiplying primes p and q"),
                    ("   phi = (p - 1) * (q - 1)", "Compute Euler totient function φ(n) = (p-1)·(q-1)"),
                    ("   for char in plaintext:", "Iterate through each character in plaintext input"),
                    ("       m = ord(char)", "Convert plaintext character to numeric ASCII code m"),
                    ("       c = pow(m, e, n)", "Apply RSA public key encryption formula: c = mᵉ mod n"),
                    ("   return ciphertext", "Return list of encrypted numeric ciphertexts [c1, c2, ...]"),
                    ("", ""),
                    ("🔹 def rsa_decrypt(ciphertext, p, q, d):", "RSA asymmetric decryption function using private key (d, n)"),
                    ("   d = mod_inverse(e, phi)", "Calculate private exponent d such that e·d ≡ 1 mod φ(n)"),
                    ("   for c in ciphertext:", "Iterate through each numeric ciphertext element c"),
                    ("       m = pow(c, d, n)", "Apply RSA private key decryption formula: m = cᵈ mod n"),
                    ("       plaintext += chr(m)", "Convert decrypted numeric code m back to ASCII character")
                ]
            },
            "SDES": {
                "AR": [
                    ("🔹 def sdes_generate_keys(key_10bit):", "دالة توليد المفاتيح الفرعية K1 و K2 من المفتاح الأصلي 10 بت"),
                    ("   key = permute(key, P10)", "تطبيق تبديل P10 على المفتاح لإعادة ترتيب الـ 10 بت"),
                    ("   C, D = key[:5], key[5:]", "تقسيم المفتاح إلى نصفين: C (5 بت) و D (5 بت)"),
                    ("   C1 = left_shift(C, 1)", "إزاحة C يسارًا بمقدار 1"),
                    ("   D1 = left_shift(D, 1)", "إزاحة D يسارًا بمقدار 1"),
                    ("   K1 = permute(C1+D1, P8)", "تطبيق P8 على (C1|D1) لإنتاج المفتاح الفرعي K1 (8 بت)"),
                    ("   C2 = left_shift(C1, 2)", "إزاحة C1 يسارًا بمقدار 2"),
                    ("   D2 = left_shift(D1, 2)", "إزاحة D1 يسارًا بمقدار 2"),
                    ("   K2 = permute(C2+D2, P8)", "تطبيق P8 على (C2|D2) لإنتاج المفتاح الفرعي K2 (8 بت)"),
                    ("", ""),
                    ("🔹 def sdes_f(right_4bit, subkey):", "دالة الجولة F: تأخذ 4 بت يمين + مفتاح فرعي 8 بت"),
                    ("   expanded = permute(right, EP)", "توسيع 4 بت إلى 8 بت باستخدام جدول التوسيع EP"),
                    ("   xored = xor(expanded, subkey)", "عمل XOR بين الناتج الموسّع والمفتاح الفرعي"),
                    ("   s0_out = sbox(xored[:4], S0)", "تمرير الـ 4 بت الأولى إلى صندوق S0 → ناتج 2 بت"),
                    ("   s1_out = sbox(xored[4:], S1)", "تمرير الـ 4 بت الثانية إلى صندوق S1 → ناتج 2 بت"),
                    ("   return permute(s0_out+s1_out, P4)", "تطبيق P4 على ناتج الصناديق للحصول على 4 بت نهائية"),
                    ("", ""),
                    ("🔹 def sdes_encrypt(text, key):", "دالة تشفير S-DES: تشفير بلوك 8 بت بمفتاح 10 بت"),
                    ("   K1, K2 = generate_keys(key)", "توليد المفتاحين الفرعيين K1 و K2"),
                    ("   block = permute(text, IP)", "تطبيق البدائية IP على النص لإعادة ترتيب البتات"),
                    ("   L0, R0 = block[:4], block[4:]", "تقسيم النص المُعاد ترتيبه إلى نصفين: L0 و R0"),
                    ("   R1 = L0 XOR F(R0, K1)", "الجولة الأولى: L1=R0, R1=L0 XOR F(R0,K1)"),
                    ("   swap → L1'=R1, R1'=L0'", "عمل SWAP (تبديل) بين النصفين"),
                    ("   R2 = L1' XOR F(R1', K2)", "الجولة الثانية: L2=R1', R2=L1' XOR F(R1',K2)"),
                    ("   return permute(R2+L2, IP⁻¹)", "تطبيق IP⁻¹ (IP المعكوس) للحصول على النص المشفر 8 بت"),
                    ("", ""),
                    ("🔹 def sdes_decrypt(text, key):", "فك التشفير: نفس التشفير لكن بعكس ترتيب المفاتيح"),
                    ("   K1, K2 = generate_keys(key)", "توليد K1 و K2"),
                    ("   ... Round 1 with K2 ...", "الجولة الأولى تستخدم K2 (عكس التشفير)"),
                    ("   ... Round 2 with K1 ...", "الجولة الثانية تستخدم K1")
                ],
                "EN": [
                    ("🔹 def sdes_generate_keys(key_10bit):", "Generate subkeys K1 and K2 from the 10-bit master key"),
                    ("   key = permute(key, P10)", "Apply P10 permutation to rearrange the 10 bits"),
                    ("   C, D = key[:5], key[5:]", "Split key into two halves: C (5 bits) and D (5 bits)"),
                    ("   C1 = left_shift(C, 1)", "Left circular shift C by 1 position"),
                    ("   D1 = left_shift(D, 1)", "Left circular shift D by 1 position"),
                    ("   K1 = permute(C1+D1, P8)", "Apply P8 to (C1|D1) to produce subkey K1 (8 bits)"),
                    ("   C2 = left_shift(C1, 2)", "Left circular shift C1 by 2 positions"),
                    ("   D2 = left_shift(D1, 2)", "Left circular shift D1 by 2 positions"),
                    ("   K2 = permute(C2+D2, P8)", "Apply P8 to (C2|D2) to produce subkey K2 (8 bits)"),
                    ("", ""),
                    ("🔹 def sdes_f(right_4bit, subkey):", "Round function F: takes 4-bit right half + 8-bit subkey"),
                    ("   expanded = permute(right, EP)", "Expand 4 bits to 8 bits using expansion permutation EP"),
                    ("   xored = xor(expanded, subkey)", "XOR the expanded result with the subkey"),
                    ("   s0_out = sbox(xored[:4], S0)", "Feed first 4 bits to S-box S0 → 2-bit output"),
                    ("   s1_out = sbox(xored[4:], S1)", "Feed last 4 bits to S-box S1 → 2-bit output"),
                    ("   return permute(s0_out+s1_out, P4)", "Apply P4 to combined S-box outputs → 4-bit result"),
                    ("", ""),
                    ("🔹 def sdes_encrypt(text, key):", "S-DES encryption: encrypt 8-bit block with 10-bit key"),
                    ("   K1, K2 = generate_keys(key)", "Generate subkeys K1 and K2"),
                    ("   block = permute(text, IP)", "Apply Initial Permutation IP to rearrange bits"),
                    ("   L0, R0 = block[:4], block[4:]", "Split permuted block into left half L0 and right half R0"),
                    ("   R1 = L0 XOR F(R0, K1)", "Round 1: L1=R0, R1=L0 XOR F(R0,K1)"),
                    ("   swap → L1'=R1, R1'=L0'", "SWAP the two halves"),
                    ("   R2 = L1' XOR F(R1', K2)", "Round 2: L2=R1', R2=L1' XOR F(R1',K2)"),
                    ("   return permute(R2+L2, IP⁻¹)", "Apply inverse IP to get 8-bit ciphertext"),
                    ("", ""),
                    ("🔹 def sdes_decrypt(text, key):", "Decryption: same as encryption but with reversed subkey order"),
                    ("   K1, K2 = generate_keys(key)", "Generate K1 and K2"),
                    ("   ... Round 1 with K2 ...", "Round 1 uses K2 (reversed from encryption)"),
                    ("   ... Round 2 with K1 ...", "Round 2 uses K1")
                ]
            },
            "DES": {
                "AR": [
                    ("🔹 def generate_keys(key):", "دالة توليد المفاتيح الفرعية الـ 16 من المفتاح الأصلي 64 بت"),
                    ("   key = permute(key, PC1)", "تطبيق PC-1: حذف الـ Parity bits وتحويل 64 بت → 56 بت"),
                    ("   C, D = key[:28], key[28:]", "تقسيم الـ 56 بت إلى نصفين C0 و D0 (28 بت لكل منهما)"),
                    ("   for n in SHIFT:", "لكل جولة نأخذ عدد الإزاحات من جدول SHIFT"),
                    ("       C = shift(C, n)", "إزاحة دائرية لليسار للنصف C بمقدار n"),
                    ("       D = shift(D, n)", "إزاحة دائرية لليسار للنصف D بمقدار n"),
                    ("       keys.append(permute(C+D, PC2))", "تطبيق PC-2 على (C|D) للحصول على المفتاح الفرعي Ki (48 بت)"),
                    ("", ""),
                    ("🔹 def f(right, key):", "دالة الجولة F: تأخذ النصف الأيمن 32 بت والمفتاح الفرعي 48 بت"),
                    ("   right = permute(right, E)", "توسيع 32 بت → 48 بت (تكرار بعض البتات)"),
                    ("   right = xor(right, key)", "XOR بين الناتج الموسّع والمفتاح الفرعي"),
                    ("   right = sbox(right)", "تمرير الـ 48 بت إلى 8 صناديق S-Box (كل 6 بت ← 4 بت)‏"),
                    ("   return permute(right, P)", "إعادة ترتيب الـ 32 بت الناتجة بتبديل P"),
                    ("", ""),
                    ("🔹 def des(block, key, decrypt=False):", "وظيفة DES الرئيسية: تفاوت 64 بت بمفتاح 64 بت عبر 16 جولة Feistel"),
                    ("   keys = generate_keys(key)", "توليد الـ 16 مفتاحًا فرعيًا K1 ... K16"),
                    ("   if decrypt: keys.reverse()", "لفك التشفير نعكس ترتيب المفاتيح: K16 → K1"),
                    ("   block = permute(block, IP)", "تطبيق البدائية Initial Permutation (IP)‏"),
                    ("   L, R = block[:32], block[32:]", "تقسيم الـ 64 بت إلى نصفين L و R (32 بت لكل منهما)"),
                    ("   for k in keys: L, R = R, L⊕F(R,k)", "16 جولة فيكل أقل: كل جولة المفتاح الفرعي الخاص بها"),
                    ("   return permute(R + L, FP)", "ترتيب R16|L16 ثم تطبيق الصافي النهائي (FP) للحصول على النص المشفر"),
                    ("", ""),
                    ("⚠️ ملاحظة أمنية:", "DES مفتاحها 56 بت فقط فلا تُستخدم TODAY للبيانات المهمة — بديلها AES")
                ],
                "EN": [
                    ("🔹 def generate_keys(key):", "Generate 16 round subkeys from the original 64-bit key"),
                    ("   key = permute(key, PC1)", "Apply PC-1: drop parity bits, 64 bits → 56 bits"),
                    ("   C, D = key[:28], key[28:]", "Split the 56 bits into C0 and D0 halves (28 bits each)"),
                    ("   for n in SHIFT:", "For each round take the shift count from the SHIFT table"),
                    ("       C = shift(C, n)", "Left circular shift half C by n positions"),
                    ("       D = shift(D, n)", "Left circular shift half D by n positions"),
                    ("       keys.append(permute(C+D, PC2))", "Apply PC-2 to (C|D) to get subkey Ki (48 bits)"),
                    ("", ""),
                    ("🔹 def f(right, key):", "Round function F: takes 32-bit right half + 48-bit subkey"),
                    ("   right = permute(right, E)", "Expand 32 bits → 48 bits (some bits are duplicated)"),
                    ("   right = xor(right, key)", "XOR between expanded bits and the subkey"),
                    ("   right = sbox(right)", "Feed 48 bits to 8 S-Boxes (each 6 bits → 4 bits)"),
                    ("   return permute(right, P)", "Rearrange the resulting 32 bits with P permutation"),
                    ("", ""),
                    ("🔹 def des(block, key, decrypt=False):", "Main DES function: encrypt 64-bit block with 64-bit key over 16 Feistel rounds"),
                    ("   keys = generate_keys(key)", "Generate the 16 subkeys K1 ... K16"),
                    ("   if decrypt: keys.reverse()", "For decryption reverse the subkey order: K16 → K1"),
                    ("   block = permute(block, IP)", "Apply the Initial Permutation (IP)"),
                    ("   L, R = block[:32], block[32:]", "Split the 64 bits into L and R halves (32 bits each)"),
                    ("   for k in keys: L, R = R, L⊕F(R,k)", "16 Feistel rounds, each using its own subkey"),
                    ("   return permute(R + L, FP)", "Arrange R16|L16 then apply the final permutation (FP) to get ciphertext"),
                    ("", ""),
                    ("⚠️ Security note:", "DES has only a 56-bit effective key, so it is NOT used for critical data today — AES replaced it")
                ]
            }
        }
        return explanations.get(cipher_name, {}).get(lang, [("⚠️ لا يوجد شرح متاح", "⚠️ No explanation available")])
