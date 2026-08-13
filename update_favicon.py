"""
Liber Astrodum — Замена favicon на пентаграмму
"""

import os
import re

NEW_FAVICON = '<link rel="icon" href="data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><polygon points=\'50,5 61,39 95,39 68,61 79,95 50,75 21,95 32,61 5,39 39,39\' fill=\'%23d4af37\' stroke=\'%23b8860b\' stroke-width=\'2\'/></svg>">'

FILES = ['app.py', 'lunar.html', 'natal.html', 'daily.html']

OLD_PATTERN = r'<link rel="icon"[^>]*>'

for filename in FILES:
    if not os.path.exists(filename):
        print(f"[SKIP] {filename} не найден")
        continue
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = re.sub(OLD_PATTERN, NEW_FAVICON, content, count=1)
    
    if new_content != content:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[OK] {filename} — favicon заменён")
    else:
        print(f"[SKIP] {filename} — favicon уже обновлён или не найден")

print("\nГотово!")