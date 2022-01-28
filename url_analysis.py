"""
URL의 각 요소를 분석함

usage: url_analysis.py <url>
"""
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

# 머리열의 너비 구하기
field_length = max(
    max((len(x) for x in query_dict.keys()), default=0) + 2,  # query 키의 최대 길이(+2한 이유는 인덴트 2칸)
    10)  # query가 없을 때 열의 최대 길이(len("  username"))

print(f'{"scheme":<{field_length}} : {parse_result.scheme or ""}')
print(f'{"netloc":<{field_length}} : {parse_result.netloc or ""}')
print(f'{"  username":<{field_length}} : {parse_result.username or ""}')
print(f'{"  password":<{field_length}} : {parse_result.password or ""}')
print(f'{"  hostname":<{field_length}} : {parse_result.hostname or ""}')
print(f'{"  port":<{field_length}} : {parse_result.port or ""}')
print(f'{"path":<{field_length}} : {unquote(parse_result.path or "")}')
print(f'{"params":<{field_length}} : {parse_result.params or ""}')
print(f'{"query":<{field_length}} : ')
for query_key, query_value in query_dict.items():
    print(f'{"  " + query_key:<{field_length}} : {query_value or ""}')
print(f'{"fragment":<{field_length}} : {parse_result.fragment or ""}')
