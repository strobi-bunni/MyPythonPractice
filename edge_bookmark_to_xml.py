#!/usr/bin/env python
"""
다음 스크립트는 Microsoft Edge의 북마크를 XML 형식으로 내보낸다.
"""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element, SubElement, tostring

TIMESTAMP_EPOCH = datetime(1601, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def convert_timestamp(t: str) -> str:
    # 타임스탬프: 1601-01-01T00:00:00Z로부터 경과한 마이크로초 단위의 시간
    ts = int(t)
    return (TIMESTAMP_EPOCH + timedelta(seconds=(ts // 1000000), microseconds=(ts % 1000000))) \
        .strftime('%Y-%m-%dT%H:%M:%SZ')


def insert_data_in_elem(data: dict, root_elem: Element):
    if data['type'] == 'folder':
        folder_elem = SubElement(root_elem, 'BookmarkFolder',
                                 attrib={'name': data['name'], 'id': data['id'],
                                         'date_added': convert_timestamp(data['date_added']),
                                         'date_modified': convert_timestamp(data['date_modified'])})

        for child in data['children']:
            insert_data_in_elem(child, folder_elem)
    else:
        SubElement(root_elem, 'Bookmark',
                   attrib={'id': data['id'], 'date_added': convert_timestamp(data['date_added']), 'href': data['url']},
                   ).text = data['name']


if __name__ == '__main__':
    bookmark_file_path = Path(os.environ['LOCALAPPDATA']) / 'Microsoft/Edge/User Data/Default/Bookmarks'
    with open(bookmark_file_path, 'r', encoding='utf-8') as f:
        d = json.load(f)['roots']

    root = Element('BookmarkBackup')
    for item in d.values():
        insert_data_in_elem(item, root)

    xmlstr = parseString(tostring(root)).toprettyxml(encoding='utf-8')
    output_file_path = Path('out/bookmark_backup.xml')
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_file_path.write_bytes(xmlstr)
