"""
Add aphorism styles to all HTML files.
"""

import os
import re

CSS_TO_ADD = """

/* ===== АФОРИЗМ-ЭПИГРАФ ===== */
.aphorism {
    font-family: 'Caveat', cursive;
    font-size: 1.35em;
    color: #d4af37;
    font-style: italic;
    margin: 8px 0 15px 0;
    padding: 12px 18px;
    border-left: 3px solid rgba(212, 175, 55, 0.6);
    background: linear-gradient(90deg, rgba(212, 175, 55, 0.08), rgba(212, 175, 55, 0.02), transparent);
    border-radius: 0 10px 10px 0;
    text-shadow: 0 0 12px rgba(212, 175, 55, 0.25);
    line-height: 1.5;
    letter-spacing: 0.03em;
}

.aphorism::before {
    content: '❧ ';
    font-size: 1.1em;
    color: #b8860b;
    opacity: 0.8;
    margin-right: 5px;
}

.aphorism-label {
    font-family: 'Cormorant Infant', serif;
    font-size: 0.7em;
    color: #b8860b;
    text-transform: uppercase;
    letter-spacing: 3px;
    opacity: 0.6;
    margin-bottom: 3px;
    margin-top: 5px;
}

/* ===== БЛОК ИНТЕРПРЕТАЦИИ ===== */
.interpretation-block {
    margin: 20px 0;
    padding: 22px 24px;
    background: linear-gradient(135deg, rgba(35, 35, 35, 0.85), rgba(10, 10, 10, 0.7));
    border: 1px solid rgba(212, 175, 55, 0.25);
    border-left: 3px solid #d4af37;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(5px);
}

.interpretation-block-title {
    color: #d4af37;
    font-size: 1.15rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(212, 175, 55, 0.25);
}

.interpretation-block-text {
    color: #e4e4e4;
    font-size: 1.05rem;
    line-height: 1.85;
    text-align: left;
}
"""

JS_TO_ADD = """
function formatAphorism(text) {
    const match = text.match(/Афоризм:\\s*[«"]([^»"]+)[»"]/);
    
    if (match) {
        const aphorismText = match[1];
        const restText = text.replace(/Афоризм:\\s*[«"][^»"]+[»"]\\s*/g, '');
        
        return `
            <div class="aphorism-label">Эпиграф</div>
            <div class="aphorism">${aphorismText}</div>
            <div class="interpretation-block-text">${restText.replace(/\\n/g, '<br>')}</div>
        `;
    }
    
    return `<div class="interpretation-block-text">${text.replace(/\\n/g, '<br>')}</div>`;
}
"""


def add_css_to_html(file_path):
    """Add CSS before closing </style> tag."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '.aphorism' in content:
        print(f'  CSS already present in {file_path}')
        return
    
    if '</style>' in content:
        content = content.replace('</style>', CSS_TO_ADD + '\n</style>')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  CSS added to {file_path}')
    else:
        print(f'  No <style> tag in {file_path}')


def add_js_to_html(file_path):
    """Add JS function before closing </script> tag."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'formatAphorism' in content:
        print(f'  JS already present in {file_path}')
        return
    
    if '</script>' in content:
        content = content.replace('</script>', JS_TO_ADD + '\n</script>')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  JS added to {file_path}')
    else:
        print(f'  No <script> tag in {file_path}')


def main():
    html_files = [
        'natal.html',
        'lunar.html',
        'solar.html',
        'daily.html',
        'daily_personal.html',
    ]
    
    print('=' * 60)
    print('ADDING APHORISM STYLES TO HTML FILES')
    print('=' * 60)
    
    for file_name in html_files:
        if not os.path.exists(file_name):
            print(f'  SKIP {file_name} (not found)')
            continue
        
        print(f'\n{file_name}:')
        add_css_to_html(file_name)
        add_js_to_html(file_name)
    
    print('\n' + '=' * 60)
    print('DONE!')
    print('=' * 60)


if __name__ == '__main__':
    main()