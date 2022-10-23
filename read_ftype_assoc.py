r"""
윈도우 파일 확장자 연결 확인

윈도우에서는 [파일 확장자] -- [파일 타입] -- [연결 프로그램] 순으로 파일이 연결된다.

https://learn.microsoft.com/en-us/windows/win32/shell/fa-file-types

예를 들어 윈도우용 Python을 설치하면 등록되는 '.py' 확장자는 'Python.File' 파일 타입과 연결된다.
이를 확인하는 명령어는 assoc이다.

::

    C:\Windows\System32>assoc .py
    .py=Python.File

또한 'Python.File' 파일 타입은 py.exe 프로그램과 연결된다. 이를 확인하는 명령어는 ftype이다.

::

    C:\Windows\System32>ftype Python.File
    Python.File="C:\Windows\py.exe" "%L" %*

만약에 mycode.py를 실행한다고 할 경우 윈도우는 레지스트리를 검색해서
.py 확장자와 연결되는 Python.File 파일 타입을 찾는다.
이후 다시 레지스트리를 검색해서 Python.File 파일 타입과 연결되는
py.exe 프로그램을 찾아 실행한다.

이 코드에서는 ftype와 assoc 명령어 실행 결과를 사용해서
어느 확장자에 어느 프로그램이 연결되었는지 확인한다.
"""
import sqlite3
from subprocess import run

# ftype와 assoc 명령어를 실행한다.
ftype_result_stdout = run('ftype'.split(), shell=True, capture_output=True).stdout.decode()
assoc_result_stdout = run('assoc'.split(), shell=True, capture_output=True).stdout.decode()

# '=' 기준으로 분할한다.
# 윈도우 기본 줄바꿈 기호는 \r\n임에 주의할 것
ftype_mapping = [((x := s.partition('='))[0], x[2]) for s in ftype_result_stdout.split('\r\n')]
assoc_mapping = [((x := s.partition('='))[0], x[2]) for s in assoc_result_stdout.split('\r\n')]

# 인메모리 데이터베이스를 만든다.
conn = sqlite3.connect(':memory:')
cur = conn.cursor()

# ftype와 assoc 데이터를 인메모리 데이터베이스에 입력한다.
cur.execute('CREATE TABLE TableAssoc (Ext, FileType);')
cur.execute('CREATE TABLE TableFType (FileType, OpenCommandString);')
cur.executemany('INSERT INTO TableAssoc VALUES (?,?);', assoc_mapping)
cur.executemany('INSERT INTO TableFType VALUES (?,?);', ftype_mapping)

# 테이블을 JOIN시켜 Ext---FileType---OpenCommandString 관계를 만든다.
# 뷰로 만드는 이유는 다음에 쿼리를 다시 쓰기 불편하기 때문이다.
cur.execute('''CREATE View ViewAssocFType AS
SELECT Ext, TableAssoc.FileType, OpenCommandString
FROM TableAssoc LEFT JOIN TableFType
ON TableAssoc.FileType = TableFType.FileType;''')

# Ext, FileType, OpenCommandString이 모두 있는 경우
cur.execute('SELECT * FROM ViewAssocFType WHERE OpenCommandString NOT NULL;')
print('File Extension Mapping')
for item in cur:
    print(' => '.join(item))

# Ext, FileType는 있지만 OpenCommandString이 없는(NULL)인 경우(Ftype에 연결된 Assoc이 없을 때)
# 이전의 뷰를 재활용한다.
# 여기에는 '.dll => dllfile'와 같은 유명 확장자도 있는데
# 아무래도 assoc로 확인할 수 없는 방식으로 레지스트리에 등록된 것으로 보인다.
cur.execute('SELECT Ext, FileType FROM ViewAssocFType WHERE OpenCommandString IS NULL;')
print('\nOrphaned Assoc')
for item in cur:
    print(' => '.join(item))

# Ext는 없지만 FileType와 OpenCommandString이 있는 경우(Assoc에 연결된 Ftype이 없을 때)
# SQLite에는 OUTER JOIN이 없기 때문에 LEFT JOIN을 한 번 더 해야 한다.
cur.execute('''SELECT FileType, OpenCommandString FROM (
    SELECT Ext, TableFType.FileType, OpenCommandString
    FROM TableFType LEFT JOIN TableAssoc
    ON TableFType.FileType = TableAssoc.FileType
) WHERE Ext IS NULL;''')
print('\nOrphaned FType')
for item in cur:
    print(' => '.join(item))

conn.close()
