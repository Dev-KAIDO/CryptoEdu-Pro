content = open(r'c:\Users\LENOVO\Desktop\Code-Cy\main.py', 'r', encoding='utf-8').read()

# Fix RSA canvas limit - the backslash u25a1 is stored as literal \u25a1 in file
idx = content.find('for ch in input_text:\n                m = ord(ch)\n                c = pow(m, e, n)')
if idx != -1:
    # Get a larger window to understand context
    snippet = content[idx-50:idx+600]
    print("Full RSA for block:")
    print(repr(snippet))
else:
    print("NOT FOUND")
