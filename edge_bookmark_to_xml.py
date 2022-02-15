import json
import os
from pathlib import Path
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element, SubElement, tostring


def insert_data_in_elem(data, root_elem):
    if data['type'] == 'folder':
        folder_elem = SubElement(root_elem, 'BookmarkFolder',
                                 attrib={'name': data['name'], 'id': data['id'], 'date_added': data['date_added'],
                                         'date_modified': data['date_modified']})

        for child in data['children']:
            insert_data_in_elem(child, folder_elem)
    else:
        SubElement(root_elem, 'Bookmark',
                   attrib={'id': data['id'], 'date_added': data['date_added'], 'href': data['url']},
                   ).text = data['name']


if __name__ == '__main__':
    bookmark_file_path = Path(os.environ['LOCALAPPDATA']) / 'Microsoft/Edge/User Data/Default/Bookmarks'
    with open(bookmark_file_path, 'r', encoding='utf-8') as f:
        d = json.load(f)['roots']

    root = Element('BookmarkBackup')
    for item in d.values():
        insert_data_in_elem(item, root)

    xmlstr = parseString(tostring(root)).toprettyxml(encoding='utf-8')
    with open('./sandbox/bookmark_backup.xml', 'wb') as wf:
        wf.write(xmlstr)
