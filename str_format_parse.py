#!/usr/bin/env python
r"""
This code parses the `format specifier`_ used in the str.format method.

.. _`format specifier` : https://docs.python.org/3/library/string.html#format-specification-mini-language
"""
import re
from textwrap import dedent
from typing import Match, NamedTuple, Optional

# Symbols used in format specifier.
ALIGN_CODE = {"<": "LEFT", ">": "RIGHT", "^": "CENTER", "=": "PAD_DIGIT"}
SIGN_CODE = {"+": "FORCE_POSITIVE", "-": "HIDE_POSITIVE", " ": "BLANK_POSITIVE"}
GROUP_CODE = {"_": "UNDERLINE", ",": "COMMA"}
TYPE_CODE = {
    "b": "BINARY",
    "c": "CHAR",
    "d": "DECIMAL",
    "e": "EXPONENTIAL",
    "E": "EXPONENTIAL_UPPER",
    "f": "FLOAT",
    "F": "FLOAT_UPPER",
    "g": "GENERAL",
    "G": "GENERAL_UPPER",
    "n": "NUMBER",
    "o": "OCTAL",
    "s": "STRING",
    "x": "HEXADECIMAL",
    "X": "HEXADECIMAL_UPPER",
    "%": "PERCENT",
}

# Regular expression of the format specifier
FMT_SPEC_REGEX = re.compile(
    r"^(?:(?P<fill>.)?(?P<align>[<>=^]))?(?P<sign>[ +\-])?(?P<base_prefix>#)?(?P<leading_zeros>0)?"
    r"(?P<width>\d+)?(?P<grouping_option>[_,])?(?P<precision>\.\d+)?(?P<type>[bcdeEfFgGnosxX%])?$"
)


# Tuple to store results
class StrFormat(NamedTuple):
    fill: Optional[str]
    align: Optional[str]
    sign: Optional[str]
    base_prefix: bool
    leading_zeros: bool
    width: Optional[int]
    grouping_option: Optional[str]
    precision: Optional[int]
    type: Optional[str]
    raw_matches: Match[str]


def parse_format_spec(s: str) -> StrFormat:
    """Parses the format specifier using regular expression."""
    if matches := FMT_SPEC_REGEX.match(s):
        return StrFormat(
            matches["fill"],
            ALIGN_CODE[matches["align"]] if matches["align"] else None,
            SIGN_CODE[matches["sign"]] if matches["sign"] else None,
            bool(matches["base_prefix"]),
            bool(matches["leading_zeros"]),
            int(matches["width"]) if matches["width"] else None,
            GROUP_CODE[matches["grouping_option"]] if matches["grouping_option"] else None,
            int(matches["precision"][1:]) if matches["precision"] else None,
            TYPE_CODE[matches["type"]] if matches["type"] else None,
            matches,
        )
    else:
        raise ValueError("Invalid format specifier.")


if __name__ == "__main__":
    # Format specifier and value to display
    my_fmt_spec = "#011_x"
    my_value = 123456789

    # Format the value using the format specifier.
    formatted_value = f"{my_value:{my_fmt_spec}}"
    parsed_fmt_spec = parse_format_spec(my_fmt_spec)
    raw_matches = parsed_fmt_spec.raw_matches

    # Show the results.
    print(
        dedent(
            f"""
          Format specifier    {my_fmt_spec!r}
          Value               {my_value!r} ({type(my_value)})
          Formatted value     {formatted_value!r}
      
          Option              Value               Raw value
          ------------------------------------------------------------
          Fill char           {parsed_fmt_spec.fill!s:<20}{raw_matches["fill"]!r}
          Alignment           {parsed_fmt_spec.align!s:<20}{raw_matches["align"]!r}
          Positive sign       {parsed_fmt_spec.sign!s:<20}{raw_matches["sign"]!r}
          Use base prefix     {parsed_fmt_spec.base_prefix!s:<20}{raw_matches["base_prefix"]!r}
          Use leading zeros   {parsed_fmt_spec.leading_zeros!s:<20}{raw_matches["leading_zeros"]!r}
          Minimum width       {parsed_fmt_spec.width!s:<20}{raw_matches["width"]!r}
          Grouping method     {parsed_fmt_spec.grouping_option!s:<20}{raw_matches["grouping_option"]!r}
          Precision           {parsed_fmt_spec.precision!s:<20}{raw_matches["precision"]!r}
          Type                {parsed_fmt_spec.type!s:<20}{raw_matches["type"]!r}"""
        )
    )
