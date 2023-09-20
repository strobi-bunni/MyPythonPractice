#!/usr/bin/env python
"""
Messing up string with unicode
"""
import random
import unicodedata
from typing import Dict, Mapping, Optional

# Create unnormalization map: {NFKC_normalized_char: unnormalized_chars}
ascii_char_mapping: Dict[str, str] = dict.fromkeys((chr(i) for i in range(32, 127)), "")
for i in range(0x4FFFF):
    char = chr(i)
    normalized_char = unicodedata.normalize("NFKC", char)
    if normalized_char in ascii_char_mapping:
        ascii_char_mapping[normalized_char] += char


def randomize_string(s: str, mapping: Mapping[str, str], seed: Optional[int] = None) -> str:
    r = random.Random(seed)
    return "".join(r.choice(mapping.get(c, c)) for c in s)


# print this script with unnormalization
with open(__file__, "r", encoding="utf-8") as f:
    print(randomize_string(f.read(), ascii_char_mapping, seed=12345))
