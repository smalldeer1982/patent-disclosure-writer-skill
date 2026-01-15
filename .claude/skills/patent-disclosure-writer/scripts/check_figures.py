#!/usr/bin/env python3
"""
check_figures.py - 检查附图编号连续性

扫描章节文件中的附图编号，验证编号是否连续。

使用方法:
    python check_figures.py --dir <directory> --verbose

Exit codes:
    0: 编号连续
    12: 发现跳号
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple


@dataclass
class FigureInfo:
    """附图信息"""
    number: int
    file: str
    title: str = ""

    def __str__(self) -> str:
        if self.title:
            return f"图{self.number} ({self.file}) - {self.title}"
        return f"图{self.number} ({self.file})"


@dataclass
class CheckResult:
    """检查结果数据类"""
    success: bool
    total_figures: int = 0
    figures: List[FigureInfo] = field(default_factory=list)
    gaps: List[Tuple[int, int]] = field(default_factory=list)  # (缺失编号, 期望位置)
    duplicates: List[int] = field(default_factory=list)

    def add_figure(self, figure: FigureInfo) -> None:
        """添加附图"""
        self.figures.append(figure)
        self.total_figures += 1

    def add_gap(self, missing_number: int, position: int) -> None:
        """添加跳号"""
        self.gaps.append((missing_number, position))
        self.success = False

    def add_duplicate(self, number: int) -> None:
        """添加重复编号"""
        if number not in self.duplicates:
            self.duplicates.append(number)
            self.success = False


class FigureChecker:
    """附图编号检查器"""

    # 附图标记模式: #### 附图X：[标题]
    FIGURE_PATTERN = re.compile(r'^####\s*附图(\d+)：\s*(.*)')

    # 可能的附图模式（兼容格式）
    ALTERNATIVE_PATTERNS = [
        re.compile(r'图(\d+)[:：]'),  # 图1：标题
        re.compile(r'Figure\s*(\d+)'),  # Figure 1
    ]

    def __init__(self, directory: Path, verbose: bool = False):
        self.directory = Path(directory)
        self.verbose = verbose
        self.result = CheckResult(success=True)

    def log(self, message: str) -> None:
        """输出日志"""
        if self.verbose:
            print(f"  {message}")

    def check(self) -> CheckResult:
        """执行检查"""
        print(f"检查目录: {self.directory}")
        print("-" * 50)

        # 扫描所有章节文件
        chapter_files = self._find_chapter_files()
        if not chapter_files:
            print("⚠ 未找到任何章节文件")
            return self.result

        # 扫描附图
        for file_path in chapter_files:
            self._scan_file(file_path)

        # 分析结果
        self._analyze_figures()

        return self._print_result()

    def _find_chapter_files(self) -> List[Path]:
        """查找所有章节文件"""
        files = []
        for pattern in ["[0-9][0-9]_*.md", "专利申请技术交底书_*.md"]:
            files.extend(self.directory.glob(pattern))
        return sorted(files)

    def _scan_file(self, file_path: Path) -> None:
        """扫描单个文件"""
        self.log(f"扫描: {file_path.name}")

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split('\n')

            for line in lines:
                # 尝试匹配标准格式
                match = self.FIGURE_PATTERN.match(line.strip())
                if match:
                    number = int(match.group(1))
                    title = match.group(2).strip()
                    self.result.add_figure(FigureInfo(number, file_path.name, title))
                    self.log(f"  ✓ 发现附图: 图{number} - {title}")
                    continue

                # 尝试匹配其他格式
                for pattern in self.ALTERNATIVE_PATTERNS:
                    match = pattern.search(line)
                    if match:
                        number = int(match.group(1))
                        self.result.add_figure(FigureInfo(number, file_path.name))
                        self.log(f"  ✓ 发现附图: 图{number} (兼容格式)")
                        break

        except Exception as e:
            print(f"⚠ 读取 {file_path.name} 失败: {e}")

    def _analyze_figures(self) -> None:
        """分析附图编号"""
        if not self.result.figures:
            return

        # 按编号排序
        self.result.figures.sort(key=lambda f: f.number)

        # 提取所有编号
        numbers = [f.number for f in self.result.figures]

        # 检查重复
        seen = set()
        for number in numbers:
            if number in seen:
                self.result.add_duplicate(number)
            seen.add(number)

        # 检查连续性
        if numbers:
            min_num = min(numbers)
            max_num = max(numbers)

            # 检查从1开始
            if min_num != 1:
                for missing in range(1, min_num):
                    self.result.add_gap(missing, 0)

            # 检查中间缺失
            for expected in range(min_num, max_num + 1):
                if expected not in seen:
                    # 找到应该插入的位置
                    position = next(
                        (i for i, f in enumerate(self.result.figures) if f.number > expected),
                        len(self.result.figures)
                    )
                    self.result.add_gap(expected, position)

    def _print_result(self) -> CheckResult:
        """打印检查结果"""
        print("-" * 50)
        print(f"发现附图: {self.result.total_figures} 幅")

        if self.result.figures:
            first = self.result.figures[0].number
            last = self.result.figures[-1].number
            print(f"编号范围: 图{first} - 图{last}")

        # 列出所有附图
        if self.verbose and self.result.figures:
            print("\n附图列表:")
            for figure in self.result.figures:
                print(f"  {figure}")

        # 报告问题
        has_issues = False

        if self.result.gaps:
            has_issues = True
            print(f"\n⚠ 发现跳号 ({len(self.result.gaps)} 个):")
            for missing, position in self.result.gaps:
                print(f"  缺少图{missing} (应插入位置: {position})")

        if self.result.duplicates:
            has_issues = True
            print(f"\n⚠ 发现重复编号 ({len(self.result.duplicates)} 个):")
            for number in self.result.duplicates:
                duplicates = [f for f in self.result.figures if f.number == number]
                print(f"  图{number} 出现 {len(duplicates)} 次:")
                for fig in duplicates:
                    print(f"    - {fig.file}")

        # 总结
        print("\n" + "-" * 50)
        if not has_issues:
            print("✅ 附图编号连续")
        else:
            print("❌ 附图编号存在问题")

        return self.result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="检查附图编号连续性",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python check_figures.py
    python check_figures.py --dir ./output
    python check_figures.py --verbose

Exit codes:
    0: 编号连续
    12: 发现跳号
        """
    )

    parser.add_argument(
        "--dir",
        type=str,
        default=".",
        help="章节文件所在目录 (默认: 当前目录)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="输出详细检查信息"
    )

    args = parser.parse_args()

    # 验证目录是否存在
    directory = Path(args.dir)
    if not directory.exists():
        print(f"错误: 目录不存在: {directory}", file=sys.stderr)
        sys.exit(1)

    if not directory.is_dir():
        print(f"错误: 不是目录: {directory}", file=sys.stderr)
        sys.exit(1)

    # 执行检查
    checker = FigureChecker(directory, verbose=args.verbose)
    result = checker.check()

    # 返回适当的退出码
    sys.exit(0 if result.success else 12)


if __name__ == "__main__":
    main()
