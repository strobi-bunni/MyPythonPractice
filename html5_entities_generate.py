"""
이 문서는 HTML 엔티티 정보를 출력하는 마크다운 문서를 생성한다.
"""
import html.entities
import unicodedata

f = open('html5_entities.md', 'w', encoding='utf-8')


def get_unicode_code_of_str(s: str) -> str:
    return ' '.join(f'U+{ord(c):04X}' for c in s)


def get_unicode_name_of_str(s: str) -> str:
    return ', '.join(get_unicode_name(c) for c in s)


def get_unicode_name(s: str) -> str:
    try:
        name = unicodedata.name(s)
    except ValueError:
        name = f'<{ord(s):04X}>'
    return name


def fix_entity(s: str) -> str:
    if s.endswith(';'):
        return '&' + s
    else:
        return '&' + s + ';'


f.write('''
<!-- Automatically generated table. do not edit it -->

|Entity|Unicode|Name|Char|
|----|----|----|----|
''')

for (entity_name, char) in html.entities.html5.items():
    f.write(f'|{entity_name}|{get_unicode_code_of_str(char)}'
            f'|{get_unicode_name_of_str(char)}|{fix_entity(entity_name)}|\n')

f.close()
