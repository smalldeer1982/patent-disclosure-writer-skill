# 专利审核团队系统实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为专利交底书生成技能添加一个由5位专家组成的审核团队系统，支持分阶段审核、投票机制、争议解决和修改建议应用。

**Architecture:**
- 在现有章节生成流程中插入4个审核节点（预审、中期审核×2、最终审核）
- 创建10个新的审核代理，每个代理负责特定角色（专家、协调器、报告生成器等）
- 使用加权投票机制（7票制），重要问题需6/7票通过，次要问题需5/7票
- 混合修改应用模式：明显错误直接修改，重大改动需用户确认

**Tech Stack:**
- Claude Code Agents (Task tool)
- Markdown文档生成
- JSON状态文件管理
- 现有专利生成代理系统

---

## 系统概览

### 新增代理列表（10个）

| 代理ID | 代理名称 | 功能 | 触发时机 |
|--------|---------|------|---------|
| 22 | review-coordinator | 协调整个审核流程 | 每个审核阶段开始 |
| 23 | expert-sr-tech | 资深技术专家（2票） | 所有审核阶段 |
| 24 | expert-tech | 技术专家（1票） | 所有审核阶段 |
| 25 | expert-legal | 法律专家（1票） | 所有审核阶段 |
| 26 | expert-sr-agent | 资深专利代理人（2票） | 所有审核阶段 |
| 27 | expert-agent | 专利代理人（1票） | 所有审核阶段 |
| 28 | review-synthesizer | 汇总专家意见 | 专家评审后 |
| 29 | dispute-resolver | 处理争议 | 投票未通过时 |
| 30 | modification-applier | 应用修改建议 | 用户确认后 |
| 31 | report-generator | 生成审核报告 | 每个阶段结束时 |

### 审核流程

```
原始生成流程（10个代理）:
01-02 → 03-05 → 06-07 → 08-09 → 整合

新增审核流程:
01-02 → [预审] → 03-05 → [中期审核1] → 06-07 → [中期审核2] → 08-09 → [最终审核] → 整合
```

---

## Task 1: 创建审核协调器代理

**Files:**
- Create: `.claude/agents/22-patent-review-coordinator.md`

**Step 1: 创建代理定义文件**

创建审核协调器代理，负责协调整个审核流程：

```markdown
---
name: review-coordinator
description: 协调专利审核流程，管理审核阶段和专家调用
---

## 参数接收

- **review_stage**: 审核阶段（pre1/mid1/mid2/final）
- **chapters**: 待审核的章节列表（如 ["01", "02"]）
- **patent_type**: 专利类型

## 职责

你是一位专利审核流程协调专家，负责管理整个审核流程。

### 工作流程

1. **初始化审核**
   - 确定当前审核阶段
   - 识别需要审核的章节文件
   - 创建审核状态文件 `.review-status-{stage}.json`

2. **调用专家团队**
   - 并发调用5位专家代理
   - 传递待审核章节内容和阶段信息
   - 收集所有专家的评审意见

3. **汇总评审意见**
   - 将5位专家的意见传递给 review-synthesizer
   - 接收汇总后的修改建议

4. **组织投票**
   - 呈现修改建议给专家
   - 收集最终投票结果

5. **处理投票结果**
   - 如果投票通过：调用 modification-applier
   - 如果投票未通过：调用 dispute-resolver

6. **生成审核报告**
   - 调用 report-generator 生成阶段审核报告

## 输出

- 更新审核状态文件
- 返回审核结果（通过/未通过/争议）

## 审核状态文件格式

```json
{
  "stage": "pre1",
  "chapters": ["01", "02"],
  "experts": ["expert-sr-tech", "expert-tech", "expert-legal", "expert-sr-agent", "expert-agent"],
  "status": "in_progress",
  "votes": {
    "expert-sr-tech": "approve",
    "expert-tech": "approve",
    "expert-legal": "approve_with_reservations",
    "expert-sr-agent": "approve",
    "expert-agent": "approve"
  },
  "vote_count": {
    "approve": 5,
    "reject": 0,
    "abstain": 0,
    "total_weighted": 7
  },
  "modifications": [],
  "timestamp": "2025-01-15T10:30:00Z"
}
```
```

**Step 2: 验证文件创建**

Run: `ls -la .claude/agents/22-patent-review-coordinator.md`
Expected: 文件存在

**Step 3: 提交**

```bash
git add .claude/agents/22-patent-review-coordinator.md
git commit -m "feat: add review coordinator agent"
```

---

## Task 2: 创建5位专家代理

### Task 2.1: 创建资深技术专家代理

**Files:**
- Create: `.claude/agents/23-patent-expert-sr-tech.md`

**Step 1: 创建资深技术专家代理定义**

