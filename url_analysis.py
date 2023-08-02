#!/usr/bin/env python
"""
URL Analysis

다음 코드는 URL의 각 요소를 분석한다. URL의 쿼리 문자열에 어떤 요소가 포함되어 있는지 더 보기 좋게 표시한다.
이를 사용해서 URL의 원치 않은 트래킹 정보를 지울 수 있다.

사용 방법

::

    $ python ./url_analysis.py "http://www.example.com"
    ---- 또는 ----
    $ echo "http://www.example.com" | python ./url_analysis.py

이 때 url은 반드시 "따옴표"로 감싸야 한다. 안 그러면 하나의 문자열로 인식하지 못할 수 있다.
"""
import argparse
import json
import sys
from urllib.parse import unquote, urlparse


def parse_url(url: str) -> dict:
    parse_result = urlparse(url)

    # 쿼리 문자열을 딕셔너리로 변환
    if query_string := parse_result.query:
        queries = query_string.split("&")
        query_partitions = [part.partition("=") for part in queries]
    else:
        query_partitions = []
    query_dict = {x[0]: unquote(x[2]) for x in query_partitions}

    return {
        "url": url,
        "scheme": parse_result.scheme or "",
        "netloc": parse_result.netloc or "",
        "netloc_details": {
            "username": parse_result.username or "",
            "password": parse_result.password or "",
            "hostname": parse_result.hostname or "",
            "port": parse_result.port or "",
        },
        "path": unquote(parse_result.path or ""),
        "params": parse_result.params or "",
        "query": query_dict,
        "fragment": parse_result.fragment or "",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str, nargs="?", help="분석할 URL")
    args = parser.parse_args()

    args_url = args.url
    if not args.url:
        args_url = sys.stdin.read()

    print(json.dumps(parse_url(args_url.strip()), ensure_ascii=False, indent=4), end="")
