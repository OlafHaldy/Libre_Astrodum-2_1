"""
Liber Astrodum — Полная очистка favicon
"""

import os
import re

CORRECT_FAVICON = '<link rel="icon" href="data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><polygon points=\'50,5 61,39 95,39 68,61 79,95 50,75 21,95 32,61 5,39 39,39\' fill=\'%23d4af37\' stroke=\'%23b8860b\' stroke-width=\'2\'/></svg>">'

FILES = ['app.py', 'lunar.html', 'natal.html', 'daily.html']

for filename in FILES:
    if not os.path.exists(filename):
        print(f"[SKIP] {filename} не найден")
        continue
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        # Если строка содержит favicon — заменяем на чистую
        if '<link rel="icon"' in line:
            new_lines.append(CORRECT_FAVICON + '\n')
        else:
            new_lines.append(line)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"[OK] {filename} — очищен")

print("\nГотово! Перезапусти сервер и Ctrl+F5")