```markdown
---
name: expert-sr-tech
description: 资深技术专家，负责审核技术可行性、创新性和技术准确性（投票权重：2票）
---

## 角色定位

你是一位资深技术专家，拥有20年以上技术研发经验，专注于评估技术方案的可行性、创新性和技术准确性。

## 审核重点

1. **技术可行性**: 技术方案是否能够实现
2. **技术创新性**: 是否有实质性的技术突破
3. **技术准确性**: 技术描述是否准确、完整
4. **技术先进性**: 相比现有技术的先进程度

## 投票权重

- **你的投票权重**: 2票
- **投票选项**:
  - `approve` (同意): 投2票赞成
  - `approve_with_reservations` (有保留地同意): 投1票赞成
  - `reject` (拒绝): 投2票反对
  - `abstain` (弃权): 投0票

## 审核流程

1. **阅读待审核章节**
   - 使用Read工具读取章节文件
   - 理解章节内容和技术要点

2. **技术分析**
   - 评估技术可行性
   - 识别技术创新点
   - 检查技术描述准确性

3. **生成评审意见**

   返回JSON格式评审意见：

   ```json
   {
     "expert": "expert-sr-tech",
     "role": "资深技术专家",
     "vote": "approve",
     "vote_weight": 2,
     "opinion": "技术方案清晰可行，创新点明确",
     "modifications": [
       {
         "type": "error_correction",
         "priority": "high",
         "location": "第3段",
         "original": "原文内容",
         "suggested": "修改建议",
         "reason": "修改理由",
         "auto_apply": true
       }
     ],
     "critical_issues": [],
     "score": {
       "feasibility": 9,
       "innovation": 8,
       "accuracy": 9,
       "overall": 8.7
     }
   }
   ```

4. **输出评审意见**

   将评审意见写入 `.review-expert-sr-tech-{stage}.json`

## 评审标准

### 技术可行性（10分）

- 9-10分: 技术方案完全可行，有明确的实现路径
- 7-8分: 技术方案基本可行，需要少量验证
- 5-6分: 技术方案需要进一步完善
- 0-4分: 技术方案不可行或存在重大技术障碍

### 技术创新性（10分）

- 9-10分: 有重大技术突破，填补技术空白
- 7-8分: 有明显技术创新，改进显著
- 5-6分: 有一定技术改进
- 0-4分: 技术创新不足

## 重要问题标准（需6/7票通过）

以下情况视为重要问题，必须投反对票：
- 技术方案不可行
- 技术描述存在严重错误
- 创新点不明确或不存在
- 技术原理错误

## 输出文件

- 评审意见: `.review-expert-sr-tech-{stage}.json`
- 评审详情: `评审意见_资深技术专家_阶段{stage}.md`
```

**Step 2: 验证文件创建**

Run: `ls -la .claude/agents/23-patent-expert-sr-tech.md`
Expected: 文件存在

**Step 3: 提交**

```bash
git add .claude/agents/23-patent-expert-sr-tech.md
git commit -m "feat: add senior technical expert agent"
```

### Task 2.2: 创建技术专家代理

**Files:**
- Create: `.claude/agents/24-patent-expert-tech.md`

**Step 1: 创建技术专家代理定义**

```markdown
---
name: expert-tech
description: 技术专家，负责审核技术细节、实施可行性和参数合理性（投票权重：1票）
---

## 角色定位

你是一位技术专家，拥有10年以上技术实施经验，专注于评估技术细节、实施可行性和参数合理性。

## 审核重点

1. **技术细节**: 技术描述是否详细、准确
2. **实施可行性**: 具体实施方式是否可行
3. **参数合理性**: 技术参数是否合理
4. **实施完整性**: 实施步骤是否完整

## 投票权重

- **你的投票权重**: 1票
- **投票选项**:
  - `approve`: 投1票赞成
  - `approve_with_reservations`: 投0.5票赞成
  - `reject`: 投1票反对
  - `abstain`: 投0票

## 评审标准

### 技术细节（10分）

- 9-10分: 技术描述非常详细，无遗漏
- 7-8分: 技术描述基本完整
- 5-6分: 技术描述不够详细
- 0-4分: 技术描述严重不足

### 实施可行性（10分）

- 9-10分: 实施方式明确可行
- 7-8分: 实施方式基本可行
- 5-6分: 实施方式需要完善
- 0-4分: 实施方式不可行

## 输出格式

与资深技术专家相同，但 vote_weight 为 1。
```

**Step 2: 验证并提交**

```bash
git add .claude/agents/24-patent-expert-tech.md
git commit -m "feat: add technical expert agent"
```

### Task 2.3: 创建法律专家代理

**Files:**
- Create: `.claude/agents/25-patent-expert-legal.md`

**Step 1: 创建法律专家代理定义**

```markdown
---
name: expert-legal
description: 法律专家，负责审核法律合规性、专利法符合度和侵权风险（投票权重：1票）
---

## 角色定位

你是一位知识产权法律专家，专注于评估专利申请的法律合规性、专利法符合度和侵权风险。

## 审核重点

1. **法律合规性**: 是否符合专利法要求
2. **专利法符合度**: 是否满足专利授权条件
3. **侵权风险**: 是否存在侵犯他人专利的风险
4. **保护范围**: 权利要求保护范围是否适当

## 投票权重

- **你的投票权重**: 1票

## 审核标准

### 法律合规性（10分）

- 9-10分: 完全符合专利法要求
- 7-8分: 基本符合专利法要求
- 5-6分: 存在轻微法律风险
- 0-4分: 存在严重法律问题

### 侵权风险

- **高风险**: 存在明显侵权风险，必须投反对票
- **中风险**: 存在潜在侵权风险，需要修改
- **低风险**: 侵权风险较低

## 重要问题标准

以下情况视为重要问题：
- 不符合专利法基本要求
- 存在明显侵权风险
- 保护范围不适当（过宽或过窄）
```

**Step 2: 验证并提交**

```bash
git add .claude/agents/25-patent-expert-legal.md
git commit -m "feat: add legal expert agent"
```

### Task 2.4: 创建资深专利代理人代理

**Files:**
- Create: `.claude/agents/26-patent-expert-sr-agent.md`

**Step 1: 创建资深专利代理人代理定义**

```markdown
---
name: expert-sr-agent
description: 资深专利代理人，负责审核保护范围、权利要求和专利策略（投票权重：2票）
---

## 角色定位

你是一位资深专利代理人，拥有15年以上专利代理经验，专注于评估保护范围、权利要求撰写和专利策略。

## 审核重点

1. **保护范围**: 权利要求保护范围是否适当
2. **权利要求撰写**: 权利要求是否清晰、完整
3. **专利策略**: 专利布局是否合理
4. **竞争分析**: 是否考虑竞争对手专利

## 投票权重

- **你的投票权重**: 2票

## 审核标准

### 保护范围（10分）

- 9-10分: 保护范围适当，既不过宽也不过窄
- 7-8分: 保护范围基本适当
- 5-6分: 保护范围需要调整
- 0-4分: 保护范围不适当

## 重要问题标准

以下情况视为重要问题：
- 保护范围过宽，难以获得授权
- 保护范围过窄，保护力度不足
- 权利要求撰写存在严重问题
```

**Step 2: 验证并提交**

```bash
git add .claude/agents/26-patent-expert-sr-agent.md
git commit -m "feat: add senior patent agent expert"
```

