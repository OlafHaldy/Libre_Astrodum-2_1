"""
Liber Astrodum — Замена catch-блоков на модальное окно
"""

import os
import re

FILES = ['lunar.html', 'natal.html', 'daily.html', 'daily_personal.html']

# Функции модального окна (если их нет)
MODAL_FUNCTIONS = """
        function showErrorModal() {
            document.getElementById('errorOverlay').style.display = 'block';
            document.getElementById('errorModal').style.display = 'block';
        }
        function closeErrorModal() {
            document.getElementById('errorOverlay').style.display = 'none';
            document.getElementById('errorModal').style.display = 'none';
        }
"""

# HTML для модального окна
MODAL_HTML = """
    <div id="errorOverlay" class="overlay-bg" onclick="closeErrorModal()"></div>
    <div id="errorModal" class="error-modal">
        <p>Звёзды, как и астролог-мечтатель, любят покой. Позвольте ему отложить до завтра ваш запрос.</p>
        <button onclick="closeErrorModal()">Принимаю</button>
    </div>
"""

# CSS для модального окна
MODAL_CSS = """
        .error-modal {
            position: fixed;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            background: #1c1c1c;
            border: 2px solid #d4af37;
            border-radius: 16px;
            padding: 30px;
            text-align: center;
            max-width: 380px;
            width: 90%;
            z-index: 1001;
            display: none;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
            backdrop-filter: blur(10px);
        }
        .error-modal p { color: #f0f0f0; font-size: 1.15em; line-height: 1.6; margin-bottom: 25px; }
        .error-modal button {
            background: none;
            border: 1px solid #b8860b;
            color: #d4af37;
            padding: 10px 25px;
            border-radius: 20px;
            cursor: pointer;
            font-family: 'Cormorant Infant', serif;
            font-size: 1em;
        }
        .error-modal button:hover { background: rgba(184,134,11,0.2); }
        .overlay-bg {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.6); z-index: 1000; display: none;
        }
"""

for filename in FILES:
    if not os.path.exists(filename):
        print(f"[SKIP] {filename} не найден")
        continue
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # 1. Заменяем resultBlock.innerHTML = 'Ошибка...' на showErrorModal()
    old_catch = re.findall(r"catch\s*\([^)]*\)\s*\{[^}]*?innerHTML\s*=\s*'[^']*Ошибка[^']*'[^}]*?\}", content, re.DOTALL)
    for old in old_catch:
        new = old.replace(old, "catch (e) {\n                showErrorModal();\n            }")
        content = content.replace(old, new)
        changed = True
    
    # 2. Добавляем функции модального окна, если их нет
    if 'showErrorModal' not in content:
        content = content.replace('</script>', MODAL_FUNCTIONS + '\n    </script>')
        changed = True
    
    # 3. Добавляем HTML модального окна, если его нет
    if 'errorModal' not in content:
        content = content.replace('</body>', MODAL_HTML + '\n</body>')
        changed = True
    
    # 4. Добавляем CSS для модального окна, если его нет
    if 'error-modal' not in content:
        content = content.replace('</style>', MODAL_CSS + '\n    </style>')
        changed = True
    
    if changed:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] {filename} — обновлён")
    else:
        print(f"[SKIP] {filename} — уже настроен")

print("\nГотово!")