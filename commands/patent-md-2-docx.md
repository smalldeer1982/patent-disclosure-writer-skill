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

你正在调用专利交底书 Markdown 转 DOCX 转换命令。本命令将已有的 Markdown 格式交底书转换为正式的 DOCX 格式。

## 执行步骤

### 1. 参数验证和路径确定

**步骤 1.1：验证 Markdown 文件**

确认 `markdown_file` 参数指向的文件存在：
- 使用 Glob 或 Read 工具验证文件存在
- 如果文件不存在，提示用户检查路径

**步骤 1.2：确定输出目录**

- 如果指定了 `output_dir`，使用该目录
- 如果未指定，使用 Markdown 文件所在目录

**步骤 1.3：提取发明名称**

从 Markdown 文件路径或内容中提取发明名称，用于命名输出文件：
- 文件名格式：`专利申请技术交底书_[发明名称].md`
- 输出 DOCX：`专利申请技术交底书_[发明名称].docx`

### 2. 环境检查

**步骤 2.1：检查 pandoc 是否安装**

```bash
pandoc --version
```

如果未安装，提供安装指导：
```bash
# macOS
brew install pandoc

# Linux
sudo apt-get install pandoc

# Windows
# 从 https://pandoc.org/installing.html 下载安装程序
```

**步骤 2.2：检查 DOCX 模板**

确认模板文件是否存在：
- 模板路径：`skills/patent-disclosure-writer/templates/发明、实用新型专利申请交底书 模板.docx`

如果模板存在，使用自定义参考文档：
```bash
pandoc "{markdown_file}" -o "{output_docx}" --reference-doc="{template_path}"
```

如果模板不存在，使用默认格式：
```bash
pandoc "{markdown_file}" -o "{output_docx}"
```

### 3. 执行转换

使用 pandoc 进行转换：

**基础转换**：
```bash
pandoc "{markdown_file_path}" \
  -o "{output_dir}/专利申请技术交底书_{发明名称}.docx" \
  --from=markdown+raw_html \
  --toc \
  --toc-depth=3
```

**使用模板的转换**（如果模板存在）：
```bash
pandoc "{markdown_file_path}" \
  -o "{output_dir}/专利申请技术交底书_{发明名称}.docx" \
  --from=markdown+raw_html \
  --reference-doc="skills/patent-disclosure-writer/templates/发明、实用新型专利申请交底书 模板.docx" \
  --toc \
  --toc-depth=3
```

### 4. 附图处理（可选）

如果 Markdown 文件中包含 Mermaid 代码块：

**选项 A：提示用户使用预渲染图片**
```
检测到 Markdown 文件中包含 Mermaid 图表。

建议：
1. 使用 Mermaid Live Editor (https://mermaid.live) 渲染图表为 PNG
2. 在 Markdown 中替换 Mermaid 代码块为图片引用
3. 重新运行转换命令

或者使用高级转换功能（需要 Python 环境，见下方说明）。
```

**选项 B：提供 Python 脚本说明**

如果用户需要自动处理 Mermaid 图表，说明高级功能需要 Python 环境：
```
高级功能说明：
- 完整的 Mermaid 图表渲染需要 Python 脚本支持
- 需要安装：python-docx, mermaid-cli
- 脚本位置：.claude/scripts/docx_conversion/
- 当前状态：开发中

如需此功能，请参考项目文档或联系开发者。
```

### 5. 验证输出

检查生成的 DOCX 文件：
```bash
# 检查文件是否存在
ls -lh "{output_dir}/专利申请技术交底书_{发明名称}.docx"
```

### 6. 展示结果

```markdown
## DOCX 转换完成

**输入文件**: {markdown_file_path}
**输出文件**: {output_dir}/专利申请技术交底书_{发明名称}.docx

---

### 转换详情

- 转换工具: pandoc
- 输出格式: DOCX
- 模板: {模板名称或"默认格式"}

---

### 后续操作

1. 检查生成的 DOCX 文件格式
2. 如需调整格式，可以在 DOCX 中手动修改
3. 如包含 Mermaid 图表，需要手动渲染并插入图片

💡 如需自动处理 Mermaid 图表和高级格式，可以使用完整版转换脚本（需要 Python 环境）。
```

## 错误处理

### pandoc 未安装

```
错误: 未检测到 pandoc

解决方法：
1. 安装 pandoc:
   - macOS: brew install pandoc
   - Linux: sudo apt-get install pandoc
   - Windows: https://pandoc.org/installing.html

2. 验证安装:
   pandoc --version
```

### Markdown 文件不存在

```
错误: 找不到指定的 Markdown 文件: {markdown_file}

请检查：
1. 文件路径是否正确
2. 文件扩展名是否为 .md
3. 是否在正确的目录中
```

### 转换失败

```
错误: DOCX 转换失败

可能原因：
1. Markdown 文件格式不正确
2. 包含不兼容的语法
3. 输出目录不可写

解决方法：
1. 检查 Markdown 文件语法
2. 尝试简化 Markdown 内容
3. 检查输出目录权限
```

## 注意事项

1. **Mermaid 图表**：pandoc 不支持直接渲染 Mermaid，需要手动处理
2. **格式限制**：基础转换使用默认样式，高级格式需要使用模板
3. **字体**：pandoc 使用系统默认字体，如需特定字体请使用模板或手动调整
4. **文件编码**：确保 Markdown 文件使用 UTF-8 编码

## 高级功能说明

完整的高级转换功能（包含 Mermaid 渲染、字体设置、格式验证）需要 Python 环境和自定义脚本。这些脚本位于：

```
.claude/scripts/docx_conversion/
├── markdown_parser.py    # Markdown 解析
├── docx_generator.py     # DOCX 生成
├── diagram_inserter.py   # 附图渲染和插入
├── docx_validator.py     # 格式验证
└── font_utils.py         # 字体工具
```

**当前状态**：开发中

**如需使用高级功能**：
1. 确保安装 Python 3.7+
2. 安装依赖：`pip install python-docx`
3. 安装 mermaid-cli：`npm install -g @mermaid-js/mermaid-cli`
4. 安装思源黑体 CN 字体
5. 等待脚本发布或参考项目文档自行实现

## 输出文件

执行完成后，输出目录将包含以下文件：

| 文件 | 说明 |
|------|------|
| `专利申请技术交底书_{发明名称}.docx` | 生成的 DOCX 格式交底书 |
