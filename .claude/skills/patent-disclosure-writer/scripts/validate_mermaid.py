#!/usr/bin/env python3
"""
validate_mermaid.py - 验证 Mermaid 图表语法

验证章节文件中的 Mermaid 代码块语法正确性。

使用方法:
    python validate_mermaid.py --dir <directory> --strict --verbose

Exit codes:
    0: 验证成功
    11: 验证失败
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class ValidationResult:
    """验证结果数据类"""
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checked_files: int = 0
    total_diagrams: int = 0
    valid_diagrams: int = 0

    def add_error(self, error: str) -> None:
        """添加错误"""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """添加警告"""
        self.warnings.append(warning)


class MermaidValidator:
    """Mermaid 语法验证器"""

    # Mermaid 代码块模式
    MERMAID_BLOCK_PATTERN = re.compile(r'```mermaid\n(.*?)\n```', re.DOTALL)

    # 附图标记模式: #### 附图X：
    FIGURE_PATTERN = re.compile(r'^####\s*附图(\d+)：')

    # 基本的 Mermaid 语法检查
    BASIC_PATTERNS = {
        'graph': re.compile(r'graph\s+(TD|TB|BT|RL|LR)'),
        'sequenceDiagram': re.compile(r'sequenceDiagram'),
        'classDiagram': re.compile(r'classDiagram'),
        'stateDiagram': re.compile(r'stateDiagram'),
        'erDiagram': re.compile(r'erDiagram'),
        'pie': re.compile(r'pie\s+showData'),
    }

    def __init__(self, directory: Path, strict: bool = False, verbose: bool = False):
        self.directory = Path(directory)
        self.strict = strict
        self.verbose = verbose
        self.result = ValidationResult(success=True)
        self.mermaid_cli_available = self._check_mermaid_cli()

    def log(self, message: str) -> None:
        """输出日志"""
        if self.verbose:
            print(f"  {message}")

    def validate(self) -> ValidationResult:
        """执行验证"""
        print(f"验证目录: {self.directory}")
        print("-" * 50)

        # 检查 mermaid-cli 可用性
        if self.mermaid_cli_available:
            print("✓ mermaid-cli 可用，将进行完整语法验证")
        else:
            if self.strict:
                print("✗ 严格模式下要求 mermaid-cli，但未检测到")
                self.result.add_error("严格模式要求 mermaid-cli (mmdc)")
                return self._print_result()
            else:
                print("⚠ mermaid-cli 不可用，将进行基础语法检查")

        # 查找所有章节文件
        chapter_files = self._find_chapter_files()
        if not chapter_files:
            self.result.add_warning("未找到任何章节文件")
            return self._print_result()

        # 验证每个文件
        for file_path in chapter_files:
            self._validate_file(file_path)

        return self._print_result()

    def _check_mermaid_cli(self) -> bool:
        """检查 mermaid-cli 是否可用"""
        try:
            result = subprocess.run(
                ["mmdc", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _find_chapter_files(self) -> List[Path]:
        """查找所有章节文件"""
        files = []
        for pattern in ["[0-9][0-9]_*.md", "专利申请技术交底书_*.md"]:
            files.extend(self.directory.glob(pattern))
        return sorted(files)

    def _validate_file(self, file_path: Path) -> None:
        """验证单个文件"""
        self.result.checked_files += 1
        self.log(f"检查: {file_path.name}")

        try:
            content = file_path.read_text(encoding="utf-8")

            # 提取 Mermaid 代码块
            diagrams = self.MERMAID_BLOCK_PATTERN.findall(content)
            if not diagrams:
                self.log(f"  无 Mermaid 图表")
                return

            self.log(f"  发现 {len(diagrams)} 个 Mermaid 图表")

            # 提取附图编号
            figure_numbers = self.FIGURE_PATTERN.findall(content)

            # 验证每个图表
            for i, diagram in enumerate(diagrams, 1):
                self._validate_diagram(file_path.name, i, diagram, figure_numbers)

        except Exception as e:
            self.result.add_error(f"读取 {file_path.name} 失败: {e}")

    def _validate_diagram(
        self,
        filename: str,
        index: int,
        diagram: str,
        figure_numbers: List[str]
    ) -> None:
        """验证单个图表"""
        self.result.total_diagrams += 1
        self.log(f"    图表 {index}:")

        # 基础语法检查
        is_valid_basic = self._validate_basic_syntax(diagram)

        # 如果 mermaid-cli 可用，进行完整验证
        if self.mermaid_cli_available and is_valid_basic:
            is_valid_full = self._validate_with_cli(diagram)
            if is_valid_full:
                self.result.valid_diagrams += 1
                self.log(f"      ✓ 语法正确")
        elif is_valid_basic:
            # 只有基础检查通过
            self.result.valid_diagrams += 1
            self.log(f"      ✓ 基础语法通过")
        else:
            self.log(f"      ✗ 语法错误")

    def _validate_basic_syntax(self, diagram: str) -> bool:
        """基础语法检查"""
        diagram = diagram.strip()

        # 检查是否为空
        if not diagram:
            self.result.add_warning("发现空的 Mermaid 代码块")
            return False

        # 检查是否包含已知的图表类型
        has_valid_type = any(
            pattern.search(diagram)
            for pattern in self.BASIC_PATTERNS.values()
        )

        if not has_valid_type:
            self.result.add_warning(f"未识别的图表类型: {diagram[:50]}...")
            return False

        # 检查基本结构
        lines = diagram.split('\n')
        if len(lines) < 2:
            self.result.add_warning("图表结构过于简单")
            return False

        return True

    def _validate_with_cli(self, diagram: str) -> bool:
        """使用 mermaid-cli 进行验证"""
        try:
            # 创建临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.mmd',
                delete=False
            ) as f:
                f.write(diagram)
                temp_file = f.name

            # 尝试渲染（验证语法）
            result = subprocess.run(
                ["mmdc", "-i", temp_file, "-o", "NUL" if sys.platform == "win32" else "/dev/null"],
                capture_output=True,
                timeout=10
            )

            # 清理临时文件
            try:
                Path(temp_file).unlink()
            except:
                pass

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            self.result.add_warning("Mermaid CLI 验证超时")
            return False
        except Exception as e:
            self.result.add_warning(f"Mermaid CLI 验证失败: {e}")
            return False

    def _print_result(self) -> ValidationResult:
        """打印验证结果"""
        print("-" * 50)

        print(f"检查文件: {self.result.checked_files}")
        print(f"发现图表: {self.result.total_diagrams}")
        print(f"有效图表: {self.result.valid_diagrams}")

        if self.result.total_diagrams > 0:
            success_rate = (self.result.valid_diagrams / self.result.total_diagrams) * 100
            print(f"成功率: {success_rate:.1f}%")

        if self.result.success and self.result.errors:
            print("✅ 验证完成（有警告）")
        elif self.result.success:
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
        description="验证 Mermaid 图表语法",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python validate_mermaid.py
    python validate_mermaid.py --dir ./output
    python validate_mermaid.py --verbose
    python validate_mermaid.py --strict

Exit codes:
    0: 验证成功
    11: 验证失败
        """
    )

    parser.add_argument(
        "--dir",
        type=str,
        default=".",
        help="章节文件所在目录 (默认: 当前目录)"
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="严格模式，必须有 mermaid-cli"
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
    validator = MermaidValidator(
        directory,
        strict=args.strict,
        verbose=args.verbose
    )
    result = validator.validate()

    # 返回适当的退出码
    sys.exit(0 if result.success else 11)


if __name__ == "__main__":
    main()
