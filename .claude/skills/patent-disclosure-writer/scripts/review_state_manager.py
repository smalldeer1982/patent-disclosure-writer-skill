#!/usr/bin/env python3
"""
审核状态管理脚本

管理专利审核流程的状态，包括审核进度、投票结果、修改建议等。
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any

# 设置 UTF-8 编码输出（Windows 兼容）
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

@dataclass
class ReviewState:
    """审核状态数据类"""
    version: str = "2.0.0"
    stage: str = ""
    chapters: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, disputed
    vote_result: Optional[Dict[str, Any]] = None
    modifications: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = ""

def get_status_file(stage: str) -> Path:
    """获取审核状态文件路径"""
    return Path.cwd() / f".review-status-{stage}.json"

def read_status(stage: str) -> Optional[ReviewState]:
    """读取审核状态"""
    status_file = get_status_file(stage)
    if not status_file.exists():
        return None

    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return ReviewState(**data)
    except Exception as e:
        print(f"Error reading status file: {e}", file=sys.stderr)
        return None

def write_status(stage: str, state: ReviewState) -> bool:
    """写入审核状态"""
    status_file = get_status_file(stage)
    try:
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(state), f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error writing status file: {e}", file=sys.stderr)
        return False

def init_status(stage: str, chapters: List[str]) -> ReviewState:
    """初始化审核状态"""
    from datetime import datetime
    state = ReviewState(
        stage=stage,
        chapters=chapters,
        status="pending",
        timestamp=datetime.now().isoformat()
    )
    write_status(stage, state)
    return state

def update_status(stage: str, **kwargs) -> bool:
    """更新审核状态"""
    state = read_status(stage)
    if state is None:
        return False

    for key, value in kwargs.items():
        if hasattr(state, key):
            setattr(state, key, value)

    from datetime import datetime
    state.timestamp = datetime.now().isoformat()
    return write_status(stage, state)

def print_status(stage: str) -> None:
    """打印审核状态"""
    state = read_status(stage)
    if state is None:
        print(f"No status found for stage: {stage}")
        return

    print(f"=== Review Status: {state.stage} ===")
    print(f"Chapters: {', '.join(state.chapters)}")
    print(f"Status: {state.status}")
    if state.vote_result:
        print(f"Vote Result: {state.vote_result}")
    print(f"Modifications: {len(state.modifications)}")
    print(f"Timestamp: {state.timestamp}")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='专利审核状态管理')
    parser.add_argument('--init', metavar='STAGE', help='初始化审核状态')
    parser.add_argument('--chapters', help='章节列表（逗号分隔）')
    parser.add_argument('--get', metavar='KEY', help='获取状态值')
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='设置状态值')
    parser.add_argument('--status', metavar='STAGE', help='显示审核状态')
    parser.add_argument('--update', metavar='STAGE', help='更新审核状态')

    args = parser.parse_args()

    if args.init:
        chapters = args.chapters.split(',') if args.chapters else []
        state = init_status(args.init, chapters)
        print(f"Initialized review status for stage: {args.init}")
        return 0

    if args.status:
        print_status(args.status)
        return 0

    if args.get:
        state = read_status(args.status or args.update)
        if state and hasattr(state, args.get):
            value = getattr(state, args.get)
            print(json.dumps(value, ensure_ascii=False))
        return 0

    if args.set:
        key, value = args.set
        # 尝试解析JSON值
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass  # 保持为字符串

        if update_status(args.update, **{key: value}):
            print(f"Updated: {key} = {value}")
            return 0
        else:
            print(f"Failed to update status", file=sys.stderr)
            return 1

    parser.print_help()
    return 1

if __name__ == '__main__':
    sys.exit(main())
