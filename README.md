# Patent Disclosure Writer

> 自动化生成专利交底书的 Claude Code 技能

## 项目简介

本技能提供了一套完整的专利交底书自动化生成解决方案，包括专利检索、技术分析、文档生成和格式转换等功能。

## 功能特性

- **智能专利检索**：基于发明的技术领域和关键词进行精准检索
- **结构化内容生成**：自动生成符合规范的专利交底书各部分内容
- **图表自动生成**：使用 Mermaid 生成流程图、序列图等专利附图
- **多格式导出**：支持 Markdown 和 Word (.docx) 格式导出
- **文档验证**：自动检查生成内容的完整性和规范性

## 安装使用

### 方式一：作为项目级技能

1. 将本仓库复制到你的项目中
2. 确保 `.claude/skills/` 目录存在
3. 在 Claude Code 中使用时，技能会自动加载

### 方式二：作为个人技能

1. 复制 `patent-disclosure-writer` 目录到 `~/.claude/skills/`
2. 重启 Claude Code

## 使用方法

### 使用技能

在 Claude Code 中直接描述需求，技能会自动触发：

```
帮我生成一个关于智能排班系统的专利交底书
```

### 使用斜杠命令

本技能包含以下斜杠命令：

- `/patent` - 启动专利交底书生成流程
- `/patent-md-2-docx` - 将 Markdown 格式转换为 Word 文档
- `/patent-update-diagrams` - 更新专利文档中的图表

## 技能结构

```
patent-disclosure-writer-skill/
├── .claude/
│   ├── skills/
│   │   └── patent-disclosure-writer/
│   │       ├── SKILL.md           # 技能定义
│   │       ├── README.md          # 技能文档
│   │       ├── CONFIG.md          # 配置说明
│   │       ├── AGENTS.md          # 子代理说明
│   │       ├── TROUBLESHOOTING.md # 故障排除
│   │       ├── templates/         # 专利模板
│   │       └── example_things/    # 示例文件
│   └── agents/
│       └── patent/                # 专利相关子代理（21个）
├── commands/                      # 斜杠命令
│   ├── patent.md
│   ├── patent-md-2-docx.md
│   └── patent-update-diagrams.md
└── plans/                         # 架构优化文档
    └── patent-agent-architecture-optimization.md
```

## 子代理架构

本技能使用 21 个专业子代理，每个子代理负责专利交底书生成的特定环节：

1. **01-patent-title-generator** - 标题生成
2. **02-patent-field-analyzer** - 技术领域分析
3. **03-patent-background-researcher** - 背景技术研究
4. **04-patent-problem-analyzer** - 技术问题分析
5. **05-patent-solution-designer** - 技术方案设计
6. **06-patent-benefit-analyzer** - 有益效果分析
7. **07-patent-implementation-writer** - 具体实施方式编写
8. **08-patent-protection-extractor** - 保护点提取
9. **09-patent-reference-collector** - 相关文献收集
10. **10-patent-diagram-generator** - 专利附图生成
11. **11-patent-document-integrator** - 文档整合
12. **12-patent-flowchart-generator** - 流程图生成
13. **13-patent-sequence-generator** - 序列图生成
14. **14-patent-protocol-generator** - 协议图生成
15. **15-patent-architecture-generator** - 架构图生成
16. **16-patent-diagram-validator** - 图表验证
17. **17-patent-environment-checker** - 环境检查
18. **18-patent-markdown-parser** - Markdown 解析
19. **19-patent-docx-generator** - Word 文档生成
20. **20-patent-docx-validator** - Word 文档验证
21. **21-patent-diagram-inserter** - 图表插入

## MCP 工具依赖

本技能依赖以下 MCP 服务：

| MCP 服务 | 用途 | 安装命令 |
|---------|------|----------|
| google-patents-mcp | 专利检索 | `npm install -g @modelcontextprotocol/server-google-patents` |
| exa | 技术文档搜索 | `npm install -g @modelcontextprotocol/server-exa` |
| web-reader | 网页内容提取 | `npm install -g @modelcontextprotocol/server-web-reader` |

## 配置要求

在 `~/.claude/settings.json` 中配置 MCP 服务：

```json
{
  "mcpServers": {
    "google-patents": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google-patents"]
    },
    "exa": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-exa"]
    }
  }
}
```

## 许可证

MIT License

## 作者

allanpk716 <allanpk716@gmail.com>

## 相关链接

- [EasyJob Skills Marketplace](https://github.com/allanpk716/EasyJobSkills)
- [Claude Code 官方文档](https://code.claude.com/docs/en/skills)
