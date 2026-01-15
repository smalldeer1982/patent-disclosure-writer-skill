#!/usr/bin/env python3
"""
state_manager.py - 专利交底书生成状态管理

管理专利交底书生成过程中的状态，支持断点续传。

使用方法:
    python state_manager.py --init
    python state_manager.py --get <key>
    python state_manager.py --set <key> <value>
    python state_manager.py --status
    python state_manager.py --reset

Exit codes:
    0: 成功
    1: 失败
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class GenerationState:
    """生成状态数据类"""
    version: str = "1.1.0"
    idea: str = ""
    patent_type: str = ""
    technical_field: str = ""
    keywords: List[str] = field(default_factory=list)
    completed_chapters: List[str] = field(default_factory=list)
    current_chapter: str = ""
    failed_chapters: List[str] = field(default_factory=list)
    figure_number: int = 1
    timestamp: str = ""
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationState":
        """从字典创建"""
        return cls(**data)

    def update_timestamp(self) -> None:
        """更新时间戳"""
        self.timestamp = datetime.now().isoformat()


class StateManager:
    """状态管理器"""

    STATE_FILE = ".patent-status.json"

    def __init__(self, working_dir: Path):
        self.working_dir = Path(working_dir)
        self.state_file = self.working_dir / self.STATE_FILE
        self.state = GenerationState()

    def exists(self) -> bool:
        """检查状态文件是否存在"""
        return self.state_file.exists()

    def load(self) -> bool:
        """加载状态"""
        if not self.exists():
            return False

        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            self.state = GenerationState.from_dict(data)
            return True
        except Exception as e:
            print(f"错误: 加载状态文件失败: {e}", file=sys.stderr)
            return False

    def save(self) -> bool:
        """保存状态"""
        try:
            self.state.update_timestamp()
            self.state_file.write_text(
                json.dumps(self.state.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            return True
        except Exception as e:
            print(f"错误: 保存状态文件失败: {e}", file=sys.stderr)
            return False

    def init(
        self,
        idea: str,
        patent_type: str,
        technical_field: str = "",
        keywords: Optional[List[str]] = None
    ) -> bool:
        """初始化状态"""
        self.state = GenerationState(
            idea=idea,
            patent_type=patent_type,
            technical_field=technical_field,
            keywords=keywords or [],
            figure_number=1
        )
        return self.save()

    def get(self, key: str) -> Optional[Any]:
        """获取状态值"""
        if not self.load():
            return None

        if not hasattr(self.state, key):
            print(f"错误: 无效的状态键: {key}", file=sys.stderr)
            return None

        return getattr(self.state, key)

    def set(self, key: str, value: Any) -> bool:
        """设置状态值"""
        if not self.load():
            # 如果状态文件不存在，创建新状态
            self.state = GenerationState()

        if not hasattr(self.state, key):
            print(f"错误: 无效的状态键: {key}", file=sys.stderr)
            return False

        setattr(self.state, key, value)
        return self.save()

    def mark_completed(self, chapter: str) -> bool:
        """标记章节完成"""
        if not self.load():
            return False

        if chapter not in self.state.completed_chapters:
            self.state.completed_chapters.append(chapter)

        return self.save()

    def mark_failed(self, chapter: str, error: str = "") -> bool:
        """标记章节失败"""
        if not self.load():
            return False

        if chapter not in self.state.failed_chapters:
            self.state.failed_chapters.append(chapter)

        if error and error not in self.state.errors:
            self.state.errors.append(error)

        return self.save()

    def set_current_chapter(self, chapter: str) -> bool:
        """设置当前章节"""
        if not self.load():
            return False

        self.state.current_chapter = chapter
        return self.save()

    def increment_figure_number(self, count: int = 1) -> int:
        """增加附图编号"""
        if not self.load():
            return self.state.figure_number

        self.state.figure_number += count
        self.save()
        return self.state.figure_number

    def reset(self) -> bool:
        """重置状态"""
        if self.exists():
            try:
                self.state_file.unlink()
            except Exception as e:
                print(f"警告: 删除状态文件失败: {e}", file=sys.stderr)
                return False

        self.state = GenerationState()
        return True

    def status(self) -> None:
        """显示状态"""
        if not self.load():
            print("状态文件不存在")
            return

        print("=" * 50)
        print("专利交底书生成状态")
        print("=" * 50)

        print(f"版本: {self.state.version}")
        print(f"专利类型: {self.state.patent_type or '(未设置)'}")
        print(f"技术领域: {self.state.technical_field or '(未设置)'}")
        print(f"关键词: {', '.join(self.state.keywords) or '(未设置)'}")
        print(f"当前章节: {self.state.current_chapter or '(未设置)'}")
        print(f"附图编号: {self.state.figure_number}")

        if self.state.completed_chapters:
            print(f"\n已完成章节 ({len(self.state.completed_chapters)}):")
            for chapter in self.state.completed_chapters:
                print(f"  ✓ {chapter}")
        else:
            print("\n已完成章节: 无")

        if self.state.failed_chapters:
            print(f"\n失败章节 ({len(self.state.failed_chapters)}):")
            for chapter in self.state.failed_chapters:
                print(f"  ✗ {chapter}")
        else:
            print("\n失败章节: 无")

        if self.state.errors:
            print(f"\n错误信息 ({len(self.state.errors)}):")
            for error in self.state.errors:
                print(f"  - {error}")

        if self.state.timestamp:
            print(f"\n最后更新: {self.state.timestamp}")

        print("=" * 50)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="专利交底书生成状态管理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 初始化状态
    python state_manager.py --init --idea "创新想法" --patent-type "发明专利"

    # 查看状态
    python state_manager.py --status

    # 获取特定值
    python state_manager.py --get figure_number

    # 设置特定值
    python state_manager.py --set current_chapter "03"

    # 标记章节完成
    python state_manager.py --mark-completed "03"

    # 重置状态
    python state_manager.py --reset

Exit codes:
    0: 成功
    1: 失败
        """
    )

    parser.add_argument(
        "--dir",
        type=str,
        default=".",
        help="工作目录 (默认: 当前目录)"
    )

    # 操作组（互斥）
    operation_group = parser.add_mutually_exclusive_group(required=True)

    operation_group.add_argument(
        "--init",
        action="store_true",
        help="初始化状态文件"
    )

    operation_group.add_argument(
        "--get",
        type=str,
        metavar="KEY",
        help="获取状态值"
    )

    operation_group.add_argument(
        "--set",
        type=str,
        metavar="KEY",
        help="设置状态值"
    )

    operation_group.add_argument(
        "--status",
        action="store_true",
        help="显示当前状态"
    )

    operation_group.add_argument(
        "--reset",
        action="store_true",
        help="重置状态"
    )

    operation_group.add_argument(
        "--mark-completed",
        type=str,
        metavar="CHAPTER",
        help="标记章节完成"
    )

    operation_group.add_argument(
        "--mark-failed",
        type=str,
        metavar="CHAPTER",
        help="标记章节失败"
    )

    # 初始化参数
    parser.add_argument("--idea", type=str, help="创新想法")
    parser.add_argument("--patent-type", type=str, help="专利类型")
    parser.add_argument("--technical-field", type=str, help="技术领域")
    parser.add_argument("--keywords", type=str, help="关键词（逗号分隔）")
    parser.add_argument("--value", type=str, help="设置值（配合 --set 使用）")
    parser.add_argument("--error", type=str, help="错误信息（配合 --mark-failed 使用）")

    args = parser.parse_args()

    # 创建状态管理器
    manager = StateManager(Path(args.dir))

    # 执行操作
    success = False

    if args.init:
        # 初始化状态
        keywords = []
        if args.keywords:
            keywords = [k.strip() for k in args.keywords.split(",")]

        if not args.idea or not args.patent_type:
            print("错误: --init 需要 --idea 和 --patent-type", file=sys.stderr)
            sys.exit(1)

        success = manager.init(
            idea=args.idea,
            patent_type=args.patent_type,
            technical_field=args.technical_field or "",
            keywords=keywords
        )
        if success:
            print(f"状态文件已创建: {manager.state_file}")

    elif args.get:
        # 获取值
        value = manager.get(args.get)
        if value is not None:
            if isinstance(value, list):
                print(json.dumps(value, ensure_ascii=False))
            else:
                print(value)
            success = True
        else:
            sys.exit(1)

    elif args.set:
        # 设置值
        if args.value is None:
            print("错误: --set 需要 --value", file=sys.stderr)
            sys.exit(1)

        # 尝试解析为 JSON
        try:
            value = json.loads(args.value)
        except json.JSONDecodeError:
            value = args.value

        success = manager.set(args.set, value)
        if success:
            print(f"已设置: {args.set} = {value}")

    elif args.status:
        # 显示状态
        manager.status()
        success = True

    elif args.reset:
        # 重置状态
        if manager.exists():
            confirm = input(f"确认删除状态文件? {manager.state_file} [y/N]: ")
            if confirm.lower() == 'y':
                success = manager.reset()
                if success:
                    print("状态已重置")
            else:
                print("取消操作")
                sys.exit(0)
        else:
            print("状态文件不存在，无需重置")
            success = True

    elif args.mark_completed:
        # 标记章节完成
        success = manager.mark_completed(args.mark_completed)
        if success:
            print(f"已标记章节完成: {args.mark_completed}")

    elif args.mark_failed:
        # 标记章节失败
        success = manager.mark_failed(args.mark_failed, args.error or "")
        if success:
            print(f"已标记章节失败: {args.mark_failed}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
