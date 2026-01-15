#!/usr/bin/env python3
"""
validate_disclosure.py - 验证专利交底书完整性

验证生成的交底书是否符合 IP-JL-027 模板标准。

使用方法:
    python validate_disclosure.py --dir <directory> --verbose

Exit codes:
    0: 验证成功
    10: 验证失败
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# 设置 UTF-8 编码输出（Windows 兼容）
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


@dataclass
class ValidationResult:
    """验证结果数据类"""
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checked_files: List[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        """添加错误"""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """添加警告"""
        self.warnings.append(warning)

    def has_issues(self) -> bool:
        """是否有任何问题"""
        return bool(self.errors or self.warnings)


class DisclosureValidator:
    """交底书验证器"""

    # 必需的章节文件（按顺序）
    REQUIRED_CHAPTERS = [
        "01_发明名称.md",
        "02_技术领域.md",
        "03_背景技术.md",
        "04_技术问题.md",
        "05_技术方案.md",
        "06_有益效果.md",
        "07_具体实施方式.md",
        "08_专利保护点.md",
        "09_参考资料.md",
    ]

    # 章节编号格式: ## **1. ** (阿拉伯数字 + 粗体)
    CHAPTER_NUMBER_PATTERN = re.compile(r'^##\s*\*\*([1-9])\s*\.\s*\*\*')

    # 子章节格式: ### **（1）** (中文括号 + 粗体)
    SUBCHAPTER_PATTERN = re.compile(r'^###\s*\*[（（]([1-9])[））]\s*\*')

    # 附图标记格式: #### 附图X：
    FIGURE_PATTERN = re.compile(r'^####\s*附图(\d+)：')

    def __init__(self, directory: Path, verbose: bool = False):
        self.directory = Path(directory)
        self.verbose = verbose
        self.result = ValidationResult(success=True)

    def log(self, message: str) -> None:
        """输出日志"""
        if self.verbose:
            print(f"  {message}")

    def validate(self) -> ValidationResult:
        """执行验证"""
        print(f"验证目录: {self.directory}")
        print("-" * 50)

        self._validate_chapters_exist()
        self._validate_chapter_format()
        self._validate_figure_format()

        print("-" * 50)
        return self._print_result()

    def _validate_chapters_exist(self) -> None:
        """验证必需章节是否存在"""
        print("检查必需章节...")

        missing = []
        for chapter in self.REQUIRED_CHAPTERS:
            file_path = self.directory / chapter
            if file_path.exists():
                self.result.checked_files.append(chapter)
                self.log(f"✓ {chapter}")
            else:
                missing.append(chapter)
                self.log(f"✗ {chapter} (缺失)")

        if missing:
            self.result.add_error(f"缺失 {len(missing)} 个必需章节: {', '.join(missing)}")

    def _validate_chapter_format(self) -> None:
        """验证章节格式"""
        print("检查章节格式...")

        for chapter_file in self.result.checked_files:
            file_path = self.directory / chapter_file
            try:
                content = file_path.read_text(encoding="utf-8")
                self._validate_file_format(chapter_file, content)
            except Exception as e:
                self.result.add_error(f"读取 {chapter_file} 失败: {e}")

    def _validate_file_format(self, filename: str, content: str) -> None:
        """验证单个文件格式"""
        lines = content.split('\n')

        # 检查是否包含章节编号
        has_chapter_number = any(self.CHAPTER_NUMBER_PATTERN.match(line) for line in lines)
        if has_chapter_number:
            self.log(f"✓ {filename}: 包含正确格式的章节编号")
        else:
            # 01 和 02 章节可能不需要章节编号（根据实际需求）
            if not filename.startswith(("01_", "02_")):
                self.result.add_warning(f"{filename}: 未检测到标准章节编号格式 (## **1. **)")

        # 检查是否包含子章节编号
        has_subchapter = any(self.SUBCHAPTER_PATTERN.match(line) for line in lines)
        if has_subchapter:
            self.log(f"✓ {filename}: 包含子章节编号")

        # 检查标题是否加粗
        has_bold_title = any('**' in line and '#' in line for line in lines[:20])
        if has_bold_title:
            self.log(f"✓ {filename}: 标题使用粗体格式")

    def _validate_figure_format(self) -> None:
        """验证附图格式"""
        print("检查附图格式...")

        figure_files = []
        for chapter_file in self.result.checked_files:
            file_path = self.directory / chapter_file
            try:
                content = file_path.read_text(encoding="utf-8")
                figures = self.FIGURE_PATTERN.findall(content)
                if figures:
                    figure_files.append((chapter_file, figures))
                    self.log(f"✓ {chapter_file}: 包含 {len(figures)} 幅附图")
            except Exception as e:
                self.result.add_warning(f"检查 {chapter_file} 附图失败: {e}")

        if not figure_files:
            self.result.add_warning("未检测到任何附图标记")

    def _print_result(self) -> ValidationResult:
        """打印验证结果"""
        if self.result.success:
            print("✅ 验证通过")
        else:
            print("❌ 验证失败")

        if self.result.errors:
            print(f"\n错误 ({len(self.result.errors)}):")
            for error in self.result.errors:
                print(f"  - {error}")

        if self.result.warnings:
            print(f"\n警告 ({len(self.result.warnings)}):")
            for warning in self.result.warnings:
                print(f"  - {warning}")

        return self.result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="验证专利交底书完整性",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python validate_disclosure.py
    python validate_disclosure.py --dir ./output
    python validate_disclosure.py --verbose

Exit codes:
    0: 验证成功
    10: 验证失败
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
        help="输出详细验证信息"
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

    # 执行验证
    validator = DisclosureValidator(directory, verbose=args.verbose)
    result = validator.validate()

    # 返回适当的退出码
    sys.exit(0 if result.success else 10)


if __name__ == "__main__":
    main()