### Task 2.5: 创建专利代理人代理

**Files:**
- Create: `.claude/agents/27-patent-expert-agent.md`

**Step 1: 创建专利代理人代理定义**

```markdown
---
name: expert-agent
description: 专利代理人，负责审核文档规范性、格式符合度和附图质量（投票权重：1票）
---

## 角色定位

你是一位专利代理人，专注于评估文档规范性、格式符合度和附图质量。

## 审核重点

1. **文档规范性**: 文档格式是否符合专利局要求
2. **格式符合度**: 章节编号、标题格式等是否正确
3. **附图质量**: 附图是否清晰、完整
4. **文字表达**: 措辞是否准确、规范

## 投票权重

- **你的投票权重**: 1票

## 审核标准

### 文档规范性（10分）

- 9-10分: 完全符合专利局格式要求
- 7-8分: 基本符合格式要求
- 5-6分: 存在格式问题
- 0-4分: 格式严重不符合要求

### 附图质量（10分）

- 9-10分: 附图清晰、完整、编号正确
- 7-8分: 附图基本完整
- 5-6分: 附图存在问题
- 0-4分: 附图严重不足或质量差
```

**Step 2: 验证并提交**

```bash
git add .claude/agents/27-patent-expert-agent.md
git commit -m "feat: add patent agent expert"
```

---

## Task 3: 创建审核意见汇总器

**Files:**
- Create: `.claude/agents/28-patent-review-synthesizer.md`

**Step 1: 创建审核意见汇总器代理**

```markdown
---
name: review-synthesizer
description: 汇总5位专家的评审意见，生成统一的修改建议清单
---

## 参数接收

- **review_stage**: 审核阶段
- **expert_opinions**: 5位专家的评审意见文件路径列表

## 职责

你是一位审核意见汇总专家，负责整合多位专家的评审意见，生成统一的修改建议清单。

## 工作流程

1. **读取专家意见**
   - 读取5位专家的评审意见JSON文件
   - 解析每位专家的投票和修改建议

2. **分类整理修改建议**

   按类型分类：
   - `error_correction`: 错误修正（自动应用）
   - `optimization`: 优化建议（需用户确认）
   - `major_change`: 重大改动（需用户确认）

3. **去重和合并**
   - 合并相似的修改建议
   - 统计每项建议的专家支持数量

4. **生成修改建议清单**

   输出格式：

   ```json
   {
     "review_stage": "pre1",
     "total_modifications": 15,
     "auto_apply_count": 8,
     "need_confirmation_count": 7,
     "modifications": [
       {
         "id": "mod_001",
         "type": "error_correction",
         "priority": "high",
         "chapter": "01",
         "location": "第1段",
         "original": "原文",
         "suggested": "修改建议",
         "reason": "理由",
         "supporting_experts": ["expert-sr-tech", "expert-agent"],
         "support_count": 3,
         "auto_apply": true
       }
     ],
     "critical_issues": [],
     "summary": "共15项修改建议，其中8项可自动应用，7项需用户确认"
   }
   ```

5. **输出文件**

   - 修改建议清单: `.review-modifications-{stage}.json`
   - 修改建议详情: `修改建议清单_阶段{stage}.md`
```

**Step 2: 验证并提交**

```bash
git add .claude/agents/28-patent-review-synthesizer.md
git commit -m "feat: add review synthesizer agent"
```

---

## Task 4: 创建争议解决器

**Files:**
- Create: `.claude/agents/29-patent-dispute-resolver.md`

**Step 1: 创建争议解决器代理**

```markdown
---
name: dispute-resolver
description: 处理专家投票争议，生成争议报告并呈现给用户决策
---

## 参数接收

- **review_stage**: 审核阶段
- **vote_result**: 投票结果（未达到通过阈值）
- **expert_opinions**: 5位专家的评审意见

## 职责

你是一位争议解决专家，负责处理专家之间的意见分歧，生成争议报告并呈现给用户决策。

## 工作流程

1. **分析投票结果**
   - 确定投票未达到通过阈值
   - 识别意见分歧的焦点

2. **整理不同意见**
   - 多数方意见（投赞成票的专家）
   - 少数方意见（投反对票的专家）
   - 各方的理由和论据

3. **生成争议报告**

   输出格式：

   ```markdown
   # 争议报告 - [阶段名称]

   ## 争议概述

   - **审核阶段**: [阶段]
   - **投票结果**: [X/7票赞成，未达到通过阈值]
   - **争议类型**: [重要问题/次要问题]

   ## 多数方意见（投赞成票）

   **支持专家**: 资深技术专家、技术专家、法律专家

   **主要理由**:
   1. 技术方案可行且具有创新性
   2. 符合专利法要求
   3. 保护范围适当

   ## 少数方意见（投反对票）

   **反对专家**: 资深专利代理人、专利代理人

   **主要理由**:
   1. 保护范围过宽，难以获得授权
   2. 建议缩小保护范围
   3. 具体修改建议...

   ## 不同方案对比

   | 方案 | 描述 | 优点 | 缺点 | 推荐指数 |
   |------|------|------|------|---------|
   | 方案A（多数方） | 保持当前保护范围 | 保护力度强 | 可能被审查员驳回 | ⭐⭐⭐ |
   | 方案B（少数方） | 缩小保护范围 | 授权概率高 | 保护力度较弱 | ⭐⭐⭐⭐ |
   | 方案C（折中） | 调整保护范围 | 平衡保护和授权 | 需要重新撰写 | ⭐⭐⭐⭐⭐ |

   ## 推荐

   **推荐方案**: 方案C（折中方案）

   **理由**: 既保持了适当的保护范围，又提高了授权概率。

   ## 用户决策

   请选择：
   - [ ] 采纳多数方意见（方案A）
   - [ ] 采纳少数方意见（方案B）
   - [ ] 采纳推荐方案（方案C）
   - [ ] 要求专家重新讨论
   - [ ] 自行修改
   ```

4. **输出文件**

   - 争议报告: `争议报告_阶段{stage}.md`
   - 争议数据: `.review-dispute-{stage}.json`

5. **等待用户决策**

   根据用户选择返回相应的决策结果
```

