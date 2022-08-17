"""
이 스크립트는 Windows용 exe 파일의 PE 헤더를 읽어서 대상 아키텍처를 확인한다.

참고 문서: https://docs.microsoft.com/en-us/windows/win32/debug/pe-format#machine-types
"""
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file', metavar='EXE_FILE', type=str, help='대상 exe 파일')
args = parser.parse_args()

with open(args.file, 'rb') as target_file:
    # 헤더 위치를 찾는다
    target_file.seek(0x3C)
    pe_header_pos = int.from_bytes(target_file.read(4), 'little', signed=False)

    # PE 헤더로 이동한다.
    target_file.seek(pe_header_pos)
    # 4바이트를 버린다.
    target_file.read(4)

    # 머신 타입 확인
    machine_type_signature = target_file.read(2)
    if machine_type_signature == b'\x64\x86':
        print('AMD64')
    elif machine_type_signature == b'\x64\xaa':
        print('ARM64')
    elif machine_type_signature == b'\x4c\x01':
        print('i386')
    else:
        print('Unknown')
