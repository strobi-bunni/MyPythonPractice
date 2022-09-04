import json
import os
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring


def insert_data_in_elem(data, root_elem):
    if data['type'] == 'folder':
        list_item_elem = SubElement(root_elem, 'li', attrib={'class': 'bookmark-folder', 'id': f"id{data['id']}"})
        para_elem = SubElement(list_item_elem, 'p', attrib={'class': 'collapsible'})
        para_elem.text = data['name']
        sublist_elem = SubElement(list_item_elem, 'ul', attrib={'class': 'bookmark-list'})
        for child in data['children']:
            insert_data_in_elem(child, sublist_elem)
    else:
        list_item_elem = SubElement(root_elem, 'li',
                                    attrib={'class': 'bookmark-item', 'id': f"id{data['id']}"})
        link_elem = SubElement(list_item_elem, 'a', attrib={'href': data['url']})
        link_elem.text = data['name']


if __name__ == '__main__':
    bookmark_file_path = Path(os.environ['LOCALAPPDATA']) / 'Microsoft/Edge/User Data/Default/Bookmarks'
    with open(bookmark_file_path, 'r', encoding='utf-8') as f:
        d = json.load(f)['roots']

    root = Element('ul', attrib={'class': 'bookmark-list'})
    for item in d.values():
        insert_data_in_elem(item, root)

    xmlstr: str = tostring(root, encoding='utf-8', method='html').decode()
    output_file_path = Path('out/bookmark_backup.html')
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file_path, 'w', encoding='utf-8') as wf:
        wf.write(f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bookmark list</title>
            <meta charset="utf-8" />
            <style>
            {Path("./res/bookmark_backup.css").read_text(encoding="utf-8")}
            </style>
        </head>
        <body>
            {xmlstr}
            <script>
            {Path("./res/bookmark_backup.js").read_text(encoding="utf-8")}
        </script></body></html>
        ''')