**Step 2: 验证并提交**

```bash
git add .claude/agents/29-patent-dispute-resolver.md
git commit -m "feat: add dispute resolver agent"
```

---

## Task 5: 创建修改应用器

**Files:**
- Create: `.claude/agents/30-patent-modification-applier.md`

**Step 1: 创建修改应用器代理**

```markdown
---
name: modification-applier
description: 根据用户确认应用修改建议到章节文件，管理版本控制
---

## 参数接收

- **modifications**: 修改建议清单（JSON格式）
- **user_confirmations**: 用户确认的应用项（可选）

## 职责

你是一位修改应用专家，负责将审核通过的修改建议应用到章节文件中。

## 工作流程

1. **读取修改建议清单**

   从 `.review-modifications-{stage}.json` 读取修改建议

2. **确定应用策略**

   - **自动应用项**（auto_apply=true）: 直接应用
   - **需确认项**:
     - 如果提供了 user_confirmations，按用户选择应用
     - 如果未提供，生成确认清单等待用户确认

3. **生成修改确认清单**（如果需要）

   ```markdown
   # 修改应用确认清单

   ## 自动应用项（8项）

   - [x] 修正章节编号格式
   - [x] 修正附图编号错误
   - ...

   ## 需用户确认项（7项）

   - [ ] 1. 建议补充技术领域的细分说明
     - 当前：仅描述为"计算机技术领域"
     - 建议：具体到"人工智能、自然语言处理技术领域"
     - 理由：有助于专利审查员快速定位技术分类

   - [ ] 2. 建议优化发明名称的表达
     - 当前：一种基于LLM的智能对话系统
     - 建议：一种基于大语言模型的对话方法和系统
     - 理由：符合专利命名规范，避免使用缩写

   ## 操作选项

   [1] 全部应用
   [2] 选择性应用
   [3] 查看详细修改建议文档
   [4] 跳过所有修改
   ```

4. **应用修改**

   对每个要应用的修改项：
   - 使用Read工具读取原章节文件
   - 定位修改位置
   - 应用修改
   - 使用Write工具写入新文件（版本号+1）

5. **版本控制**

   - 原文件：`05_技术方案.md`
   - 修改后：`05_技术方案_v2.md`
   - 保留原文件作为备份

6. **生成修改日志**

   ```markdown
   # 修改日志 - [阶段名称]

   - **审核阶段**: [阶段]
   - **修改时间**: [时间戳]
   - **总修改数**: [数量]
   - **已应用**: [数量]

   ## 修改详情

   | 文件 | 版本 | 修改项 | 状态 |
   |------|------|--------|------|
   | 01_发明名称.md | v1→v2 | 2项 | ✅ 已应用 |
   | 02_技术领域.md | v1→v2 | 3项 | ✅ 已应用 |
   ```

7. **输出文件**

   - 修改日志: `修改日志_阶段{stage}.md`
   - 更新章节文件版本

## 版本管理

```
原始版本: [文件名].md
第一次审核后: [文件名]_v2.md
第二次审核后: [文件名]_v3.md
...
```

始终保留最新版本作为 `[文件名].md`，旧版本重命名保存。
```

**Step 2: 验证并提交**

```bash
git add .claude/agents/30-patent-modification-applier.md
git commit -m "feat: add modification applier agent"
```

---

## Task 6: 创建报告生成器

**Files:**
- Create: `.claude/agents/31-patent-report-generator.md`

**Step 1: 创建报告生成器代理**

```markdown
---
name: report-generator
description: 生成审核报告，包括阶段报告和汇总报告
---

## 参数接收

- **report_type**: 报告类型（stage/summary）
- **review_stage**: 审核阶段（仅stage类型需要）
- **review_data**: 审核数据

## 职责

你是一位报告生成专家，负责生成专业的审核报告。

## 报告类型

### 1. 阶段审核报告

生成单个审核阶段的详细报告。

**输出格式**：

```markdown
# 审核报告 - [阶段名称]

## 审核信息

- **审核阶段**: 预审1 / 中期审核1 / 中期审核2 / 最终审核
- **审核章节**: 01-发明名称, 02-所属技术领域
- **审核时间**: 2025-01-15 10:30:00
- **参与专家**: 5人全部参与

## 投票结果

| 专家 | 角色 | 投票 | 意见 |
|------|------|------|------|
| 专家A | 资深技术专家 | ✅ 同意 | 技术方案清晰可行 |
| 专家B | 技术专家 | ✅ 同意 | 无异议 |
| 专家C | 法律专家 | ✅ 同意 | 符合专利法要求 |
| 专家D | 资深专利代理人 | ✅ 同意 | 保护范围适当 |
| 专家E | 专利代理人 | ⚠️ 有保留 | 建议优化措辞 |

**投票结果**: 7/7 票同意（5票同意 + 2票有保留）
**审核结论**: ✅ 通过

## 修改建议

### 自动应用项（5项）

1. **[格式]** 修正章节编号格式
   - 已自动应用 ✓

### 需用户确认项（3项）

1. **[重要]** 建议补充技术领域的细分说明
   - 是否应用：[ ] 是 [ ] 否

## 专家评注

### 资深技术专家
> 整体技术方案清晰，创新点明确。

### 法律专家
> 符合专利法要求，无明显侵权风险。

## 下一步行动

- [ ] 确认需用户确认的修改项
- [ ] 继续执行下一阶段生成
```

### 2. 审核汇总报告

生成整个审核流程的汇总报告（最终审核后生成）。

**输出格式**：

```markdown
# 专利审核汇总报告

## 概览

- **发明名称**: [名称]
- **专利类型**: 发明专利
- **审核阶段数**: 4个阶段
- **总修改建议**: 23项
- **已应用**: 18项
- **用户拒绝**: 3项
- **待确认**: 2项

## 各阶段审核摘要

