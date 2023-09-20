#!/usr/bin/env python
"""
마인크래프트(JE)의 파일들을 추출하는 코드
"""
import argparse
import json
import os
import re
import sys
from fnmatch import fnmatch
from pathlib import Path
from shutil import copy
from typing import Dict, Iterator, List, Optional, Tuple, TypedDict, Union


class ResourceInfo(TypedDict):
    hash: str
    size: int


T_AssetData = Dict[str, ResourceInfo]
T_PathLike = Union[str, os.PathLike]
# 시스템 타입에 맞춰서 마인크래프트 경로 설정
if sys.platform == "win32":
    # Windows
    MC_HOME_DIR = Path(os.getenv("APPDATA")) / ".minecraft/"
elif sys.platform == "darwin":
    # macOS
    MC_HOME_DIR = Path("~/Library/Application Support/minecraft/")
else:
    # Linux
    MC_HOME_DIR = Path("~/.minecraft/")

MC_ASSET_FILES_DIR = MC_HOME_DIR / "assets/objects/"  # 리소스 파일이 저장된 경로
MC_INDEX_FILES_DIR = MC_HOME_DIR / "assets/indexes/"  # 인덱스 파일이 저장된 경로


def get_latest_version() -> Optional[str]:
    """가장 최신 버전을 구한다.

    버전은 X.XX 형식이다.
    """
    re_version = re.compile(r"^(\d+)\.(\d+)$", re.I)
    x: List[Tuple[int, int]] = []
    for index_file_path in MC_INDEX_FILES_DIR.iterdir():
        if matches := re_version.match(index_file_path.stem):
            x.append((int(matches[1]), int(matches[2])))
    if re_version:
        latest_version_tuple = max(x)
        return f"{latest_version_tuple[0]}.{latest_version_tuple[1]}"


def get_asset_path(h: str) -> Path:
    """리소스 파일의 내부적으로 사용되는 경로를 구한다.
    (예시 : minecraft/sounds/dig/sand1.ogg)

    Parameters
    ----------
    h : str
        해시

    Returns
    -------
    p : Path
        리소스 파일의 경로
    """
    return MC_ASSET_FILES_DIR / h[:2] / h


def get_asset_index_data(version: str) -> T_AssetData:
    """인덱스 파일을 열어서 데이터를 가져온다.

    데이터 형식은 다음과 같다.

    ::

        {<리소스 내부 경로>: {"hash": <파일 해시>, "size": <파일 크기>} ...}
    """
    index_file = MC_INDEX_FILES_DIR / (version + ".json")  # 인덱스 파일
    with index_file.open(mode="r", encoding="utf-8") as f:
        return json.load(f)["objects"]  # 인덱스


def extract_resource(respath: str, output_folder: T_PathLike, asset_data: T_AssetData) -> Optional[Path]:
    """파일을 추출한다."""
    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True, parents=True)

    # 파일의 해시를 구한다.
    if resource_data := asset_data.get(respath):
        asset_file_hash = resource_data["hash"]

        # 원본 데이터 파일의 위치와 추출된 파일의 최종 경로를 구한다.
        original_data_path = get_asset_path(asset_file_hash)
        output_file_path = output_folder / respath

        # 파일을 복사하고 이름을 바꾼다.
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        copy(original_data_path, output_file_path.parent)

        # 복사된 파일은 이름이 바뀌지 않았다. 따라서 이름을 바꾼다.
        just_copied_file = output_file_path.parent / asset_file_hash
        just_copied_file.rename(output_file_path)

        return output_file_path


def query_items(asset_data: T_AssetData, path_filter: str = "*") -> Iterator[Tuple[str, ResourceInfo]]:
    for respath, resdata in sorted(asset_data.items()):
        if fnmatch(respath, path_filter):
            yield respath, resdata


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(title="Sub-commands", description="action", dest="subparser")

    parser_extract = subparsers.add_parser("extract", help="파일을 추출한다", description="1개 이상의 대상 파일을 추출한다")
    parser_extract.add_argument("path", nargs="*", type=str, help="파일의 경로", default=["*"])
    parser_extract.add_argument(
        "-mv", "--minecraft-version", type=str, help="마인크래프트 버전", metavar="X.XX", default=get_latest_version()
    )
    parser_extract.add_argument("-o", "--output", help="출력할 파일의 경로", required=True)

    parser_query = subparsers.add_parser("query", help="파일을 찾는다", description="대상 필터를 사용해서 파일을 찾는다")
    parser_query.add_argument("path", nargs="*", type=str, help="파일의 경로", default=["*"])
    parser_query.add_argument(
        "-mv", "--minecraft-version", type=str, help="마인크래프트 버전", metavar="X.XX", default=get_latest_version()
    )
    args = parser.parse_args()

    if args.subparser == "extract":
        if not args.minecraft_version:
            print("Cannot find Minecraft index file", file=sys.stderr)
            sys.exit(1)
        data = get_asset_index_data(args.minecraft_version)
        for p in args.path:
            for item in query_items(data, p):
                extract_resource(item[0], args.output, data)

    elif args.subparser == "query":
        if not args.minecraft_version:
            print("Cannot find Minecraft index file", file=sys.stderr)
            sys.exit(1)
        data = get_asset_index_data(args.minecraft_version)
        for p in args.path:
            for item in query_items(data, p):
                print(f'{item[0]},{item[1]["hash"]},{item[1]["size"]}')
