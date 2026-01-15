---
description: 智能扫描专利章节文档，分析并补充缺失的附图（仅处理章节03-07）
arguments:
  - name: directory
    description: 专利章节文件所在目录（默认当前目录）
    required: false
  - name: force_regenerate
    description: 是否强制重新生成所有附图（默认false，仅补充缺失）
    required: false
  - name: skip_confirmation
    description: 跳过用户确认，直接执行（默认false）
    required: false
---

# 专利附图智能更新

智能扫描专利章节文档（03-07），分析并补充缺失的附图。

## 快速开始

```bash
# 补充缺失的附图
/patent-update-diagrams

# 指定目录
/patent-update-diagrams directory="./patent_chapters"

# 强制重新生成所有附图
/patent-update-diagrams force_regenerate=true
```

## 功能说明

本命令专注于**附图补充**，不修改章节正文内容：

1. 扫描章节 03-07（背景技术、技术问题、技术方案、有益效果、具体实施方式）
2. 智能分析每个章节是否需要附图
3. 检测现有附图编号，确保连续性
4. 调用专门的附图生成器生成缺失的附图
5. 将附图嵌入到章节文件中

**不处理**：章节 01、02、08、09（这些章节不需要附图）

## 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| `directory` | 否 | 章节文件所在目录，默认当前目录 |
| `force_regenerate` | 否 | 是否强制重新生成所有附图，默认 false |
| `skip_confirmation` | 否 | 跳过用户确认直接执行，默认 false |

## 执行步骤

1. 扫描章节文件（03-07）
2. 分析章节内容，判断需要哪些附图
3. 统计现有附图编号
4. 用户确认（可跳过）
5. 调用附图生成器
6. 插入附图到章节文件
7. 生成报告

## 附图类型

| 附图类型 | 生成器 | 适用章节 |
|---------|--------|----------|
| 流程图 | flowchart-generator | 07 具体实施方式 |
| 时序图 | sequence-generator | 07 具体实施方式 |
| 协议格式图 | protocol-generator | 05 技术方案 |
| 架构图/结构图/原理图 | architecture-generator | 03、04、05 |

## 输出报告

```
附图更新完成

扫描章节: 5个
需要更新: 3个章节
生成附图: 6幅
```

## 注意事项

- **只处理章节 03-07**：其他章节不需要附图
- **不修改正文内容**：只插入附图
- **附图编号全局连续**：确保从 1 开始连续
- **Mermaid 格式**：生成的附图使用 Mermaid 语法

## 错误处理

| 错误 | 解决方法 |
|------|----------|
| 章节文件缺失 | 运行 `/patent` 命令先生成章节 |
| 生成器调用失败 | 检查 MCP 服务是否已配置 |
| 附图编号不连续 | 检查现有附图或使用 force_regenerate |

## 详细实现

实现细节（智能判断逻辑、编号管理算法）见: [SKILL.md - 附图生成](../.claude/skills/patent-disclosure-writer/SKILL.md#附图生成)