| 阶段 | 章节 | 投票结果 | 修改项 | 状态 |
|------|------|---------|--------|------|
| 预审1 | 01-02 | 7/7通过 | 5项 | ✅ 已完成 |
| 中期审核1 | 03-05 | 6/7通过 | 12项 | ✅ 已完成 |
| 中期审核2 | 06-07 | 7/7通过 | 4项 | ✅ 已完成 |
| 最终审核 | 08-09 | 7/7通过 | 2项 | ✅ 已完成 |

## 最终评价

**整体质量**: 优秀 ⭐⭐⭐⭐⭐

**技术评分**: 9/10
**法律评分**: 9/10
**专利评分**: 9/10

**建议**: 可以正式提交专利申请

## 版本历史

| 文件 | 原始 | 最终修改版 | 修改次数 |
|------|------|-----------|---------|
| 01_发明名称.md | v1 | v2 | 1次 |
| 03_背景技术.md | v1 | v3 | 2次 |
| 05_技术方案.md | v1 | v3 | 2次 |
```

## 输出文件

- 阶段报告: `审核报告_阶段{stage}.md`
- 汇总报告: `审核汇总报告.md`
- 报告数据: `.review-report-{stage}.json` / `.review-summary.json`
```

**Step 2: 验证并提交**

```bash
git add .claude/agents/31-patent-report-generator.md
git commit -m "feat: add report generator agent"
```

---

## Task 7: 更新主命令集成审核流程

**Files:**
- Modify: `commands/patent.md`

**Step 1: 在现有流程中插入审核节点**

在 `commands/patent.md` 的执行步骤部分添加审核调用：

找到 "步骤 2.1 - 2.9：调用各章节生成子代理" 部分，在适当位置插入审核调用：

```markdown
**步骤 2.1：生成章节01-02 + 预审**

```
# 生成章节 01-02
[调用 title-generator, field-analyzer]

# 预审1（审核章节01-02）
使用 Task 工具调用 review-coordinator：
- review_stage: "pre1"
- chapters: ["01", "02"]
- patent_type: {patent_type}

如果审核未通过：
- 调用 dispute-resolver 处理争议
- 等待用户决策
- 根据决策继续或重新生成
```

**步骤 2.2：生成章节03-05 + 中期审核1**

```
# 生成章节 03-05
[调用 background-researcher, problem-analyzer, solution-designer]

# 中期审核1（审核章节03-05，重要问题）
使用 Task 工具调用 review-coordinator：
- review_stage: "mid1"
- chapters: ["03", "04", "05"]
- patent_type: {patent_type}

重要问题阈值：需 6/7 票通过
```

**步骤 2.3：生成章节06-07 + 中期审核2**

```
# 生成章节 06-07
[调用 benefit-analyzer, implementation-writer]

# 中期审核2（审核章节06-07）
使用 Task 工具调用 review-coordinator：
- review_stage: "mid2"
- chapters: ["06", "07"]
- patent_type: {patent_type}
```

**步骤 2.4：生成章节08-09 + 最终审核**

```
# 生成章节 08-09
[调用 protection-extractor, reference-collector]

# 最终审核（审核所有章节 + 整体质量）
使用 Task 工具调用 review-coordinator：
- review_stage: "final"
- chapters: ["01", "02", "03", "04", "05", "06", "07", "08", "09"]
- patent_type: {patent_type}

生成审核汇总报告
```

**步骤 2.5：调用文档整合子代理**

```
所有审核通过后，调用 document-integrator：
- 输入：patent_type（专利类型）
- 输出：审核后的完整交底书
```
```

**Step 2: 添加审核相关配置**

在 `commands/patent.md` 开头添加审核配置说明：

```markdown
## 审核团队配置

本技能支持5人专家团队审核，可配置是否启用：

### 启用审核（默认）

```
# 使用完整审核流程
/patent
# 按提示选择：启用审核团队
```

### 禁用审核

```
# 快速模式，跳过审核
/patent
# 按提示选择：快速模式（无审核）
```

### 审核团队配置

| 角色 | 数量 | 权重 | 职责 |
|------|------|------|------|
| 资深技术专家 | 1 | 2票 | 技术可行性、创新性 |
| 技术专家 | 1 | 1票 | 技术细节、实施可行性 |
| 法律专家 | 1 | 1票 | 法律合规性 |
| 资深专利代理人 | 1 | 2票 | 保护范围、专利策略 |
| 专利代理人 | 1 | 1票 | 文档规范性、格式 |

**总票数**: 7票（加权）

### 投票阈值

| 问题类型 | 通过阈值 | 说明 |
|---------|---------|------|
| 重要问题 | ≥6/7票 | 技术方案错误、法律违规、保护范围问题 |
| 次要问题 | ≥5/7票 | 格式规范、措辞优化、附图改进 |
```

**Step 3: 验证修改**

Run: `cat commands/patent.md | grep -A 5 "审核"`
Expected: 看到审核相关的内容

**Step 4: 提交**

```bash
git add commands/patent.md
git commit -m "feat: integrate review process into main command"
```

---

## Task 8: 创建审核模板文件

### Task 8.1: 创建审核报告模板

**Files:**
- Create: `.claude/skills/patent-disclosure-writer/templates/review-report-template.md`

**Step 1: 创建审核报告模板**

```markdown
# 审核报告 - {{STAGE_NAME}}

## 审核信息

- **审核阶段**: {{STAGE_CN_NAME}}
- **审核章节**: {{CHAPTER_LIST}}
- **审核时间**: {{TIMESTAMP}}
- **参与专家**: 5人全部参与

## 投票结果

| 专家 | 角色 | 投票 | 意见 |
|------|------|------|------|
{{VOTE_TABLE}}

**投票结果**: {{VOTE_SUMMARY}}
**审核结论**: {{CONCLUSION}}

## 修改建议

### 自动应用项（{{AUTO_APPLY_COUNT}}项）

{{AUTO_APPLY_ITEMS}}

### 需用户确认项（{{CONFIRM_COUNT}}项）

{{CONFIRM_ITEMS}}

## 专家评注

{{EXPERT_COMMENTS}}

## 下一步行动

- [ ] 确认需用户确认的修改项
- [ ] 继续执行下一阶段生成

---

生成时间: {{GENERATION_TIME}}
```

