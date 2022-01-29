"""
해당 폴더 안의 모든 하위 폴더에서 __pycache__ 폴더를 지운다.

이 작업은 당신의 프로젝트를 파괴하지는 않겠지만(아마도...)
Python 바이트코드를 다시 컴파일해야 하므로 다시 실행하는 데 다시 실행하는 데 조금 오래 걸릴 것이다.
"""

import sys
from pathlib import Path
from shutil import rmtree

if len(sys.argv) != 2:
    print('Invalid parameter.\nUSAGE: delete_pycache.py <TARGET_FOLDER_PATH>')
    exit(1)

path = Path(sys.argv[1])
print(f'Deleting __pycache__ folders from every subdirectory of {path!s}?\nTHIS JOB CANNOT BE UNDONE!\n[Y]es | [N]o')
confirm = input('> ')

# find venv
venv_folders = [p.parent for p in path.glob('**/pyvenv.cfg')]

if confirm.strip().lower() in ['y', 'yes']:
    for pycache_folder in path.glob('**/__pycache__/'):
        # do not delete __pycache__ from venv folder
        if all((parent not in venv_folders) for parent in pycache_folder.parents):
            print(f'{pycache_folder!s} is deleted')
            rmtree(pycache_folder)
