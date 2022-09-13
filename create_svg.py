"""
Creates Pascal's Triangle SVG file with built-in xml module.
"""
import math
from numbers import Real
from pathlib import Path
from typing import Any, Dict, Optional
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element, SubElement, tostring


def add_rect(parent: Element, x: Real, y: Real, width: Real, height: Real,
             options: Optional[Dict[str, Any]] = None) -> Element:
    if options is None:
        options = {}
    options = {k: str(v) for (k, v) in options.items()}
    return SubElement(parent, 'rect',
                      attrib={'x': str(x), 'y': str(y), 'width': str(width), 'height': str(height), **options})


def add_group(parent: Element, options: Optional[Dict[str, Any]] = None) -> Element:
    if options is None:
        options = {}
    options = {k: str(v) for (k, v) in options.items()}
    return SubElement(parent, 'g', attrib=options)


def add_text(parent: Element, x: Real, y: Real, text: Any,
             options: Optional[Dict[str, Any]] = None) -> Element:
    if options is None:
        options = {}
    options = {k: str(v) for (k, v) in options.items()}
    elem = SubElement(parent, 'text',
                      attrib={'x': str(x), 'y': str(y), **options})
    elem.text = str(text)
    return elem


if __name__ == '__main__':
    block_size = 50
    margin_size = 25

    total_rows = 12
    root = Element('svg', attrib={'width': str(block_size * total_rows + 2 * margin_size),
                                  'height': str(block_size * total_rows + 2 * margin_size),
                                  'xmlns': "http://www.w3.org/2000/svg"})
    style_tag = SubElement(root, 'style')
    style_tag.text = '''
    text.number {font-size: 24px; text-anchor: middle; alignment-baseline: middle;}
    rect.block {stroke: black; stroke-width: 2; fill: white;}
    '''
    group_blocks = add_group(root, {'id': 'blocks'})
    group_texts = add_group(root, {'id': 'texts'})
    for row in range(total_rows):
        for col in range(row + 1):
            add_rect(group_blocks,
                     col * block_size + (total_rows - row) * block_size // 2,
                     margin_size + row * block_size,
                     block_size,
                     block_size,
                     {'class': 'block'})
            add_text(group_texts,
                     margin_size + col * block_size + (total_rows - row) * block_size // 2,
                     2 * margin_size + row * block_size,
                     math.comb(row, col),
                     {'class': 'number'})

    output_file_path = Path('out/output.svg')
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_file_path.write_bytes(parseString(tostring(root)).toprettyxml(encoding='utf-8'))