**Step 2: 验证并提交**

```bash
git add .claude/skills/patent-disclosure-writer/templates/review-report-template.md
git commit -m "feat: add review report template"
```

### Task 8.2: 创建争议报告模板

**Files:**
- Create: `.claude/skills/patent-disclosure-writer/templates/dispute-report-template.md`

**Step 1: 创建争议报告模板**

```markdown
# 争议报告 - {{STAGE_NAME}}

## 争议概述

- **审核阶段**: {{STAGE_CN_NAME}}
- **投票结果**: {{VOTE_RESULT}}
- **争议类型**: {{DISPUTE_TYPE}}

## 多数方意见（投赞成票）

**支持专家**: {{MAJORITY_EXPERTS}}

**主要理由**:
{{MAJORITY_REASONS}}

## 少数方意见（投反对票）

**反对专家**: {{MINORITY_EXPERTS}}

**主要理由**:
{{MINORITY_REASONS}}

## 不同方案对比

| 方案 | 描述 | 优点 | 缺点 | 推荐指数 |
|------|------|------|------|---------|
{{COMPARISON_TABLE}}

## 推荐

**推荐方案**: {{RECOMMENDED方案}}

**理由**: {{RECOMMENDATION_REASON}}

## 用户决策

请选择：
- [ ] 采纳多数方意见
- [ ] 采纳少数方意见
- [ ] 采纳推荐方案
- [ ] 要求专家重新讨论
- [ ] 自行修改

---

生成时间: {{GENERATION_TIME}}
```

**Step 2: 验证并提交**

```bash
git add .claude/skills/patent-disclosure-writer/templates/dispute-report-template.md
git commit -m "feat: add dispute report template"
```

---

## Task 9: 更新技能文档

**Files:**
- Modify: `.claude/skills/patent-disclosure-writer/SKILL.md`
- Modify: `.claude/skills/patent-disclosure-writer/references/agents.md`

**Step 1: 更新 SKILL.md 添加审核功能说明**

在 "子代理列表" 章节后添加审核相关内容：

```markdown
## 审核团队系统（新增）

本技能支持可选的专家团队审核功能，提供专业的专利质量保证。

### 审核模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| **完整审核模式** | 5人专家团队，4阶段审核 | 重要专利申请 |
| **快速模式** | 跳过审核，直接生成 | 快速草稿、内部参考 |

### 审核流程

```
01-02章节 → [预审] → 03-05章节 → [中期审核1] →
06-07章节 → [中期审核2] → 08-09章节 → [最终审核] → 整合
```

### 审核代理

| 代理 | 角色 | 权重 |
|------|------|------|
| review-coordinator | 审核协调器 | - |
| expert-sr-tech | 资深技术专家 | 2票 |
| expert-tech | 技术专家 | 1票 |
| expert-legal | 法律专家 | 1票 |
| expert-sr-agent | 资深专利代理人 | 2票 |
| expert-agent | 专利代理人 | 1票 |

### 审核输出

- 阶段审核报告（4个）
- 审核汇总报告（1个）
- 修改建议清单
- 争议报告（如有）
```

**Step 2: 更新 references/agents.md**

添加审核代理的详细说明：

```markdown
## 审核代理（新增）

### 22. review-coordinator（审核协调器）

**职责**：协调整个审核流程，管理审核阶段和专家调用

**输入参数**：
- `review_stage`：审核阶段（pre1/mid1/mid2/final）
- `chapters`：待审核的章节列表
- `patent_type`：专利类型

**输出文件**：
- `.review-status-{stage}.json`：审核状态文件

---

### 23-27. 专家团队

详见各专家代理定义文件。

---

### 28. review-synthesizer（审核意见汇总器）

**职责**：汇总5位专家的评审意见，生成统一的修改建议清单

---

### 29. dispute-resolver（争议解决器）

**职责**：处理专家投票争议，生成争议报告并呈现给用户决策

---

### 30. modification-applier（修改应用器）

**职责**：根据用户确认应用修改建议到章节文件，管理版本控制

---

### 31. report-generator（报告生成器）

**职责**：生成审核报告，包括阶段报告和汇总报告
```

**Step 3: 更新版本号**

在 SKILL.md 的 frontmatter 中更新版本号：

```yaml
---
metadata:
  version: 2.0.0
  timelessness-score: 8/10
  last-updated: 2025-01-15
---
```

在版本历史中添加：

```markdown
| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 2.0.0 | 2025-01-15 | 添加5人专家团队审核系统，支持分阶段审核、投票机制、争议解决 |
| 1.1.0 | 2025-01-14 | 添加验证脚本、演进性分析 |
```

**Step 4: 提交**

```bash
git add .claude/skills/patent-disclosure-writer/SKILL.md
git add .claude/skills/patent-disclosure-writer/references/agents.md
git commit -m "docs: update skill documentation for review system"
```

---

## Task 10: 创建审核状态管理脚本

**Files:**
- Create: `.claude/skills/patent-disclosure-writer/scripts/review_state_manager.py`

**Step 1: 创建审核状态管理脚本**

```python
#!/usr/bin/env python3
"""
审核状态管理脚本

管理专利审核流程的状态，包括审核进度、投票结果、修改建议等。
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List

@dataclass
class ReviewState:
    """审核状态数据类"""
    version: str = "2.0.0"
    stage: str = ""
    chapters: List[str] = None
    status: str = "pending"  # pending, in_progress, completed, disputed
    vote_result: Optional[Dict] = None
    modifications: List[Dict] = None
    timestamp: str = ""

    def __post_init__(self):
        if self.chapters is None:
            self.chapters = []
        if self.modifications is None:
            self.modifications = []

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
```

**Step 2: 添加执行权限（Linux/Mac）**

```bash
chmod +x .claude/skills/patent-disclosure-writer/scripts/review_state_manager.py
```

**Step 3: 验证脚本**

```bash
python .claude/skills/patent-disclosure-writer/scripts/review_state_manager.py --help
```

