"""
URL Analysis

다음 코드는 URL의 각 요소를 분석한다. URL의 쿼리 문자열에 어떤 요소가 포함되어 있는지 더 보기 좋게 표시한다.
이를 사용해서 URL의 원치 않은 트래킹 정보를 지울 수 있다.

사용 방법

::

    $ url_analysis.py <url>

이 때 url은 반드시 "따옴표"로 감싸야 한다. 안 그러면 하나의 문자열로 인식하지 못할 수 있다.
"""
import json
import sys
from urllib.parse import unquote, urlparse

url = sys.argv[1]
parse_result = urlparse(url)

# 쿼리 문자열을 딕셔너리로 변환
if query_string := parse_result.query:
    queries = query_string.split('&')
    query_partitions = [part.partition('=') for part in queries]
else:
    query_partitions = []
query_dict = {x[0]: unquote(x[2]) for x in query_partitions}

analysis_result = {
    'url': url,
    'scheme': parse_result.scheme or '',
    'netloc': parse_result.netloc or '',
    'netloc_details': {
        'username': parse_result.username or '',
        'password': parse_result.password or '',
        'hostname': parse_result.hostname or '',
        'port': parse_result.port or ''
    },
    'path': unquote(parse_result.path or ''),
    'params': parse_result.params or '',
    'query': query_dict,
    'fragment': parse_result.fragment or ''
}
print(json.dumps(analysis_result, ensure_ascii=False, indent=4))
