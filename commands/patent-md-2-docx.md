---
description: 将 Markdown 格式的专利交底书转换为 DOCX 格式
arguments:
  - name: markdown_file
    description: Markdown 交底书文件路径（必需）
    required: true
  - name: output_dir
    description: 输出目录（可选，默认与 Markdown 文件同目录）
    required: false
---

# 专利交底书 Markdown 转 DOCX

将 Markdown 格式的专利交底书转换为正式的 DOCX 格式文档。

## 快速开始

```bash
/patent-md-2-docx markdown_file="专利申请技术交底书_[发明名称].md"
```

## 前置要求

- **pandoc**: 文档转换工具
  - 安装方法见 [README.md - 环境配置](../README.md#环境配置)
  - 验证安装: `pandoc --version`

## 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| `markdown_file` | 是 | Markdown 交底书文件路径 |
| `output_dir` | 否 | 输出目录，默认与输入文件同目录 |

## 执行步骤

1. 验证 Markdown 文件存在
2. 检查 pandoc 是否已安装
3. 执行转换（使用自定义模板或默认格式）
4. 验证输出文件

## 输出文件

| 文件 | 说明 |
|------|------|
| `专利申请技术交底书_[发明名称].docx` | 生成的 DOCX 格式交底书 |

## 注意事项

- **Mermaid 图表**: pandoc 不支持直接渲染 Mermaid 图表，需要手动处理
- **格式**: 基础转换使用默认样式，高级格式需要自定义模板
- **编码**: 确保 Markdown 文件使用 UTF-8 编码

## 错误处理

| 错误 | 解决方法 |
|------|----------|
| pandoc 未安装 | 安装 pandoc，见 [README.md - 环境配置](../README.md#环境配置) |
| Markdown 文件不存在 | 检查文件路径是否正确 |
| 转换失败 | 检查 Markdown 文件格式和输出目录权限 |

## 高级功能

完整的高级转换功能（Mermaid 渲染、字体设置、格式验证）需要 Python 环境。

详细信息见: [SKILL.md - DOCX 转换](../.claude/skills/patent-disclosure-writer/SKILL.md#docx-转换)