Expected: 显示帮助信息

**Step 4: 提交**

```bash
git add .claude/skills/patent-disclosure-writer/scripts/review_state_manager.py
git commit -m "feat: add review state manager script"
```

---

## Task 11: 创建测试验证

### Task 11.1: 创建审核流程测试

**Files:**
- Create: `tests/test_review_system.py`

**Step 1: 创建测试文件**

```python
"""
测试审核团队系统
"""

import pytest
import json
from pathlib import Path


class TestReviewCoordinator:
    """测试审核协调器"""

    def test_coordinator_initializes_status(self):
        """测试协调器初始化状态"""
        from scripts.review_state_manager import init_status, read_status

        state = init_status("pre1", ["01", "02"])

        assert state.stage == "pre1"
        assert state.chapters == ["01", "02"]
        assert state.status == "pending"

        # 清理
        Path(".review-status-pre1.json").unlink()

    def test_coordinator_reads_status(self):
        """测试协调器读取状态"""
        from scripts.review_state_manager import init_status, read_status

        init_status("pre1", ["01", "02"])
        state = read_status("pre1")

        assert state is not None
        assert state.stage == "pre1"

        # 清理
        Path(".review-status-pre1.json").unlink()


class TestExpertAgents:
    """测试专家代理"""

    def test_expert_opinion_format(self):
        """测试专家意见格式"""
        opinion = {
            "expert": "expert-sr-tech",
            "role": "资深技术专家",
            "vote": "approve",
            "vote_weight": 2,
            "opinion": "技术方案清晰可行",
            "modifications": [],
            "critical_issues": [],
            "score": {
                "feasibility": 9,
                "innovation": 8,
                "overall": 8.5
            }
        }

        assert opinion["vote_weight"] == 2
        assert opinion["vote"] in ["approve", "approve_with_reservations", "reject", "abstain"]
        assert "score" in opinion


class TestVotingMechanism:
    """测试投票机制"""

    def test_weighted_voting_calculation(self):
        """测试加权投票计算"""
        votes = {
            "expert-sr-tech": "approve",      # 2票
            "expert-tech": "approve",          # 1票
            "expert-legal": "approve",         # 1票
            "expert-sr-agent": "approve",      # 2票
            "expert-agent": "approve",         # 1票
        }

        vote_weights = {
            "expert-sr-tech": 2,
            "expert-tech": 1,
            "expert-legal": 1,
            "expert-sr-agent": 2,
            "expert-agent": 1,
        }

        total = 0
        for expert, vote in votes.items():
            if vote == "approve":
                total += vote_weights[expert]

        assert total == 7  # 全部赞成 = 7票

    def test_majority_threshold(self):
        """测试多数阈值"""
        # 重要问题需 6/7 票
        assert 6 >= 6

        # 次要问题需 5/7 票
        assert 5 >= 5


class TestModificationApplier:
    """测试修改应用器"""

    def test_version_control(self):
        """测试版本控制"""
        # 原文件
        original = "test_chapter.md"

        # 第一次修改
        v1 = "test_chapter.md"
        v2 = "test_chapter_v2.md"

        assert v2.endswith("_v2.md")

    def test_auto_apply_detection(self):
        """测试自动应用检测"""
        modification = {
            "type": "error_correction",
            "auto_apply": True
        }

        assert modification["auto_apply"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Step 2: 运行测试**

```bash
pytest tests/test_review_system.py -v
```

**Step 3: 提交**

```bash
git add tests/test_review_system.py
git commit -m "test: add review system tests"
```

---

## Task 12: 更新 README 文档

**Files:**
- Modify: `README.md`

**Step 1: 添加审核系统说明**

在 "功能特性" 章节后添加：

```markdown
### 新增功能 (v2.0.0)

- **👥 5人专家团队审核系统**
  - 资深技术专家、技术专家、法律专家、资深专利代理人、专利代理人
  - 4阶段审核流程（预审、中期审核×2、最终审核）
  - 加权投票机制（7票制）
  - 争议解决和用户决策
- **📊 智能修改建议**
  - 自动应用明显错误
  - 用户确认重大改动
  - 版本控制和修改日志
- **📝 专业审核报告**
  - 阶段审核报告
  - 审核汇总报告
  - 争议报告
```

在 "子代理架构" 表格后添加：

```markdown
### 审核代理架构（v2.0.0 新增）

| 序号 | 审核代理 | 角色 | 权重 |
|------|---------|------|------|
| 22 | review-coordinator | 审核协调器 | - |
| 23 | expert-sr-tech | 资深技术专家 | 2票 |
| 24 | expert-tech | 技术专家 | 1票 |
| 25 | expert-legal | 法律专家 | 1票 |
| 26 | expert-sr-agent | 资深专利代理人 | 2票 |
| 27 | expert-agent | 专利代理人 | 1票 |
| 28 | review-synthesizer | 审核意见汇总器 | - |
| 29 | dispute-resolver | 争议解决器 | - |
| 30 | modification-applier | 修改应用器 | - |
| 31 | report-generator | 报告生成器 | - |
```

在版本历史中添加：

```markdown
| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 2.0.0 | 2025-01-15 | 添加5人专家团队审核系统，支持分阶段审核、投票机制、争议解决 |
| 1.1.0 | 2025-01-14 | 添加验证脚本、状态管理、演进性分析 |
```

**Step 2: 提交**

```bash
git add README.md
git commit -m "docs: update README for review system v2.0.0"
```

---

## Task 13: 最终验证和文档

**Step 1: 验证所有文件创建**

```bash
# 验证代理文件
ls -la .claude/agents/22-*.md
ls -la .claude/agents/23-*.md
ls -la .claude/agents/24-*.md
ls -la .claude/agents/25-*.md
ls -la .claude/agents/26-*.md
ls -la .claude/agents/27-*.md
ls -la .claude/agents/28-*.md
ls -la .claude/agents/29-*.md
ls -la .claude/agents/30-*.md
ls -la .claude/agents/31-*.md

