"""
다음은 터미널 내용을 읽는 Python 코드 예제이다.
"""
from subprocess import PIPE, Popen, run

# 터미널 설정. 다음은 한글 Windows 기준이다.
terminal_encoding = 'cp949'
terminal_newline_char = '\r\n'  # 새 줄 문자

if __name__ == '__main__':
    command = 'dir'  # 실행할 명령어

    # 1. Popen 클래스 사용
    with Popen(command, shell=True, stdout=PIPE).stdout as pipe:
        output = pipe.read()

        # 뒤의 replace 메서드는 터미널의 개행 문자(CRLF)를 일반 개행 문자(LF)로 바꾸기 위해서이다.
        print(output.decode(terminal_encoding).replace(terminal_newline_char, '\n'))

    # 2. 더 쉬운 방법
    # encoding 키워드 인자를 지정하면 터미널 줄바꿈(Windows 기준 '\r\n')을 사용하지 않고
    # 일반 줄바꿈 '\n'을 사용한다.
    run_stdout = run(command, shell=True, capture_output=True, encoding=terminal_encoding).stdout
    print(run_stdout)