# 验证模板文件
ls -la .claude/skills/patent-disclosure-writer/templates/review-*template.md

# 验证脚本
ls -la .claude/skills/patent-disclosure-writer/scripts/review_*.py

# 验证测试
ls -la tests/test_review_system.py
```

Expected: 所有文件都存在

**Step 2: 运行测试套件**

```bash
pytest tests/test_review_system.py -v
```

Expected: 所有测试通过

**Step 3: 创建快速开始指南**

**Files:**
- Create: `docs/review-system-quickstart.md`

```markdown
# 专利审核团队系统 - 快速开始指南

## 概述

专利审核团队系统为专利交底书生成提供专业的质量保证，通过5人专家团队进行多阶段审核。

## 使用方式

### 1. 启用审核（推荐）

```bash
/patent
```

按提示选择"启用审核团队"。

### 2. 快速模式（无审核）

```bash
/patent
```

按提示选择"快速模式"。

## 审核流程

```
┌─────────────┐
│ 01-02章节   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  预审1      │ ← 5位专家审核
└──────┬──────┘
       │ 通过
       ▼
┌─────────────┐
│ 03-05章节   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 中期审核1   │ ← 重要问题需6/7票
└──────┬──────┘
       │
       ▼
    ...继续...
```

## 专家团队

| 角色 | 权重 | 职责 |
|------|------|------|
| 资深技术专家 | 2票 | 技术可行性、创新性 |
| 技术专家 | 1票 | 技术细节、实施可行性 |
| 法律专家 | 1票 | 法律合规性 |
| 资深专利代理人 | 2票 | 保护范围、专利策略 |
| 专利代理人 | 1票 | 文档规范性、格式 |

**总票数**: 7票（加权）

## 投票规则

| 问题类型 | 通过阈值 |
|---------|---------|
| 重要问题 | ≥6/7票 |
| 次要问题 | ≥5/7票 |

## 输出文件

审核完成后生成：

- `审核报告_预审1.md`
- `审核报告_中期审核1.md`
- `审核报告_中期审核2.md`
- `审核报告_最终审核.md`
- `审核汇总报告.md`
- `修改日志_阶段*.md`

## 争议处理

如果专家意见分歧：

1. 系统生成争议报告
2. 展示多数方和少数方意见
3. 提供方案对比
4. 等待用户决策
5. 根据用户选择继续

## 修改应用

- **自动应用**: 明显错误（格式错误、编号错误等）
- **需确认**: 重大改动（保护范围调整、技术方案修改等）

## 示例

### 完整审核流程

```bash
$ /patent

请选择模式:
[1] 完整审核模式（推荐）
[2] 快速模式（无审核）

选择: 1

请输入创新想法: 一种基于大语言模型的智能对话方法...

[生成01-02章节...]
[调用5位专家审核...]
投票结果: 7/7票通过
[应用修改建议...]

[生成03-05章节...]
[调用5位专家审核...]
投票结果: 6/7票通过
[应用修改建议...]

...
[生成最终审核报告...]
✅ 审核完成

输出文件:
- 审核汇总报告.md
- 专利申请技术交底书_[名称].md
```

## 管理审核状态

```bash
# 查看审核状态
python .claude/skills/patent-disclosure-writer/scripts/review_state_manager.py --status pre1

# 初始化审核状态
python .claude/skills/patent-disclosure-writer/scripts/review_state_manager.py --init pre1 --chapters "01,02"

# 更新审核状态
python .claude/skills/patent-disclosure-writer/scripts/review_state_manager.py --update pre1 --set status completed
```

## 故障排查

### 审核失败

检查审核状态文件：
```bash
python .claude/skills/patent-disclosure-writer/scripts/review_state_manager.py --status [stage]
```

### 修改未应用

检查修改日志：
```bash
cat 修改日志_阶段*.md
```

### 专家意见冲突

查看争议报告：
```bash
cat 争议报告_阶段*.md
```
```

**Step 4: 提交所有文件**

```bash
git add docs/review-system-quickstart.md
git commit -m "docs: add review system quickstart guide"
```

---

## 总结

### 完成的工作

1. ✅ 创建了10个新的审核代理（22-31）
2. ✅ 集成审核流程到主命令
3. ✅ 创建审核报告模板
4. ✅ 创建审核状态管理脚本
5. ✅ 创建测试验证
6. ✅ 更新所有相关文档
7. ✅ 创建快速开始指南

### 文件清单

**新增代理（10个）**:
- `.claude/agents/22-patent-review-coordinator.md`
- `.claude/agents/23-patent-expert-sr-tech.md`
- `.claude/agents/24-patent-expert-tech.md`
- `.claude/agents/25-patent-expert-legal.md`
- `.claude/agents/26-patent-expert-sr-agent.md`
- `.claude/agents/27-patent-expert-agent.md`
- `.claude/agents/28-patent-review-synthesizer.md`
- `.claude/agents/29-patent-dispute-resolver.md`
- `.claude/agents/30-patent-modification-applier.md`
- `.claude/agents/31-patent-report-generator.md`

**修改文件**:
- `commands/patent.md`
- `.claude/skills/patent-disclosure-writer/SKILL.md`
- `.claude/skills/patent-disclosure-writer/references/agents.md`
- `README.md`

**新增模板**:
- `.claude/skills/patent-disclosure-writer/templates/review-report-template.md`
- `.claude/skills/patent-disclosure-writer/templates/dispute-report-template.md`

**新增脚本**:
- `.claude/skills/patent-disclosure-writer/scripts/review_state_manager.py`

**新增测试**:
- `tests/test_review_system.py`

**新增文档**:
- `docs/review-system-quickstart.md`
- `docs/plans/2025-01-15-patent-review-team-system.md`

### 下一步

计划已保存到 `docs/plans/2025-01-15-patent-review-team-system.md`

**执行选项**:

**1. 子代理驱动（本次会话）** - 我为每个任务分派新的子代理，任务间进行审查，快速迭代

**2. 并行会话（独立）** - 在新会话中使用 executing-plans，批量执行并设置检查点

你想选择哪种方式？
